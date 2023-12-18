import os
import threading

import httpx
from flask import request
from openai import OpenAI, RateLimitError, APITimeoutError, InternalServerError
from app.helpers.constants import ContractStatus, ContractMailStatus, ValidationMessages, DEFAULT_SECTION_DICT, \
    DEFAULT_SECTIONS
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import UserType
from app.helpers.utility import field_type_validator
from app.helpers.utility import get_pagination_meta
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.models.client import Client
from app.models.contract import Contract
from app.models.contract_log import ContractLog
from app.models.user import User
from app.models.contract_signee import ContractSignee
from app.views.base_view import BaseView
from app.models.account import Account
from app.models.signee import Signee
from workers.email_worker import EmailWorker
from app.helpers.constants import EmailTypes
from app.helpers.utility import generate_email_token
from app import config_data
from app import logger
import jwt
from app.models.folder import Folder
from typing import Union
from app.models.email_template import EmailTemplate
from datetime import datetime
import pdfkit

from workers.s3_worker import upload_file_and_get_object_details, get_presigned_url


class ContractView(BaseView):
    sections = []
    sections_dict = {}

    @classmethod
    def create_update(cls):
        """Create & Update Contract"""
        user_obj = ContractView.get_logged_in_user(request=request)
        account_uuid = user_obj.account_uuid
        data = request.get_json(force=True)
        field_types = {'contract_uuid': str, 'purpose': str, 'client_uuid': str, 'folder_uuid': str, 'signees': list,
                       'brief': str, 'content': str, 'service_name': str, 'duration': int, 'amount': float,
                       'currency_code': str, 'duration_type': str, 'payment_frequency': str}

        required_fields = ['purpose', 'client_uuid',
                           'folder_uuid', 'signees', 'brief', 'content']
        post_data = field_type_validator(
            request_data=data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        signee_uuids = data.get('signees')
        if not signee_uuids:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=ValidationMessages.SIGNEES_REQUIRED.name.lower())

        folder_obj = Folder.get_by_uuid(data.get('folder_uuid'))
        if not folder_obj:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.FOLDER_NOT_FOUND.value, data=None,
                                      error=None)
        duration = data.get('duration')
        duration_type = data.get('duration_type')
        if any([duration, duration_type]) and not all([duration, duration_type]):
            duration = None
            duration_type = None

        amount = data.get('amount')
        currency_code = data.get('currency_code')
        payment_frequency = data.get('payment_frequency')
        if any([amount, currency_code, payment_frequency]) and not all([amount, currency_code, payment_frequency]):
            amount = None
            currency_code = None
            payment_frequency = None

        contract_uuid = data.get('contract_uuid', None)
        if contract_uuid:
            contract_obj = Contract.get_by_uuid(uuid=contract_uuid)
            if contract_obj is None:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.CONTRACT_NOT_FOUND.value, data=None,
                                          error=None)

            contract_obj.brief = data.get('brief')
            contract_obj.folder_uuid = data.get('folder_uuid')
            contract_obj.client_uuid = data.get('client_uuid')
            contract_obj.service_name = data.get('service_name')
            contract_obj.duration = duration
            contract_obj.duration_type = duration_type
            contract_obj.amount = amount
            contract_obj.currency_code = currency_code
            contract_obj.payment_frequency = payment_frequency
            contract_obj.content = data.get('content')
            contract_obj.signed_content = data.get('content')

            Contract.update()

            signees = data.get('signees')
            db_signees = ContractSignee.get_by_account_client_and_contract(account_uuid=account_uuid,
                                                                           client_uuid=data.get(
                                                                               'client_uuid'),
                                                                           contract_uuid=contract_uuid)
            result = set(signees) == {obj.uuid for obj in db_signees}

            if not result:
                ContractSignee.delete_by_contract(
                    account_uuid=account_uuid, contract_uuid=contract_uuid, client_uuid=data.get('client_uuid'))

                ContractView.add_new_signees_to_contract(account_uuid=account_uuid, signees=signees,
                                                         contract_uuid=contract_uuid,
                                                         client_uuid=data.get(
                                                             'client_uuid'),
                                                         is_account_signee=False)

            contract_log_data = {
                'uuid': ContractLog.create_uuid(),
                'account_uuid': contract_obj.account_uuid,
                'contract_uuid': contract_uuid,
                'description': '{} {} updated this document.'.format(user_obj.first_name, user_obj.last_name)
            }
            ContractLog.add(contract_log_data)
            data = {'contract_uuid': contract_uuid}
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.CONTRACT_DATA_UPDATED_SUCCESSFULLY.value,
                                      data=data, error=None)

        contract_data = {
            'uuid': Contract.create_uuid(),
            'account_uuid': user_obj.account_uuid,
            'created_by': user_obj.uuid,
            'purpose': data.get('purpose'),
            'client_uuid': data.get('client_uuid'),
            'template_uuid': None,
            'folder_uuid': data.get('folder_uuid'),
            'brief': data.get('brief'),
            'content': data.get('content'),
            'signed_content': data.get('content'),
            'service_name': data.get('service_name'),
            'duration': duration,
            'duration_type': duration_type,
            'amount': amount,
            'currency_code': currency_code,
            'payment_frequency': payment_frequency,
            'status': ContractStatus.DRAFT.value
        }
        contract_obj = Contract.add(contract_data)
        contract_uuid = contract_obj.uuid

        if contract_obj is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

        contract_log_data = {
            'uuid': ContractLog.create_uuid(),
            'account_uuid': contract_obj.account_uuid,
            'contract_uuid': contract_uuid,
            'description': '{} {} created this document.'.format(user_obj.first_name, user_obj.last_name)
        }
        ContractLog.add(contract_log_data)

        # add selected signees
        signees = data.get('signees')
        ContractView.add_new_signees_to_contract(account_uuid=account_uuid, signees=signees,
                                                 contract_uuid=contract_uuid, client_uuid=data.get(
                                                     'client_uuid'),
                                                 is_account_signee=False)
        # add account level signees
        account_client_obj = Client.get_default_account_client(
            account_uuid=account_uuid)
        if account_client_obj:
            account_signees = Signee.get_all_by_client_uuid(
                account_uuid=account_uuid, client_uuid=account_client_obj.uuid)
            account_signees = [obj.uuid for obj in account_signees]
            ContractView.add_new_signees_to_contract(account_uuid=account_uuid, signees=account_signees,
                                                     contract_uuid=contract_uuid, client_uuid=account_client_obj.uuid,
                                                     is_account_signee=True)

        data = {'contract_uuid': contract_uuid}
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.CONTRACT_CREATED_SUCCESSFULLY.value, data=data,
                                  error=None)

    @staticmethod
    def add_new_signees_to_contract(account_uuid: str, signees: list, contract_uuid: str, client_uuid: str,
                                    is_account_signee: bool):
        for signee in signees:
            signee_detail = Signee.get_by_uuid(signee)
            contract_signee_data = {
                'uuid': ContractSignee.create_uuid(),
                'account_uuid': account_uuid,
                'contract_uuid': contract_uuid,
                'client_uuid': client_uuid,
                'signee_uuid': signee,
                'signee_email': signee_detail.email,
                'signee_full_name': signee_detail.full_name,
                'status': ContractMailStatus.NOT_SENT.value,
                'signee_priority': signee_detail.signing_sequence,
                'is_account_signee': is_account_signee
            }
            ContractSignee.add(contract_signee_data)

    @classmethod
    def list(cls, folder_uuid: Union[str, None] = None):
        """Return list of contract according to given page, size, sort and q(filter query)."""
        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        user_obj = cls.get_logged_in_user(request=request)
        account_uuid = user_obj.account_uuid

        if folder_uuid:
            contract_objs, objects_count = Contract.get_contracts_list(account_uuid=account_uuid, folder_uuid=folder_uuid,
                                                                       q=q, sort=sort, page=page, size=size)

        else:
            contract_objs, objects_count = Contract.get_contracts_list(
                account_uuid=account_uuid, q=q, sort=sort, page=page, size=size)

        contract_list = Contract.serialize(contract_objs)

        data = {'result': contract_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=int(size), total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_by_uuid(cls, contract_uuid: str):
        """Get Contract by given uuid"""
        contract_obj = Contract.get_by_uuid(contract_uuid)
        if contract_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.CONTRACT_NOT_FOUND.value, data=None,
                                      error=None)
        contract_data = Contract.serialize(contract_obj)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=contract_data,
                                  error=None)

    @classmethod
    def view_contract(cls, contract_uuid: str):
        contract_obj = Contract.get_by_uuid(contract_uuid)
        if contract_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.CONTRACT_NOT_FOUND.value, data=None,
                                      error=None)
        contract_data = Contract.serialize(contract_obj)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=contract_data,
                                  error=None)

    @classmethod
    def download_as_pdf(cls, contract_uuid: str):
        contract_obj = Contract.get_by_uuid(contract_uuid)
        if contract_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.CONTRACT_NOT_FOUND.value, data=None,
                                      error=None)
        account_uuid = contract_obj.account_uuid
        contract_signed_content = contract_obj.signed_content

        file_name = 'contract_{}.pdf'.format(contract_uuid)
        pdf_local_path = os.path.join(config_data['UPLOAD_FOLDER'], file_name)  # type: ignore  # noqa: FKA100

        try:
            pdfkit.from_string(contract_signed_content, pdf_local_path)  # type: ignore  # noqa: FKA100
            s3_folder_path = f'media/{account_uuid}/contracts/'.lower()
            s3_file_path = upload_file_and_get_object_details(file_path=pdf_local_path,
                                                              file_name=file_name,
                                                              s3_folder_path=s3_folder_path)

            s3_bucket_link = get_presigned_url(path=s3_file_path)
        except Exception as e:
            logger.error(e)
            os.remove(pdf_local_path)
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.DOWNLOAD_AS_PDF_SUCCESSFUL.value,
                                  data={'pdf_file': s3_bucket_link}, error=None)

    @classmethod
    def send(cls):
        """Update Contract status"""
        user_obj = ContractView.get_logged_in_user(request=request)
        account_uuid = user_obj.account_uuid
        data = request.get_json(force=True)
        field_types = {'contract_uuid': str}
        required_fields = ['contract_uuid']

        post_data = field_type_validator(
            request_data=data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        contract_uuid = data.get('contract_uuid')
        contract_obj = Contract.get_by_uuid(contract_uuid)
        if contract_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.CONTRACT_NOT_FOUND.value, data=None,
                                      error=None)

        account_owner = User.get_primary_user_of_account(account_uuid)

        client_uuid = contract_obj.client_uuid
        client_obj = Client.get_by_uuid(client_uuid)
        priority_required = client_obj.priority_required

        email_template_obj = EmailTemplate.get_email_template_by_email_type(
            account_uuid=account_uuid, email_type=EmailTypes.SEND_CONTRACT_TO_SIGNEE.value)
        email_template_subject = email_template_obj.email_subject

        recipients_list = []
        # get account level signees
        account_client_obj = Client.get_default_account_client(
            account_uuid=account_uuid)
        if account_client_obj:
            account_signees = ContractSignee.get_by_account_client_and_contract(account_uuid=account_uuid,
                                                                                client_uuid=account_client_obj.uuid,
                                                                                contract_uuid=contract_uuid)

            for signee in account_signees:
                if signee.status == ContractMailStatus.SIGNED.value:
                    continue
                temp = {'uuid': signee.uuid, 'full_name': signee.signee_full_name,
                        'email': signee.signee_email}
                recipients_list.append(temp)
                signee.status = ContractMailStatus.PENDING.value
                ContractSignee.update()

        if not priority_required:
            contract_signees = ContractSignee.get_by_account_client_and_contract(account_uuid=account_uuid,
                                                                                 client_uuid=client_uuid,
                                                                                 contract_uuid=contract_uuid)

            for signee in contract_signees:
                if signee.status == ContractMailStatus.SIGNED.value:
                    continue
                temp = {'uuid': signee.uuid, 'full_name': signee.signee_full_name,
                        'email': signee.signee_email}
                recipients_list.append(temp)
                signee.status = ContractMailStatus.PENDING.value
                ContractSignee.update()
        else:
            signee = ContractSignee.get_highest_priority_signee(account_uuid=account_uuid,
                                                                contract_uuid=contract_uuid)
            if signee is not None and signee.status != ContractMailStatus.SIGNED.value:
                temp = {'uuid': signee.uuid, 'full_name': signee.signee_full_name,
                        'email': signee.signee_email}
                recipients_list.append(temp)
                signee.status = ContractMailStatus.PENDING.value
                ContractSignee.update()

        app_url = config_data.get('APP_URL')
        for recipient in recipients_list:
            recipient_uuid = recipient.get('uuid')
            recipient_full_name = recipient.get('full_name')
            recipient_email = recipient.get('email')

            contract_token = generate_email_token(recipient_uuid)
            contract_link = app_url + '/contract/sign-contract?token=' + contract_token

            email_template_body = email_template_obj.email_body
            email_template_body = email_template_body.format(
                signee_name=recipient_full_name, contract_link=contract_link,
                contact_information=account_owner.email)

            email_data = {
                'email_to': recipient_email,
                'subject': email_template_subject,
                'template': 'emails/send_contract_to_signee.html',
                'email_type': EmailTypes.SEND_CONTRACT_TO_SIGNEE.value,
                'email_data': {
                    'email_body': email_template_body
                }
            }

            EmailWorker.send(email_data)

        if recipients_list:
            contract_obj.status = ContractStatus.SENT_FOR_SIGNING.value
            Contract.update()

        contract_log_data = {
            'uuid': ContractLog.create_uuid(),
            'account_uuid': contract_obj.account_uuid,
            'contract_uuid': contract_uuid,
            'description': '{} {} shared this document.'.format(user_obj.first_name, user_obj.last_name)
        }
        ContractLog.add(contract_log_data)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.CONTRACT_IS_SENT.value, data=None,
                                  error=None)

    @classmethod
    def cancel(cls):
        """Cancel Contract by ACCOUNT ADMIN"""
        user_obj = cls.get_logged_in_user(request=request)
        account_uuid = user_obj.account_uuid

        data = request.get_json(force=True)
        field_types = {'contract_uuid': str}
        required_fields = ['contract_uuid']

        post_data = field_type_validator(
            request_data=data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        contract_uuid = data.get('contract_uuid')
        contract_obj = Contract.get_by_uuid(contract_uuid)
        if contract_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.CONTRACT_NOT_FOUND.value, data=None,
                                      error=None)

        if contract_obj.account_uuid != user_obj.account_uuid and user_obj.user_type != UserType.PRIMARY_USER.value:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.NOT_ALLOWED.value, data=None,
                                      error=None)
        old_contract_status = contract_obj.status
        contract_obj.status = ContractStatus.CANCELLED.value
        Contract.update()

        contract_created_by = User.get_by_uuid(contract_obj.created_by)

        email_template_obj = EmailTemplate.get_email_template_by_email_type(
            account_uuid=account_uuid, email_type=EmailTypes.CONTRACT_CANCELLED.value)
        email_template_body = email_template_obj.email_body
        email_template_subject = email_template_obj.email_subject

        recipients_list = []
        if old_contract_status == ContractStatus.DRAFT.value:
            temp = {
                'full_name': contract_created_by.first_name + ' ' + contract_created_by.last_name,
                'email': contract_created_by.email
            }
            recipients_list.append(temp)
        else:
            contract_signees = ContractSignee.get_by_account_contact_and_status(account_uuid=account_uuid,
                                                                                contract_uuid=contract_uuid,
                                                                                status_list=[ContractMailStatus.PENDING.value,
                                                                                             ContractMailStatus.SIGNED.value])
            for signee_obj in contract_signees:
                temp = {
                    'full_name': signee_obj.signee_full_name,
                    'email': signee_obj.signee_email
                }
                recipients_list.append(temp)

        for recipient in recipients_list:
            email = recipient.get('email')
            full_name = recipient.get('full_name')
            email_data = {
                'email_to': email,
                'subject': email_template_subject,
                'template': 'emails/contract_cancelled.html',
                'email_type': EmailTypes.CONTRACT_CANCELLED.value,
                'email_data': {
                    'email_body': email_template_body.format(name=full_name)
                }
            }

            EmailWorker.send(email_data)

        contract_log_data = {
            'uuid': ContractLog.create_uuid(),
            'account_uuid': contract_obj.account_uuid,
            'contract_uuid': contract_uuid,
            'description': '{} {} cancelled this document.'.format(user_obj.first_name, user_obj.last_name)
        }
        ContractLog.add(contract_log_data)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.CONTRACT_IS_CANCELLED.value, data=None,
                                  error=None)

    @classmethod
    def get_ai_response(cls, client, prompt, section):
        """Get Contract section using Open AI API call"""
        try:
            response = client.chat.completions.create(
                messages=[
                    {'role': 'system', 'content': 'You are a legal advisor.'},
                    {'role': 'user', 'content': prompt.format(section)}
                ],
                model=config_data.get('GPT_MODEL_4'),
            )
            section_details = response.choices[0].message.content.strip()
            cls.sections_dict[section] = section_details.replace('\n', '<br>')

        except RateLimitError as rate_err:
            logger.error('rate_err : {}'.format(rate_err))
            cls.sections = DEFAULT_SECTIONS
            cls.sections_dict = DEFAULT_SECTION_DICT

        except APITimeoutError as timeout_err:
            logger.error('timeout_err : {}'.format(timeout_err))
            cls.sections = DEFAULT_SECTIONS
            cls.sections_dict = DEFAULT_SECTION_DICT

        except InternalServerError as internal_err:
            logger.error('internal_err : {}'.format(internal_err))
            cls.sections = DEFAULT_SECTIONS
            cls.sections_dict = DEFAULT_SECTION_DICT

        except Exception as e:
            logger.error(e)
            cls.sections = DEFAULT_SECTIONS
            cls.sections_dict = DEFAULT_SECTION_DICT

    @classmethod
    def get_ai_generated_template(cls):   # type: ignore  # noqa: C901
        """Return AI generated Sample contract template in html"""
        data = request.get_json(force=True)

        field_types = {'contract_uuid': str, 'purpose': str, 'client_uuid': str, 'signees': list, 'brief': str,
                       'service_name': str, 'duration': int, 'duration_type': str, 'currency_code': str,
                       'amount': float, 'payment_frequency': str}
        required_fields = ['purpose', 'client_uuid', 'signees',
                           'brief']

        post_data = field_type_validator(
            request_data=data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        purpose = data.get('purpose')

        client = OpenAI(
            api_key=config_data.get('OPEN_AI_KEY'),
            timeout=httpx.Timeout(
                600.0, read=300.0, write=300.0, connect=300.0),
        )

        do_generation_process = True
        try:
            response = client.chat.completions.create(
                messages=[
                    {'role': 'system', 'content': 'You are a legal advisor.'},
                    {'role': 'user', 'content': f'Give me MUST 7 Section Headings of {purpose} except signature section in a comma separated format. Your language must be British English.'}
                ],
                model=config_data.get('GPT_MODEL_4'),
            )
            section_string = response.choices[0].message.content.strip()
            sections = section_string.split(',')
            cls.sections = [section.strip() for section in sections]

        except RateLimitError as rate_err:
            logger.error('rate_err : {}'.format(rate_err))
            cls.sections = DEFAULT_SECTIONS
            cls.sections_dict = DEFAULT_SECTION_DICT
            do_generation_process = False

        except APITimeoutError as timeout_err:
            logger.error('timeout_err : {}'.format(timeout_err))
            cls.sections = DEFAULT_SECTIONS
            cls.sections_dict = DEFAULT_SECTION_DICT
            do_generation_process = False

        except InternalServerError as internal_err:
            logger.error('internal_err : {}'.format(internal_err))
            cls.sections = DEFAULT_SECTIONS
            cls.sections_dict = DEFAULT_SECTION_DICT
            do_generation_process = False

        except Exception as e:
            logger.error(e)
            cls.sections = DEFAULT_SECTIONS
            cls.sections_dict = DEFAULT_SECTION_DICT
            do_generation_process = False

        if do_generation_process:
            brief = data.get('brief')

            client_uuid = data.get('client_uuid')
            client_obj = Client.get_by_uuid(uuid=client_uuid)
            client_country = client_obj.country
            client_legal_name = client_obj.legal_name

            duration = data.get('duration')
            duration_type = data.get('duration_type')
            if any([duration, duration_type]) and not all([duration, duration_type]):
                duration = None
                duration_type = None

            amount = data.get('amount')
            currency_code = data.get('currency_code')
            payment_frequency = data.get('payment_frequency')
            if any([amount, currency_code, payment_frequency]) and not all([amount, currency_code, payment_frequency]):
                amount = None
                currency_code = None
                payment_frequency = None

            duration_text = ''
            amount_text = ''
            country_text = ''
            if duration:
                duration_text = f'Duration: {duration} {duration_type}(s). '
            if amount:
                amount_text = f'Amount: {amount} {currency_code} {payment_frequency}.'
            if client_country:
                country_text = f' according to jurisdiction of {client_country} '

            prompt = ('Give me {} section of ' + purpose + country_text + 'without Section Heading. Your language must be British English.'
                      + '\n Client is ' + client_legal_name
                      + '\n Brief is ' + brief + '. ' + duration_text + ' ' + amount_text
                      + '\n Output should be in text format without special characters.')
            try:
                threads = []

                for section in cls.sections:
                    thread = threading.Thread(
                        target=cls.get_ai_response, args=(client, prompt, section))
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()

            except Exception as e:
                cls.sections = DEFAULT_SECTIONS
                cls.sections_dict = DEFAULT_SECTION_DICT
                logger.error(e)

        data = {
            'contract_data': data,
            'content': cls.sections_dict,
            'sections': cls.sections,
            'contract_currency_code': data.get('currency_code'),
            'updated_amount': data.get('amount')
        }

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value,
                                  data=data,
                                  error=None)

    @classmethod
    def get_dashboard_details(cls, account_uuid: str):
        """Get dashboard contract details by account uuid"""
        account = Account.get_by_uuid(account_uuid)
        if account is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                      error=None)

        start_date_param = request.args.get('start_date')
        end_date_param = request.args.get('end_date')

        # Initialize the timestamps with None
        start_timestamp = None
        end_timestamp = None

        # Check if start_date_param is not None and is a valid integer
        if start_date_param:
            start_timestamp = int(start_date_param)

        # Check if end_date_param is not None and is a valid integer
        if end_date_param:
            end_timestamp = int(end_date_param)

        contracts = Contract.get_contracts_status_details(
            account_uuid=account_uuid, start_timestamp=start_timestamp, end_timestamp=end_timestamp)

        dashboard_data_obj = {
            status.value: {'count': 0, 'amount': 0} for status in ContractStatus
        }

        for count, amount, status in contracts:
            if status in dashboard_data_obj:
                dashboard_data_obj[status]['count'] = count
                dashboard_data_obj[status]['amount'] = amount

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=dashboard_data_obj,
                                  error=None)

    @classmethod
    def verify_contract_token(cls):
        """ Authenticate_contract_token """
        data = request.get_json(force=True)
        field_types = {'token': str}
        required_fields = ['token']

        post_data = field_type_validator(
            request_data=data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        token = data.get('token').strip()
        try:
            # decoding the payload to fetch the stored details
            token_data = jwt.decode(jwt=token, key=config_data.get(
                'SECRET_KEY'), algorithms=['HS256'])
            contract_signee_uuid = token_data['id']
            contract_signee_obj = ContractSignee.get_by_uuid(
                uuid=contract_signee_uuid)
            if contract_signee_obj is None:
                return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                          message_key=ResponseMessageKeys.CONTRACT_SIGNEE_NOT_FOUND.value, data=None,
                                          error=None)

            contract_obj = Contract.get_by_uuid(
                uuid=contract_signee_obj.contract_uuid)
            if contract_obj is None:
                return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                          message_key=ResponseMessageKeys.CONTRACT_NOT_FOUND.value, data=None,
                                          error=None)

            if contract_obj.status in [ContractStatus.SENT_FOR_SIGNING.value, ContractStatus.SIGNED.value]:
                contract_signee_data = {
                    'contract_content': contract_obj.signed_content,
                    'signee_name': contract_signee_obj.signee_full_name,
                    'contract_signee_uuid': contract_signee_uuid,
                    'signee_sign_status': contract_signee_obj.status
                }
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.CONTRACT_TOKEN_VERIFIED_SUCCESSFULLY.value,
                                          data=contract_signee_data,
                                          error=None)
            else:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.FAILED.value, data=None,
                                          error=None)

        except Exception as e:
            logger.info('we got exception{}'.format(e))
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_TOKEN.value, data=None,
                                      error=None)

    @classmethod
    def get_ai_popup_response(cls):
        """Return AI Popup Response"""
        data = request.get_json(force=True)
        field_types = {'query': str}
        required_fields = ['query']

        post_data = field_type_validator(
            request_data=data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        question = data.get('query')
        try:
            client = OpenAI(
                api_key=config_data.get('OPEN_AI_KEY'),
                timeout=httpx.Timeout(
                    600.0, read=300.0, write=300.0, connect=300.0),
            )
            completion = client.chat.completions.create(
                messages=[
                    {
                        'role': 'user',
                        'content': question,
                    }
                ],
                model=config_data.get('GPT_MODEL_3_TURBO'),
                temperature=0.2
            )
            response_data = completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(e)
            response_data = 'Oops something went.'

        data = {
            'answer': response_data
        }

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value,
                                  data=data,
                                  error=None)

    @classmethod
    def send_reminder_to_signees(cls):
        """Send reminder mail to signees who haven't signed the contract"""
        logger.info('Started send_reminder_to_signees')
        contracts = Contract.get_uuid_by_status(
            status=ContractStatus.SENT_FOR_SIGNING.value)
        contract_uuids = [data[0] for data in contracts]
        contract_signees = ContractSignee.get_email_by_contact_uuids_and_status(status=ContractMailStatus.PENDING.value,
                                                                                contract_uuids=contract_uuids)
        signee_data = []
        for data in contract_signees:
            signee_details = {
                'uuid': data[0],
                'signee_email': data[1],
                'signee_full_name': data[2],
                'account_uuid': data[3],
                'contract_uuid': data[4]
            }

            signee_data.append(signee_details)

        for signee in signee_data:
            contract_token = generate_email_token(signee['uuid'])
            contract_link = config_data.get(
                'APP_URL') + '/contract/sign-contract?token=' + contract_token

            email_template_obj = EmailTemplate.get_email_template_by_email_type(
                account_uuid=signee['account_uuid'], email_type=EmailTypes.SEND_REMINDER_TO_SIGNEE.value)

            email_template_body = email_template_obj.email_body
            email_template_subject = email_template_obj.email_subject
            email_template_body = email_template_body.format(
                name=signee['signee_full_name'], contract_link=contract_link)

            email_data = {
                'email_to': signee['signee_email'],
                'subject': email_template_subject,
                'template': 'emails/signature_reminder_email.html',
                'email_type': EmailTypes.SEND_REMINDER_TO_SIGNEE.value,
                'email_data': {
                    'email_body': email_template_body
                }
            }

            EmailWorker.send(email_data)
            current_date = datetime.now().strftime('%Y-%m-%d')
            logger.info('contract_uuid')
            logger.info(signee['contract_uuid'])
            contract_log_data = {
                'uuid': ContractLog.create_uuid(),
                'account_uuid': signee['account_uuid'],
                'contract_uuid': signee['contract_uuid'],
                'description': 'Reminder email sent to {} on {}.'.format(signee['signee_full_name'], current_date)
            }

            ContractLog.add(contract_log_data)
