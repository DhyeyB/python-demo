from datetime import datetime

from app import config_data
from app.helpers.constants import EmailSubject
from app.helpers.constants import EmailTypes
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import UserType
from app.helpers.utility import field_type_validator
from app.helpers.utility import get_pagination_meta
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.helpers.utility import validate_email
from app.models.contact_us import ContactUs
from app.views.base_view import BaseView
from flask import request
from workers.email_worker import EmailWorker


class ContactUsView(BaseView):
    @classmethod
    def create(cls):
        """Create Contact Us object"""
        data = request.get_json(force=True)
        field_types = {'first_name': str, 'last_name': str, 'email': str,
                       'company_size': int, 'company_name': str, 'message': str}
        required_fields = ['email', 'company_name']
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

        if not validate_email(data.get('email')):
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, data=None,
                                      error=None)

        contact_us_uuid = ContactUs.create_uuid()

        contact_us_data = {
            'uuid': contact_us_uuid,
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'company_size': data.get('company_size'),
            'company_name': data.get('company_name'),
            'message': data.get('message')
        }

        contact_us_obj = ContactUs.add(contact_us_data)
        if contact_us_obj is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)
        # Get the current date and time
        current_datetime = datetime.now()

        # Format the current date and time as a human-readable string
        human_readable_format = current_datetime.strftime(
            '%A, %B %d, %Y %I:%M:%S %p')
        # Split the email addresses by comma
        email_addresses = config_data['ADMIN_NOTIFICATION_EMAIL'].split(',')

        # Iterate through the email addresses and send the email to each one
        for email_address in email_addresses:
            email_data = {
                'email_to': email_address.strip(),
                'subject': EmailSubject.CONTACT_US_SUBMISSION.value,
                'template': 'emails/contact_us_submit.html',
                'email_type': EmailTypes.CONTACT_US_SUBMISSION.value,
                'email_data': {
                    'first_name': data.get('first_name'),
                    'last_name': data.get('last_name'),
                    'email': data.get('email'),
                    'company_size': data.get('company_size'),
                    'company_name': data.get('company_name'),
                    'message': data.get('message'),
                    'date_and_time_of_inquiry': human_readable_format
                }
            }

            EmailWorker.send(email_data)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.MESSAGE_RECEIVED_SUCCESSFULLY.value, data=None,
                                  error=None)

    @classmethod
    def list(cls):
        """Return list of Contact Us object data according to given page, size, sort and q(filter query)."""
        user_obj = ContactUsView.get_logged_in_user(request=request)

        if user_obj.user_type != UserType.SUPER_ADMIN.value:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.NOT_ALLOWED.value, data=None,
                                      error=None)

        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        contact_us_objs, objects_count = ContactUs.get_contact_us_list(
            q=q, sort=sort, page=page, size=size)
        contact_us_list = ContactUs.serialize(contact_us_objs)

        data = {'result': contact_us_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=int(size), total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_by_uuid(cls, contact_us_request_uuid: str):
        """Get Contact Us object data by given uuid"""
        user_obj = ContactUsView.get_logged_in_user(request=request)

        if user_obj.user_type != UserType.SUPER_ADMIN.value:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.NOT_ALLOWED.value, data=None,
                                      error=None)

        contact_us_obj = ContactUs.get_by_uuid(contact_us_request_uuid)
        if contact_us_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.CONTACT_US_REQUEST_NOT_FOUND.value, data=None,
                                      error=None)
        contact_us_data = ContactUs.serialize(contact_us_obj)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=contact_us_data,
                                  error=None)
