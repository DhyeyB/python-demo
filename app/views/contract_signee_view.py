import datetime
import os

from flask import request
from magic import Magic

from app.helpers.constants import ContractStatus, ContractMailStatus, SupportedImageTypes
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import field_type_validator
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.models.client import Client
from app.models.contract import Contract
from app.models.contract_log import ContractLog
from app.models.contract_signee import ContractSignee
from app.views.base_view import BaseView
from app.models.signee import Signee
from workers.email_worker import EmailWorker
from app.helpers.constants import EmailSubject
from app.helpers.constants import EmailTypes
from app.helpers.utility import generate_email_token
from app import config_data, logger
from workers.s3_worker import upload_file_and_get_object_details, get_presigned_url
from app.models.email_template import EmailTemplate
from app.models.user import User


class ContractSigneeView(BaseView):
    @classmethod
    def list_signees(cls, contract_uuid):
        """Return all signee data of given contract."""
        is_required_all = request.args.get('all', False)
        user_obj = cls.get_logged_in_user(request=request)
        account_uuid = user_obj.account_uuid

        if is_required_all:
            contract_signees = ContractSignee.get_by_account_and_contract(account_uuid=account_uuid,
                                                                          contract_uuid=contract_uuid)
        else:
            contract_obj = Contract.get_by_uuid(uuid=contract_uuid)
            client_uuid = contract_obj.client_uuid
            contract_signees = ContractSignee.get_by_account_client_and_contract(
                account_uuid=account_uuid, client_uuid=client_uuid, contract_uuid=contract_uuid)

        contract_signees_list = ContractSignee.serialize(contract_signees)
        data = {'result': contract_signees_list}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_signature_s3_link(cls):
        """Store image in S3 bucket and return S3 bucket link"""
        uuid_data = request.form
        field_types = {'contract_signee_uuid': str}
        required_fields = ['contract_signee_uuid']

        post_data = field_type_validator(
            request_data=uuid_data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=uuid_data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        data = request.files
        signature_file = data.get('signature_file')
        required_fields = ['signature_file']

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

        file_name = signature_file.filename
        temp_path = os.path.join(config_data['UPLOAD_FOLDER'], file_name)  # type: ignore  # noqa: FKA100
        signature_file.save(temp_path)

        content_type = Magic(mime=True).from_file(temp_path)
        if content_type not in SupportedImageTypes.values():
            os.remove(temp_path)
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_FILE_TYPE.value, data=None)

        contract_signee_uuid = uuid_data.get('contract_signee_uuid')
        contract_signee_obj = ContractSignee.get_by_uuid(
            uuid=contract_signee_uuid)
        contract_obj = Contract.get_by_uuid(
            uuid=contract_signee_obj.contract_uuid)

        try:
            s3_folder_path = f'media/{contract_obj.account_uuid}/{contract_obj.client_uuid}/{contract_obj.uuid}/signature'.lower()
            s3_file_path = upload_file_and_get_object_details(file_path=temp_path,
                                                              file_name=file_name,
                                                              s3_folder_path=s3_folder_path)
            s3_bucket_link = get_presigned_url(path=s3_file_path)

            data = {'s3_bucket_link': s3_bucket_link}
        except Exception as e:
            logger.error(e)
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.IMAGE_STORED_SUCCESSFULLY.value, data=data,
                                  error=None)

    @classmethod
    def submit(cls):
        """Steps to perform on contract submit"""
        data = request.get_json(force=True)
        field_types = {'contract_signee_uuid': str,
                       'signed_content': str, 'signature': str, 'signature_type': str}
        required_fields = ['contract_signee_uuid',
                           'signed_content', 'signature', 'signature_type']

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

        signee_signature = data.get('signature')
        signature_type = data.get('signature_type')
        contract_signee_uuid = data.get('contract_signee_uuid')
        contract_signee_obj = ContractSignee.get_by_uuid(
            uuid=contract_signee_uuid)
        contract_signee_obj.status = ContractMailStatus.SIGNED.value
        contract_signee_obj.signee_signature = signee_signature
        contract_signee_obj.signature_type = signature_type
        contract_signee_obj.signee_ip = request.environ.get('REMOTE_ADDR')
        contract_signee_obj.signed_at = int(
            datetime.datetime.utcnow().timestamp())
        ContractSignee.update()

        contract_uuid = contract_signee_obj.contract_uuid
        contract_obj = Contract.get_by_uuid(uuid=contract_uuid)
        contract_obj.signed_content = data.get('signed_content')
        Contract.update()

        signee_uuid = contract_signee_obj.signee_uuid
        signee_obj = Signee.get_by_uuid(signee_uuid)

        contract_log_data = {
            'uuid': ContractLog.create_uuid(),
            'account_uuid': contract_obj.account_uuid,
            'contract_uuid': contract_uuid,
            'description': '{} signed this document.'.format(signee_obj.full_name)
        }
        ContractLog.add(contract_log_data)

        email_template_obj = EmailTemplate.get_email_template_by_email_type(
            account_uuid=contract_obj.account_uuid, email_type=EmailTypes.CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE.value)
        email_template_body = email_template_obj.email_body
        email_template_subject = email_template_obj.email_subject

        email_template_body = email_template_body.format(
            name=signee_obj.full_name)

        email_data = {
            'email_to': signee_obj.email,
            'subject': email_template_subject,
            'template': 'emails/contract_signing_status_complete.html',
            'email_type': EmailTypes.CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE.value,
            'email_data': {
                'email_body': email_template_body
            }
        }
        EmailWorker.send(email_data)

        client_uuid = contract_obj.client_uuid
        client_obj = Client.get_by_uuid(uuid=client_uuid)
        account_owner = User.get_primary_user_of_account(
            contract_obj.account_uuid)

        if client_obj.priority_required and contract_signee_obj.signee_priority is not None:
            next_signee_obj = ContractSignee.get_next_signee(contract_uuid=contract_uuid,
                                                             signee_priority=contract_signee_obj.signee_priority)

            if next_signee_obj is not None:
                contract_token = generate_email_token(next_signee_obj.uuid)
                contract_link = config_data.get(
                    'APP_URL') + '/contract/sign-contract?token=' + contract_token

                email_template_obj = EmailTemplate.get_email_template_by_email_type(
                    account_uuid=contract_obj.account_uuid, email_type=EmailTypes.SEND_CONTRACT_TO_SIGNEE.value)
                email_template_subject = email_template_obj.email_subject
                email_template_body = email_template_obj.email_body
                email_template_body = email_template_body.format(
                    signee_name=next_signee_obj.signee_full_name, contract_link=contract_link, contact_information=account_owner.email)
                email_data = {
                    'email_to': next_signee_obj.signee_email,
                    'subject': email_template_subject,
                    'template': 'emails/send_contract_to_signee.html',
                    'email_type': EmailTypes.SEND_CONTRACT_TO_SIGNEE.value,
                    'email_data': {
                        'email_body': email_template_body
                    }
                }
                EmailWorker.send(email_data)
                next_signee_obj.status = ContractMailStatus.PENDING.value
                ContractSignee.update()

        pending_status_signees_count = ContractSignee.get_count_by_contact_uuid_and_status(contract_uuid=contract_uuid,
                                                                                           status=ContractMailStatus.PENDING.value)
        if not pending_status_signees_count:
            account_uuid = contract_obj.account_uuid
            contract_signees = ContractSignee.get_by_account_and_contract(account_uuid=account_uuid,
                                                                          contract_uuid=contract_uuid)
            recipients_list = []
            for signee in contract_signees:
                temp_dict = {'email': signee.signee_email,
                             'full_name': signee.signee_full_name}
                recipients_list.append(temp_dict)

            contract_link = config_data.get(
                'APP_URL') + '/contract/view/' + contract_obj.uuid
            for recipient in recipients_list:
                email_data = {
                    'email_to': recipient.get('email'),
                    'subject': EmailSubject.CONTRACT_SIGNED_BY_ALL_SIGNEE.value,
                    'template': 'emails/update_account_owner_when_contract_signed_by_all_signee.html',
                    'email_type': EmailTypes.UPDATE_CONTRACT_AUTHOR_WHEN_CONTRACT_SIGNED_BY_ALL_SIGNEE.value,
                    'email_data': {
                        'full_name': recipient.get('full_name'),
                        'contract_link': contract_link
                    }
                }
                EmailWorker.send(data=email_data)

            contract_obj.status = ContractStatus.SIGNED.value
            Contract.update()

            contract_log_data = {
                'uuid': ContractLog.create_uuid(),
                'account_uuid': contract_obj.account_uuid,
                'contract_uuid': contract_uuid,
                'description': 'Document has been signed by all signees. '
            }
            ContractLog.add(contract_log_data)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.STATUS_UPDATED_SUCCESSFULLY.value, data=None,
                                  error=None)
