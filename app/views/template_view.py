"""Contains user related API definitions."""
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import field_type_validator
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.models.template import Template
from flask import request


def create_template():
    data = request.get_json(force=True)
    field_types = {'name': str, 'content': str}
    required_fields = ['name', 'content']
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

    # user_id and account id will be used from token recived from congnito
    template_data = {
        'user_id': data.get('user_id'),
        'account_id': data.get('account_id'),
        'name': data.get('name'),
        'content': data.get('content')
    }

    template = Template.add(template_data)
    if template is None:
        return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                  message_key=ResponseMessageKeys.FAILED.value, data=None,
                                  error=None)

    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                              message_key=ResponseMessageKeys.RECORD_ADDED_SUCCESSFULLY.value, data=None,
                              error=None)


def get_all_templates():
    templates = Template.get_all()
    templates_data = Template.serialize_template(templates)
    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                              message_key=ResponseMessageKeys.SUCCESS.value, data=templates_data,
                              error=None)


def get_all_templates_by_account(account_id: int):
    templates = Template.get_template_by_account(account_id)
    templates_data = Template.serialize_template(templates)
    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                              message_key=ResponseMessageKeys.SUCCESS.value, data=templates_data,
                              error=None)


def get_template_by_id(template_id: int):
    template = Template.get_by_id(template_id)
    template_data = Template.serialize_template(template)
    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                              message_key=ResponseMessageKeys.SUCCESS.value, data=template_data,
                              error=None)


def delete_template(template_id: int):
    Template.delete_by_id(template_id)
    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                              message_key=ResponseMessageKeys.RECORD_DELETED_SUCCESSFULLY.value, data=None,
                              error=None)


def update_template(template_id: int):
    data = request.get_json(force=True)
    field_types = {'name': str, 'content': str}
    required_fields = ['name', 'content']
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

    template = Template.get_by_id(template_id)
    template.name = data.get('name')
    template.content = data.get('content')

    Template.update()

    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                              message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                              error=None)
