import jwt
from flask import request


from app import logger, config_data
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import field_type_validator
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.models.contract_log import ContractLog
from app.models.contract_signee import ContractSignee
from app.views.base_view import BaseView


class ContractLogView(BaseView):
    @classmethod
    def add_log_on_open(cls):
        """Add Contract Log of signee review doc """
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
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.CONTRACT_SIGNEE_NOT_FOUND.value, data=None,
                                          error=None)

            contract_log_data = {
                'uuid': ContractLog.create_uuid(),
                'account_uuid': contract_signee_obj.account_uuid,
                'contract_uuid': contract_signee_obj.contract_uuid,
                'description': '{} opened this document.'.format(contract_signee_obj.signee_full_name)
            }
            ContractLog.add(contract_log_data)
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.LOG_IS_ADDED_SUCCESSFULLY.value, data=None,
                                      error=None)

        except Exception as e:
            logger.info('we got exception : {}'.format(e))
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_TOKEN.value, data=None,
                                      error=None)

    @classmethod
    def list_logs(cls, contract_uuid):
        """Return logs of selected Contract of Current user's account."""
        user_obj = cls.get_logged_in_user(request=request)
        account_uuid = user_obj.account_uuid
        contract_logs = ContractLog.get_by_account_and_contract(
            account_uuid=account_uuid, contract_uuid=contract_uuid)
        contract_logs_list = ContractLog.serialize(contract_logs)
        data = {'result': contract_logs_list}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)
