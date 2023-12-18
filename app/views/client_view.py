"""Contains Client related API definitions."""
import os
from datetime import datetime

from app import config_data
from app.helpers.constants import EmailSubject, CurrencyCode
from app.helpers.constants import EmailTypes
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import SupportedExcelTypes
from app.helpers.utility import field_type_validator
from app.helpers.utility import get_pagination_meta
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.helpers.utility import validate_email
from app.models.client import Client
from app.models.contract import Contract
from app.models.user import User
from app.views.base_view import BaseView
from flask import request
from magic import Magic
import pandas as pd
from slugify import slugify
from workers.email_worker import EmailWorker
from workers.s3_worker import upload_file_and_get_object_details, get_presigned_url


class ClientView(BaseView):
    @classmethod
    def create_update(cls):
        """Create and update client object"""
        data = request.get_json(force=True)
        field_types = {'client_uuid': str, 'legal_name': str, 'display_name': str, 'email': str, 'phone': str,
                       'street_name': str, 'postal_code': str, 'city': str, 'state': str, 'country': str}

        client_uuid = data.get('client_uuid', None)
        required_fields = ['legal_name', 'display_name', 'email', 'phone']

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

        if data.get('email', '') and not validate_email(data.get('email')):
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, data=None,
                                      error=None)

        if client_uuid is None:
            user_obj = ClientView.get_logged_in_user(request=request)
            user_uuid = user_obj.uuid
            account_uuid = user_obj.account_uuid
            legal_name_slug = slugify(data.get('legal_name'))

            if Client.check_if_client_exits(account_uuid=account_uuid, legal_name_slug=legal_name_slug):
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.CLIENT_ALREADY_EXISTS.value.format(data.get('legal_name')), data=None,
                                          error=None)

            client_data = {
                'uuid': Client.create_uuid(),
                'account_uuid': account_uuid,
                'created_by': user_uuid,
                'legal_name': data.get('legal_name'),
                'legal_name_slug': legal_name_slug,
                'display_name': data.get('display_name'),
                'email': data.get('email').lower(),
                'phone': data.get('phone')
            }
            client = Client.add(client_data)

            if client is None:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.FAILED.value, data=None,
                                          error=None)

            account_owner = User.get_primary_user_of_account(
                account_uuid=account_uuid)
            data = {
                'email_to': account_owner.email,
                'subject': EmailSubject.NEW_CLIENT_ADDED.value,
                'template': 'emails/client_added_to_account.html',
                'email_type': EmailTypes.CLIENT_ADDED.value,
                'email_data': {
                    'user_name': account_owner.first_name,
                    'client_name': data.get('legal_name')
                }
            }
            EmailWorker.send(data)

            data = {'client': Client.serialize(client)}
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.CLIENT_CREATED_SUCCESSFULLY.value, data=data,
                                      error=None)
        else:
            client_obj = Client.get_by_uuid(client_uuid)
            if client_obj is None:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.CLIENT_NOT_FOUND.value, data=None,
                                          error=None)

            account_uuid = client_obj.account_uuid
            legal_name_slug = slugify(data.get('legal_name'))

            if Client.check_if_client_exits(account_uuid=account_uuid, legal_name_slug=legal_name_slug,
                                            client_uuid=client_uuid):
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.CLIENT_ALREADY_EXISTS.value.format(data.get('legal_name')), data=None,
                                          error=None)

            client_obj.legal_name = data.get('legal_name')
            client_obj.legal_name_slug = legal_name_slug
            client_obj.display_name = data.get('display_name')
            client_obj.email = data.get('email').lower()
            client_obj.phone = data.get('phone')
            client_obj.street_name = data.get('street_name')
            client_obj.postal_code = data.get('postal_code')
            client_obj.city = data.get('city')
            client_obj.state = data.get('state')
            client_obj.country = data.get('country')
            client_obj.currency_code = CurrencyCode.get(data.get('country'))
            Client.update()

            data = {'client': Client.serialize(client_obj)}
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.CLIENT_DATA_UPDATED_SUCCESSFULLY.value, data=data,
                                      error=None)

    @classmethod
    def bulk_upload(cls):
        """Bulk insert clients from Excel file"""
        user_obj = ClientView.get_logged_in_user(request=request)
        user_uuid = user_obj.uuid
        account_uuid = user_obj.account_uuid

        data = request.files
        required_fields = ['clients_data']
        is_valid = required_validator(
            request_data=data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        clients_data = data.get('clients_data')
        temp_path = os.path.join(config_data['UPLOAD_FOLDER'], clients_data.filename)  # type: ignore  # noqa: FKA100
        clients_data.save(temp_path)
        content_type = Magic(mime=True).from_file(temp_path)

        if content_type not in SupportedExcelTypes.values():
            os.remove(temp_path)
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_FILE_TYPE.value, data=None)

        df = pd.read_excel(temp_path)
        clients_data = df.to_dict(orient='records')

        field_types = {'legal_name': str, 'display_name': str, 'email': str, 'phone': int, 'street_name': str,
                       'postal_code': int, 'city': str, 'state': str, 'country': str}
        required_fields = ['legal_name', 'display_name', 'email', 'phone', 'street_name', 'postal_code', 'city',
                           'state', 'country']

        error_data_list = []
        for data in clients_data:
            client_data = {
                'legal_name': data.get('legal_name'),
                'display_name': data.get('display_name'),
                'email': data.get('email').lower(),
                'phone': str(data.get('phone')),
                'street_name': data.get('street_name'),
                'postal_code': str(data.get('postal_code')),
                'city': data.get('city'),
                'state': data.get('state'),
                'country': data.get('country')
            }
            post_data = field_type_validator(
                request_data=data, field_types=field_types)
            if post_data['is_error']:
                client_data['error'] = post_data['data']
                error_data_list.append(client_data)
                continue

            is_valid = required_validator(
                request_data=data, required_fields=required_fields)
            if is_valid['is_error']:
                client_data['error'] = is_valid['data']
                error_data_list.append(client_data)
                continue

            if not validate_email(data.get('email')):
                client_data['error'] = ResponseMessageKeys.INVALID_EMAIL_FORMAT.value
                error_data_list.append(client_data)
                continue

            legal_name_slug = slugify(data.get('legal_name'))
            if Client.check_if_client_exits(account_uuid=account_uuid, legal_name_slug=legal_name_slug):
                client_data['error'] = ResponseMessageKeys.CLIENT_ALREADY_EXISTS.value.format(
                    data.get('legal_name'))
                error_data_list.append(client_data)
                continue

            client_data['uuid'] = Client.create_uuid()
            client_data['account_uuid'] = account_uuid
            client_data['created_by'] = user_uuid
            client_data['legal_name_slug'] = legal_name_slug
            Client.add(client_data)

        os.remove(temp_path)

        if not error_data_list:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.CLIENT_CREATED_SUCCESSFULLY.value,
                                      data=None, error=None)

        df = pd.DataFrame.from_dict(error_data_list)

        time_stamp = str(int(datetime.now().timestamp()))
        file_name = 'error_client_data_{}.xlsx'.format(time_stamp)
        error_file_local_path = os.path.join(config_data['UPLOAD_FOLDER'], file_name)  # type: ignore  # noqa: FKA100
        df.to_excel(error_file_local_path, index=False)

        s3_folder_path = f'media/{account_uuid}/{user_uuid}/'.lower()
        s3_file_path = upload_file_and_get_object_details(file_path=error_file_local_path,
                                                          file_name=file_name,
                                                          s3_folder_path=s3_folder_path)
        s3_bucket_link = get_presigned_url(path=s3_file_path)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                  message_key=ResponseMessageKeys.FAILED.value,
                                  data=None, error={'error_file': s3_bucket_link})

    @classmethod
    def list(cls):
        """
        Get all clients belong to the logged-in user's account.
        Return data in a paginated format.
        """
        user_obj = ClientView.get_logged_in_user(request=request)

        account_uuid = user_obj.account_uuid
        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        client_objs, objects_count = Client.get_all_by_account_uuid(q=q, sort=sort, page=page, size=size,
                                                                    account_uuid=account_uuid)
        client_list = Client.serialize(client_objs)

        data = {'result': client_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=objects_count if size is None else int(
                                                               size),
                                                           total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_by_uuid(cls, client_uuid: str):
        """Get client by client_uuid"""
        client_obj = Client.get_by_uuid(client_uuid)
        if client_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.CLIENT_NOT_FOUND.value, data=None,
                                      error=None)
        client_data = Client.serialize(client_obj)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=client_data,
                                  error=None)
