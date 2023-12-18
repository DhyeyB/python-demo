"""Contains email templates relates api information"""

from app.views.base_view import BaseView
from flask import request
from app.models.email_template import EmailTemplate
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import required_validator, field_type_validator, get_pagination_meta
from app.helpers.utility import send_json_response
from app.helpers.constants import EmailTypes
from app import logger


class EmailTemplateView(BaseView):
    @classmethod
    def list(cls):
        """Return list of Email Template object data according to given page, size, sort and q(filter query)."""
        user_obj = EmailTemplateView.get_logged_in_user(request=request)

        account_uuid = user_obj.account_uuid

        page = request.args.get('page')
        q = request.args.get('q')
        size = request.args.get('size')
        sort = request.args.get('sort')

        email_template_objs, objects_count = EmailTemplate.get_email_template_list(
            account_uuid=account_uuid, page=page, q=q, size=size, sort=sort)

        email_template_list = EmailTemplate.serialize(email_template_objs)

        data = {'result': email_template_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=objects_count if size is None else int(
                                                               size),
                                                           total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_by_uuid(cls, email_template_uuid: str):
        """Get Email Template object data by given uuid"""
        email_template_obj = EmailTemplate.get_by_uuid(email_template_uuid)
        if email_template_obj is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.EMAIL_TEMPLATE_NOT_FOUND.value, data=None,
                                      error=None)

        email_template_data = EmailTemplate.serialize(email_template_obj)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=email_template_data,
                                  error=None)

    @classmethod
    def update_by_uuid(cls, email_template_uuid: str):
        """Update Email Template Object data by given uuid."""
        data = request.get_json(force=True)
        field_types = {'email_subject': str, 'email_body': str}
        required_fields = ['email_subject', 'email_body']

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

        email_template_obj = EmailTemplate.get_by_uuid(email_template_uuid)
        if email_template_obj is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.EMAIL_TEMPLATE_NOT_FOUND.value, error=None,
                                      data=None)

        email_template_type = email_template_obj.email_type
        email_template_body = data.get('email_body')

        # Check if the dynamic variable are named correctly while updating
        try:
            if email_template_type == EmailTypes.SEND_CONTRACT_TO_SIGNEE.value:
                email_template_body.format(
                    signee_name='signee_name', contract_link='contract_link', contact_information='contact_information')
            if email_template_type == EmailTypes.CONTRACT_CANCELLED.value:
                email_template_body.format(name='name')
            if email_template_type == EmailTypes.CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE.value:
                email_template_body.format(name='name')
            if email_template_type == EmailTypes.SEND_REMINDER_TO_SIGNEE.value:
                email_template_body.format(
                    name='name', contract_link='contract_link')
        except KeyError as exception_error:
            logger.error(
                f'An error occurred while updating the Email Body :- {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=(f'An error occurred while updating the Email Body, Please udpate the variable :- {exception_error}'), error=None,
                                      data=None)

        email_template_obj.email_body = data.get('email_body')
        email_template_obj.email_subject = data.get('email_subject')

        EmailTemplate.update()

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, error=None,
                                  data=None)
