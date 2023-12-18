"""Contains Signee related API definitions."""
from app import logger
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import field_type_validator
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.helpers.utility import validate_email
from app.models.client import Client
from app.models.signee import Signee
from app.models.contract_signee import ContractSignee
from app.views.base_view import BaseView
from flask import request
from app.helpers.constants import UserType


class SigneeView(BaseView):
    @classmethod
    def create(cls):
        """Create signee"""
        user_obj = SigneeView.get_logged_in_user(request=request)
        user_uuid = user_obj.uuid
        account_uuid = user_obj.account_uuid

        data = request.get_json(force=True)

        # priority_required is updated in client
        client_data = data.get('client_data')
        field_types = {'client_uuid': str, 'priority_required': bool}
        required_fields = ['client_uuid', 'priority_required']
        post_data = field_type_validator(
            request_data=client_data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=client_data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])
        client_uuid = client_data.get('client_uuid')
        priority_required = client_data.get('priority_required')
        client_obj = Client.get_by_uuid(uuid=client_uuid)
        client_obj.priority_required = priority_required
        Client.update()

        # add signees in db
        all_signees_data = data.get('signees_data')
        field_types = {'client_uuid': str, 'full_name': str,
                       'job_title': str, 'email': str, 'signing_sequence': int}
        required_fields = ['client_uuid',
                           'full_name', 'email', 'signing_sequence']

        signees_data_list = []
        signee_uuids = []
        for signee_data in all_signees_data:
            post_data = field_type_validator(
                request_data=signee_data, field_types=field_types)
            if post_data['is_error']:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                          error=post_data['data'])

            is_valid = required_validator(
                request_data=signee_data, required_fields=required_fields)
            if is_valid['is_error']:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                          error=is_valid['data'])

            if not validate_email(signee_data.get('email')):
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, data=None,
                                          error=None)

            if Signee.check_if_email_already_exists(account_uuid=account_uuid, email=signee_data.get('email').lower()):
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.SIGNEE_EMAIL_ALREADY_EXISTS.value.format(
                                              signee_data.get('email')),
                                          data=None, error=None)

            signee_data = {
                'uuid': Signee.create_uuid(),
                'client_uuid': signee_data.get('client_uuid'),
                'account_uuid': account_uuid,
                'created_by': user_uuid,
                'full_name': signee_data.get('full_name'),
                'job_title': signee_data.get('job_title', None),
                'email': signee_data.get('email').lower(),
                'signing_sequence': signee_data.get('signing_sequence')
            }
            signees_data_list.append(signee_data)
            signee_uuids.append(signee_data.get('uuid'))

        try:
            Signee.bulk_insert(signees_data_list)
        except Exception as e:
            logger.error(e)
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SIGNEES_CREATED_SUCCESSFULLY.value, data=signee_uuids,
                                  error=None)

    @classmethod
    def get_by_client_uuid(cls, client_uuid):
        """Get all signees belong to given client"""
        user_obj = cls.get_logged_in_user(request=request)

        if user_obj.user_type == UserType.SUPER_ADMIN.value:
            signee_objs = Signee.get_all_by_client_uuid(
                client_uuid=client_uuid)
        else:
            account_uuid = user_obj.account_uuid
            signee_objs = Signee.get_all_by_client_uuid(
                account_uuid=account_uuid, client_uuid=client_uuid)

        signee_list = Signee.serialize(signee_objs)

        data = {'result': signee_list}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_by_uuid(cls, signee_uuid: str):
        """Get signee by signee_uuid"""
        signee_obj = Signee.get_by_uuid(signee_uuid)
        if signee_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.SIGNEE_NOT_FOUND.value, data=None,
                                      error=None)
        signee_data = Signee.serialize(signee_obj)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=signee_data,
                                  error=None)

    @classmethod
    def update_by_client_uuid(cls, client_uuid: str):
        """Update signee record of given client_uuid"""
        user_obj = SigneeView.get_logged_in_user(request=request)
        user_uuid = user_obj.uuid
        account_uuid = user_obj.account_uuid

        client_obj = Client.get_by_uuid(uuid=client_uuid)
        if client_obj is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.CLIENT_NOT_FOUND.value, data=None,
                                      error=None)

        all_data = request.get_json(force=True)

        # priority_required is updated in client
        client_data = all_data.get('client_data')
        field_types = {'client_uuid': str, 'priority_required': bool}
        required_fields = ['client_uuid', 'priority_required']
        post_data = field_type_validator(
            request_data=client_data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=client_data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])
        client_uuid = client_data.get('client_uuid')
        priority_required = client_data.get('priority_required')
        client_obj = Client.get_by_uuid(uuid=client_uuid)
        client_obj.priority_required = priority_required
        Client.update()

        signee_data = all_data.get('signees_data')
        field_types = {'client_uuid': str, 'signee_uuid': str, 'full_name': str,
                       'job_title': str, 'email': str, 'signing_sequence': int}
        required_fields = ['client_uuid',
                           'full_name', 'email', 'signing_sequence']

        signees = Signee.get_all_signee_uuid_by_client_uuid(
            account_uuid=account_uuid, client_uuid=client_uuid)
        db_signee_uuid_list = [data[0] for data in signees]
        signee_uuids = []
        for data in signee_data:
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

            email = data.get('email').lower()
            if not validate_email(email):
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, data=None,
                                          error=None)

            signee_uuid = data.get('signee_uuid')
            if not signee_uuid:
                # New Signee - Create
                if Signee.check_if_email_already_exists(account_uuid=account_uuid, email=email):
                    return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                              message_key=ResponseMessageKeys.SIGNEE_EMAIL_ALREADY_EXISTS.value.format(
                                                  email),
                                              data=None, error=None)
                signee_data = {
                    'uuid': Signee.create_uuid(),
                    'client_uuid': client_uuid,
                    'account_uuid': account_uuid,
                    'created_by': user_uuid,
                    'full_name': data.get('full_name'),
                    'job_title': data.get('job_title', None),
                    'email': email,
                    'signing_sequence': data.get('signing_sequence')
                }
                signee_obj = Signee.add(signee_data)

                signee_uuids.append(signee_data.get('uuid'))
                if signee_obj is None:
                    return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                              message_key=ResponseMessageKeys.FAILED.value, data=None,
                                              error=None)
            else:
                # Existing Signee - Update
                signee_obj = Signee.get_by_uuid(signee_uuid)
                if Signee.check_if_email_already_exists(account_uuid=account_uuid, email=email, signee_uuid=signee_obj.uuid):
                    return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                              message_key=ResponseMessageKeys.SIGNEE_EMAIL_ALREADY_EXISTS.value.format(
                                                  email),
                                              data=None, error=None)
                if signee_obj is None:
                    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                              message_key=ResponseMessageKeys.SIGNEE_NOT_FOUND.value, data=None,
                                              error=None)

                signee_obj.full_name = data.get('full_name')
                signee_obj.job_title = data.get('job_title', None)
                signee_obj.email = email
                signee_obj.signing_sequence = data.get('signing_sequence')
                Signee.update()

                db_signee_uuid_list.remove(signee_uuid)

        associated_contract_found = False

        associated_signees = ''
        for remaining_signee_uuid in db_signee_uuid_list:
            signee_obj = ContractSignee.get_contract_signee_by_signee_uuid(account_uuid=account_uuid,
                                                                           signee_uuid=remaining_signee_uuid)

            if signee_obj:
                associated_contract_found = True
                associated_signees += ',' + signee_obj.signee_email
            else:
                Signee.delete_by_uuid(remaining_signee_uuid)

        if associated_contract_found:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.SIGEE_ALREADY_HAVE_CONTRACT_ASCCOCIATED_AND_CANT_BE_DELETED.value.format(associated_signees), data=None,
                                      error=None)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SIGNEE_DATA_UPDATED_SUCCESSFULLY.value, data=signee_uuids,
                                  error=None)
