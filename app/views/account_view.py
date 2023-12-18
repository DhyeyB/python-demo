"""Contains user related API definitions."""
from slugify import slugify

from app.helpers.constants import HttpStatusCode, UserType, CurrencyCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import field_type_validator
from app.helpers.utility import get_pagination_meta
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.models.account import Account
from app.models.client import Client
from app.models.contract import Contract
from app.models.signee import Signee
from app.views.base_view import BaseView
from flask import request
from datetime import datetime, timedelta
from app.helpers.constants import DEFAULT_PRE_DELETION_PERIOD_IN_DAYS
from app import logger, COGNITO_CLIENT
from app.models.user import User
from app.views.user_view import UserView
from workers.email_worker import EmailWorker
from app.helpers.constants import EmailSubject
from app.helpers.constants import EmailTypes
import os
import pandas as pd
from workers.s3_worker import upload_file_and_get_object_details, get_presigned_url
from app import config_data
from bombaysoftwares_pysupp import str_to_bool


class AccountView(BaseView):
    @classmethod
    # @cross_origin()
    def list(cls):
        """Return list of Account object data according to given page, size, sort and q(filter query)."""
        user_obj = AccountView.get_logged_in_user(request=request)

        if user_obj.user_type != UserType.SUPER_ADMIN.value:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.NOT_ALLOWED.value, data=None,
                                      error=None)

        download = request.args.get('download')
        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        accounts_objs, objects_count = Account.get_account_list(
            q=q, sort=sort, page=page, size=size)
        accounts_list = [row._asdict() for row in accounts_objs]

        if download and str_to_bool(download):
            accounts_objs = Account.get_account_list(
                q=q, sort=sort, page=page, size=size, download=download)

            csv_accounts_list = [row._asdict() for row in accounts_objs]
            df = pd.DataFrame.from_dict(csv_accounts_list)

            time_stamp = str(int(datetime.now().timestamp()))

            file_name = 'account_list_data_{}.csv'.format(time_stamp)
            account_list_data_path = os.path.join(config_data['UPLOAD_FOLDER'], file_name)  # type: ignore  # noqa: FKA100
            df.to_csv(account_list_data_path, index=False)

            s3_folder_path = f'media/accounts/{user_obj.account_uuid}/'.lower()
            s3_file_path = upload_file_and_get_object_details(file_path=account_list_data_path,
                                                              file_name=file_name,
                                                              s3_folder_path=s3_folder_path)
            s3_bucket_link = get_presigned_url(path=s3_file_path)

            logger.info(
                f'CSV file "{account_list_data_path}" has been created And can be downloaded using this link -> {s3_bucket_link}')

            data = {
                'download_link': s3_bucket_link
            }

            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                      error=None)

        data = {'result': accounts_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=int(size), total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_account_by_uuid(cls, account_uuid: str):
        account = Account.get_by_uuid(account_uuid)
        if account is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                      error=None)
        account_data = Account.serialize(account)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=account_data,
                                  error=None)

    @classmethod
    def update_account(cls, account_uuid: str):
        """Update account details"""
        authorization_header = request.headers.get('Authorization')
        access_token = authorization_header.replace('Bearer ', '').strip()
        if access_token:
            user_info = COGNITO_CLIENT.get_user(AccessToken=access_token)
        else:
            return send_json_response(http_status=401, response_status=False,
                                      message_key=ResponseMessageKeys.ACCESS_DENIED.value, data=None, error=None)

        user_email = [data.get('Value') for data in user_info.get(
            'UserAttributes') if data.get('Name') == 'email'][0]

        user_obj = User.get_by_email(user_email)
        if user_obj is None:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_DETAILS_NOT_FOUND.value, data=None,
                                      error=None)

        data = request.get_json(force=True)
        field_types = {'legal_name': str, 'display_name': str, 'postal_code': str,
                       'address': str, 'city': str, 'state': str, 'country': str, 'vat_percentage': str}
        required_fields = ['legal_name', 'display_name', 'postal_code',
                           'address', 'city', 'state', 'country']
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

        account = Account.get_by_uuid(account_uuid)
        if account is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                      error=None)

        account.legal_name = data.get('legal_name')
        account.display_name = data.get('display_name')
        account.postal_code = data.get('postal_code')
        account.address = data.get('address')
        account.city = data.get('city')
        account.state = data.get('state')
        account.country = data.get('country')
        account.currency_code = CurrencyCode.get(data.get('country'))
        account.vat_percentage = data.get('vat_percentage')

        Account.update()

        if account is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

        default_client = Client.get_default_account_client(
            account_uuid=account_uuid)
        if default_client is None:
            legal_name_slug = slugify(data.get('legal_name'))
            client_data = {
                'uuid': Client.create_uuid(),
                'account_uuid': account_uuid,
                'created_by': user_obj.uuid,
                'legal_name': data.get('legal_name'),
                'legal_name_slug': legal_name_slug,
                'display_name': data.get('display_name'),
                'email': user_obj.email.lower(),
                'phone': user_obj.mobile_number,
                'street_name': data.get('address'),
                'postal_code': data.get('postal_code'),
                'city': data.get('city'),
                'state': data.get('state'),
                'country': data.get('country'),
                'is_account_client': True
            }
            client = Client.add(client_data)

            signee_data = {
                'uuid': Signee.create_uuid(),
                'client_uuid': client.uuid,
                'account_uuid': account_uuid,
                'created_by': user_obj.uuid,
                'full_name': user_obj.first_name + ' ' + user_obj.last_name,
                'job_title': None,
                'email': user_obj.email.lower(),
                'signing_sequence': None
            }
            Signee.add(signee_data)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                  error=None)

    @classmethod
    def delete(cls, account_uuid: str):
        """
            API to request account deletion.
        """
        user_obj = AccountView.get_logged_in_user(request=request)
        if user_obj.user_type == UserType.SECONDARY_USER.value:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.NOT_ALLOWED.value, data=None,
                                      error=None)

        account_obj = Account.get_by_uuid(account_uuid)
        if account_obj is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                      error=None)

        delete_date = datetime.combine(datetime.now().date() + timedelta(days=DEFAULT_PRE_DELETION_PERIOD_IN_DAYS), datetime.min.time()).date()  # noqa: FKA100
        account_obj.deletion_scheduled_at = int(
            datetime.combine(delete_date, datetime.min.time()).timestamp())   # noqa: FKA100
        account_obj.deactivated_at = datetime.utcnow()
        Account.update()
        primary_user_obj = User.get_primary_user_of_account(account_uuid)

        """ Send email notification to the account owner regarding the deletion request initiation of the account"""
        email_data = {
            'email_to': primary_user_obj.email,
            'subject': EmailSubject.ACCOUNT_DELETION_REQUEST_INTIATED.value,
            'template': 'emails/account_deletion_request_initiated.html',
            'email_type': EmailTypes.ACCOUNT_DELETION_REQUEST_INTIATED.value,
            'org_id': account_uuid,
            'email_data': {
                'acount_name': account_obj.legal_name,
                'delete_period': DEFAULT_PRE_DELETION_PERIOD_IN_DAYS,
                'account_legal_name': account_obj.legal_name,
                'account_email': primary_user_obj.email,
                'deletion_date': delete_date,
            }
        }

        EmailWorker.send(email_data)

        user_objs = User.get_all_user_by_account_uuid(account_uuid)
        usernames = []
        for user_obj in user_objs:
            usernames.append(user_obj.email)

        """Disabling users from cognito"""
        UserView.disable_users_from_cognito_pool(usernames)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.ACCOUNT_DELETION_REQUEST_ADDED_SUCCESSFULLY.value, data=None,
                                  error=None)

    @classmethod
    def delete_scheduled_accounts(cls):
        """
            Delete the accounts and users of that account from cognito.
        """
        logger.info('Started delete_scheduled_accounts')
        account_objs = Account.get_delete_scheduled_accounts()
        for account in account_objs:
            logger.info(f'Started deletion for account  -> {account.uuid}')

            account_obj = account
            account_uuid = account_obj.legal_name
            account_lgeal_name = account_obj.legal_name

            """
                1. Delete all the user of tha account from cognito
                2. Delete the account and the following related models with CASCADE deletion:
                    - Branding: Deletes branding records associated with the account.
                    - Client: Deletes client records associated with the account.
                    - Contract: Deletes contract records associated with the account.
                    - Contract Log: Deletes contract log records associated with the account.
                    - Contract Signee: Deletes contract signee records associated with the account.
                    - Folder: Deletes folder records associated with the account.
                    - Payment: Deletes payment records associated with the account.
                    - Signee: Deletes signee records associated with the account.
                    - Subscription: Deletes subscription records associated with the account.
                    - Template: Deletes template records associated with the account.
                    - User: Deletes user records associated with the account.
                    - User Invite: Deletes user invite records associated with the account.

                    Note: The CASCADE deletion ensures that when an account is deleted, all associated records in these models will be automatically deleted.
            """
            user_objs = User.get_all_user_by_account_uuid(account_obj.uuid)

            usernames = []
            for user_obj in user_objs:
                usernames.append(user_obj.email)

            """Deleting users from cognito"""
            UserView.delete_users_from_cognito(usernames)

            primary_user_obj = User.get_primary_user_of_account(
                account_obj.uuid)

            """Deleting account"""
            Account.delete_by_uuid(account_obj.uuid)

            # Convert timestamp to datetime object
            dt_object = datetime.utcfromtimestamp(
                account_obj.deletion_scheduled_at)

            # Format datetime object as a string
            formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S UTC')

            email_data = {
                'email_to': primary_user_obj.email,
                'subject': EmailSubject.ACCOUNT_DELETION_CONFIRMATION.value,
                'template': 'emails/account_deletion_confirmation.html',
                'email_type': EmailTypes.ACCOUNT_DELETION_CONFIRMATION.value,
                'org_id': account_uuid,
                'email_data': {
                    'acount_name': account_lgeal_name,
                    'account_legal_name': account_lgeal_name,
                    'account_email': primary_user_obj.email,
                    'deletion_date': formatted_date
                }
            }

            EmailWorker.send(email_data)
