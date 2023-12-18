from datetime import datetime
from datetime import timezone

from app import config_data
from app import logger
from app.helpers.constants import EmailSubject
from app.helpers.constants import EmailTypes
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import UserInviteStatusTypes
from app.helpers.constants import UserType
from app.helpers.utility import field_type_validator
from app.helpers.utility import generate_email_token
from app.helpers.utility import get_pagination_meta
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.helpers.utility import validate_email
from app.models.account import Account
from app.models.user import User
from app.models.user_invite import UserInvite
from app.views import UserView
from app.views.base_view import BaseView
from flask import request
import jwt
from werkzeug.security import generate_password_hash
from workers.email_worker import EmailWorker


class UserInviteView(BaseView):
    @classmethod
    def send_invite(cls):
        """ Send user invite """
        try:
            data = request.get_json(force=True)
            field_types = {'first_name': str, 'last_name': str, 'email': str}
            required_fields = ['first_name', 'last_name', 'email']
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

            is_email_exist = User.get_by_email(data.get('email'))

            if is_email_exist:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.EMAIL_ALREADY_EXIST.value.format(data.get('email')), data=None,
                                          error=None)

            user_obj = UserInviteView.get_logged_in_user(request=request)
            invited_user_email = data.get('email')
            first_name = data.get('first_name')
            last_name = data.get('last_name')

            user_invite_uuid = UserInvite.create_uuid()

            user_invite_data = {
                'uuid': user_invite_uuid,
                'user_invited_by': user_obj.uuid,
                'account_uuid': user_obj.account_uuid,
                'first_name': first_name,
                'last_name': last_name,
                'email': invited_user_email,
                'status': UserInviteStatusTypes.PENDING.value
            }

            user_invite = UserInvite.add(user_invite_data)
            if user_invite is None:
                logger.error('POST -> User Invitation Failed')
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.FAILED.value, data=None,
                                          error=None)

            email_token = generate_email_token(user_invite.uuid)
            token_link = config_data.get(
                'APP_URL') + '/user-invite/set-password?token=' + email_token
            account = Account.get_by_uuid(user_obj.account_uuid)
            if account is None:
                logger.error('POST -> User Invitation Failed')
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                          error=None)

            email_data = {
                'email_to': invited_user_email,
                'subject': EmailSubject.USER_INVITE.value,
                'template': 'emails/user_invite.html',
                'email_type': EmailTypes.INVITE.value,
                'org_id': user_obj.account_uuid,
                'email_data': {
                    'first_name': first_name,
                    'invite_link': token_link,
                    'legal_name': account.legal_name
                }
            }

            EmailWorker.send(email_data)
            logger.info('POST -> User invitation successfull')
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.SEND_USER_INVITE_SUCCESS.value, data=None,
                                      error=None)

        except AttributeError as exception_error:
            logger.error(f'POST -> User Invitation Failed: {exception_error}')
            return send_json_response(
                http_status=HttpStatusCode.BAD_REQUEST.value,
                response_status=False,
                message_key=ResponseMessageKeys.SEND_USER_INVITE_FAILED.value,
            )

    @classmethod
    def verify_token(cls):
        """ Authenticate_token """
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
            token_timestamp = token_data['timestamp']

            current_time = datetime.now(timezone.utc)
            token_time = datetime.fromtimestamp(
                token_timestamp, tz=timezone.utc)
            # Calculate the time difference in hours
            time_difference_hours = (
                current_time - token_time).total_seconds() / 3600
            if time_difference_hours < 0:
                invited_user = UserInvite.get_by_uuid(token_data['id'])
                if invited_user is None:
                    return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                              message_key=ResponseMessageKeys.INVALID_TOKEN.value, data=None,
                                              error=None)

                if invited_user.status == UserInviteStatusTypes.ACCEPTED.value:
                    return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                              message_key=ResponseMessageKeys.USER_ALREADY_ACCEPTED_INVITATION.value, data=None,
                                              error=None)

                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.INVITE_TOKEN_VERIFIED_SUCCESSFULLY.value, data=None,
                                          error=None)
            else:
                return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                          message_key=ResponseMessageKeys.TOKEN_EXPIRED.value, data=None,
                                          error=None)

        except Exception as e:
            logger.info('we got exception {}'.format(e))
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_TOKEN.value, data=None,
                                      error=None)

    @classmethod
    def accept_invite(cls):
        """Create Secondary user after invite is accepted"""
        data = request.get_json(force=True)
        field_types = {'password': str, 'token': str}
        required_fields = ['password', 'token']
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
        token_data = jwt.decode(jwt=token, key=config_data.get(
            'SECRET_KEY'), algorithms=['HS256'])
        user_invite_uuid = token_data['id']
        user_invite_obj = UserInvite.get_by_uuid(user_invite_uuid)

        if user_invite_obj is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_INVITE_NOT_FOUND.value, data=None,
                                      error=None)

        if user_invite_obj.status == UserInviteStatusTypes.ACCEPTED.value:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVITE_ALREADY_ACCEPTED.value, data=None,
                                      error=None)

        user_uuid = User.create_uuid()
        user_data = {
            'uuid': user_uuid,
            'account_uuid': user_invite_obj.account_uuid,
            'first_name': user_invite_obj.first_name,
            'last_name': user_invite_obj.last_name,
            'email': user_invite_obj.email,
            'force_password_update': False,
            'password': generate_password_hash(data.get('password')),
            'user_type': UserType.SECONDARY_USER.value
        }
        user = User.add(user_data)

        if user is None:
            user_invite_obj.update_status(
                status=UserInviteStatusTypes.PENDING.value)
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

        email = user_invite_obj.email
        password = data.get('password')

        cognito_user = UserView.add_user_with_verified_mail_in_cognito_pool(
            email_id=email, password=password)

        if cognito_user is None:
            user_invite_obj.update_status(
                status=UserInviteStatusTypes.PENDING.value)
            User.delete_by_uuid(user.uuid)
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.COGNITO_USER_CREATION_FAILED.value, data=None,
                                      error=None)

        user_invite_obj.update_status(
            status=UserInviteStatusTypes.ACCEPTED.value)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.INVITE_ACCEPTED_SUCCESSFULLY.value, data=None,
                                  error=None)

    @classmethod
    def resend_user_invite(cls):
        """ Resend user invite """
        try:
            data = request.get_json(force=True)
            field_types = {'user_invite_uuid': str}
            required_fields = ['user_invite_uuid']
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

            user_invite_uuid = data.get('user_invite_uuid')
            invited_user = UserInvite.get_by_uuid(user_invite_uuid)

            if invited_user is None:
                return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                          message_key=ResponseMessageKeys.USER_INVITE_NOT_FOUND.value, data=None,
                                          error=None)

            if invited_user.status == UserInviteStatusTypes.ACCEPTED.value:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.INVITE_ALREADY_ACCEPTED.value, data=None,
                                          error=None)

            invited_user_email = invited_user.email
            first_name = invited_user.first_name

            email_token = generate_email_token(invited_user.uuid)
            token_link = config_data.get(
                'APP_URL') + '/user-invite/set-password?token=' + email_token
            user_obj = UserInviteView.get_logged_in_user(request=request)
            account = Account.get_by_uuid(user_obj.account_uuid)
            if account is None:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                          error=None)

            email_data = {
                'email_to': invited_user_email,
                'subject': EmailSubject.USER_INVITE.value,
                'template': 'emails/user_invite.html',
                'email_type': EmailTypes.INVITE.value,
                'org_id': user_obj.account_uuid,
                'email_data': {
                    'first_name': first_name,
                    'invite_link': token_link,
                    'legal_name': account.legal_name
                }
            }

            EmailWorker.send(email_data)
            logger.info('POST -> Resend user invitation successfull')
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.RESEND_USER_INVITE_SUCCESS.value, data=None,
                                      error=None)

        except AttributeError as exception_error:
            logger.error(
                f'POST -> Resend user invitation Failed: {exception_error}')
            return send_json_response(
                http_status=HttpStatusCode.BAD_REQUEST.value,
                response_status=False,
                message_key=ResponseMessageKeys.RESEND_USER_INVITE_FAILED.value,
            )

    @classmethod
    def list(cls):
        """
        Get all user_invites belong to the logged-in user's account.
        Return data in a paginated format.
        """
        user_obj = UserInviteView.get_logged_in_user(request=request)

        account_uuid = user_obj.account_uuid
        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        user_invite_objs, objects_count = UserInvite.get_user_invite_list_by_account(
            q=q, sort=sort, page=page, size=size, account_uuid=account_uuid)
        user_invite_list = UserInvite.serialize(user_invite_objs)

        data = {'result': user_invite_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=int(size), total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def delete(cls, uuid):
        """Delete user invite"""
        user_invite_obj = UserInvite.get_by_uuid(uuid=uuid)
        if user_invite_obj is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_INVITE_NOT_FOUND.value, data=None,
                                      error=None)

        UserInvite.delete_by_uuid(uuid=uuid)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.USER_INVITE_DELETED_SUCCESSFULLY.value, data=None,
                                  error=None)
