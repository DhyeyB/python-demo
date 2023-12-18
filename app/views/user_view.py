"""Contains user related API definitions."""
from datetime import datetime

from app import COGNITO_CLIENT
from app import config_data
from app import logger
from app.helpers.constants import EmailSubject
from app.helpers.constants import EmailTypes
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import UserType
from app.helpers.utility import field_type_validator, get_pagination_meta
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.helpers.utility import validate_email, generate_temporary_password
from app.models.account import Account
from app.models.user import User
from app.views.base_view import BaseView
from flask import request
from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash
from workers.email_worker import EmailWorker
import urllib
from app.helpers.utility import add_email_template
from app.helpers.constants import SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE, CONTRACT_CANCELLED, CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE, SEND_REMINDER_TO_SIGNEE


class UserView(BaseView):
    @classmethod
    def authenticate(cls):
        """ Authenticate user and return token """
        try:
            data = request.get_json(force=True)

            # Data Validation
            field_types = {'email': str, 'password': str}
            required_fields = ['email', 'password']

            post_data = field_type_validator(
                request_data=data, field_types=field_types)

            if post_data['is_error']:
                return send_json_response(
                    http_status=HttpStatusCode.BAD_REQUEST.value,
                    response_status=False,
                    message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value,
                    error=post_data['data'],
                )

            # Check Required Field
            is_valid = required_validator(
                request_data=data, required_fields=required_fields
            )

            if is_valid['is_error']:
                return send_json_response(
                    http_status=HttpStatusCode.BAD_REQUEST.value,
                    response_status=False,
                    message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value,
                    error=is_valid['data'],
                )

            email = data.get('email')
            password = data.get('password')

            # Check if valid Input
            if not validate_email(data.get('email')):
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value,
                                          response_status=False,
                                          message_key=ResponseMessageKeys.INVALID_EMAIL_FORMAT.value,
                                          data=None,
                                          error=None)

            cognito_auth_token = UserView._get_token_by_cognito(
                email_id=email, password=password)

            return send_json_response(
                http_status=200,
                response_status=True,
                message_key=ResponseMessageKeys.LOGIN_SUCCESSFULLY.value,
                data={'auth_token': cognito_auth_token},
            )

        except Exception as exception_error:
            logger.error(f'POST -> User Login Failed: {exception_error}')
            return send_json_response(
                http_status=500,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
            )

    @classmethod
    def create_user(cls):
        data = request.get_json(force=True)
        field_types = {'first_name': str, 'last_name': str,
                       'email': str, 'password': str, 'mobile_number': str}
        required_fields = ['first_name', 'last_name',
                           'email', 'password', 'mobile_number']
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

        email = data.get('email').lower()
        is_email_exist = User.get_by_email(email=email)

        if is_email_exist:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.EMAIL_ALREADY_EXIST.value.format(email), data=None,
                                      error=None)

        account_uuid = Account.create_uuid()
        account_data = {
            'uuid': account_uuid,
            'legal_name': '',
            'display_name': '',
            'vat_percentage': '',
            'address': '',
            'postal_code': '',
            'city': '',
            'state': '',
            'country': ''
        }
        account = Account.add(account_data)
        if account is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_CREATION_FAILED.value, data=None,
                                      error=None)

        user_uuid = User.create_uuid()
        user_data = {
            'uuid': user_uuid,
            'account_uuid': account.uuid,
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': email,
            'force_password_update': False,
            'password': generate_password_hash(data.get('password')),
            'mobile_number': data.get('mobile_number'),
            'user_type': UserType.PRIMARY_USER.value
        }
        user = User.add(user_data)
        if user is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

        password = data.get('password')

        cognito_user, message = UserView.add_user_in_cognito_pool(
            email_id=email, password=password)

        if cognito_user is None:
            User.delete_by_id(user.id)
            Account.delete_by_id(account.id)
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=message, data=None,
                                      error=None)

        # Add predefined email templates for new account
        add_email_template(account_uuid=account.uuid, email_type=EmailTypes.SEND_CONTRACT_TO_SIGNEE.value,
                           email_subject=EmailSubject.SEND_CONTRACT_TO_SIGNEE.value, email_body=SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE)
        add_email_template(account_uuid=account.uuid, email_type=EmailTypes.CONTRACT_CANCELLED.value,
                           email_subject=EmailSubject.CONTRACT_CANCELLED.value, email_body=CONTRACT_CANCELLED)
        add_email_template(account_uuid=account.uuid, email_type=EmailTypes.CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE.value,
                           email_subject=EmailSubject.CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE.value, email_body=CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE)
        add_email_template(account_uuid=account.uuid, email_type=EmailTypes.SEND_REMINDER_TO_SIGNEE.value,
                           email_subject=EmailSubject.SEND_REMINDER_TO_SIGNEE.value, email_body=SEND_REMINDER_TO_SIGNEE)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.REGISTER_SUCCESSFULLY.value, data=None,
                                  error=None)

    @classmethod
    def list(cls):
        """Return list of Users along with Account data according to given page, size, sort and q(filter query)."""
        user_obj = UserView.get_logged_in_user(request=request)

        if user_obj.user_type != UserType.SUPER_ADMIN.value:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.NOT_ALLOWED.value, data=None,
                                      error=None)
        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        users_objs, objects_count = User.get_users_with_account_legal_name(
            q=q, sort=sort, page=page, size=size)
        users_list = [row._asdict() for row in users_objs]

        data = {'result': users_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=int(size), total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_user_by_uuid(cls, user_uuid: str):
        user = User.get_by_uuid(user_uuid)
        if user is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_NOT_FOUND.value, data=None,
                                      error=None)

        user_data = User.serialize(user)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=user_data,
                                  error=None)

    @classmethod
    def update_user(cls, user_uuid: str):
        data = request.get_json(force=True)
        field_types = {'first_name': str,
                       'last_name': str, 'mobile_number': str}
        required_fields = ['first_name', 'last_name', 'mobile_number']
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

        user = User.get_by_uuid(user_uuid)
        if user is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_NOT_FOUND.value, data=None,
                                      error=None)

        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.mobile_number = data.get('mobile_number')
        User.update()

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.UPDATED_SUCCESSFULLY.value, data=None,
                                  error=None)

    @classmethod
    def add_user_in_cognito_pool(cls, email_id=None, password=None):
        try:
            # Add User in Cognito User Pool
            cognito_user = COGNITO_CLIENT.sign_up(
                ClientId=config_data.get('COGNITO_APP_CLIENT_ID'),
                Username=email_id,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email_id
                    }
                ],
                ValidationData=[
                    {
                        'Name': 'email',
                        'Value': email_id
                    }
                ]
            )

            logger.info(
                f'Cognito -> User "{email_id}" Is Added To Cognito User Pool and Email Verification Sent.'
            )
            message = f'Cognito -> User "{email_id}" Is Added To Cognito User Pool and Email Verification Sent.'
            user = cognito_user

        except COGNITO_CLIENT.exceptions.CodeDeliveryFailureException as exception_error:
            logger.error(
                f'{exception_error}')
            message = ResponseMessageKeys.FAILED.value
            cls.disable_users_from_cognito_pool(usernames=[email_id])
            cls.delete_users_from_cognito(usernames=[email_id])
            user = None

        except COGNITO_CLIENT.exceptions.UsernameExistsException as exception_error:
            logger.error(
                f'Cognito -> Failed To Add User "{email_id}" To Cognito User Pool  {exception_error}')
            message = ResponseMessageKeys.USER_ALREADY_EXISTS.value
            user = None

        except Exception as exception_error:
            logger.error(
                f'Cognito -> Failed To Add User "{email_id}" To Cognito User Pool {exception_error}.')
            message = ResponseMessageKeys.FAILED.value
            user = None
        return user, message

    @classmethod
    def add_user_with_verified_mail_in_cognito_pool(cls, email_id=None, password=None):
        try:
            if email_id and password:
                # Add User with verified email in Cognito User Pool
                cognito_user = COGNITO_CLIENT.admin_create_user(
                    UserPoolId=config_data.get('COGNITO_USER_POOL_ID'),
                    Username=email_id,
                    UserAttributes=[
                        {'Name': 'email', 'Value': email_id},
                        {'Name': 'email_verified', 'Value': 'true'}
                    ],
                    ForceAliasCreation=True,
                    MessageAction='SUPPRESS',
                    DesiredDeliveryMediums=[
                        'EMAIL',
                    ],
                )
                logger.info('Create Admin :: User added in Cognito.')

                # Set User Password
                COGNITO_CLIENT.admin_set_user_password(
                    UserPoolId=config_data.get('COGNITO_USER_POOL_ID'),
                    Username=email_id,
                    Password=password,
                    Permanent=True | False,
                )
                logger.info(
                    'Create Admin :: User password updated in Cognito.')

                logger.info(
                    f'Cognito -> User "{email_id}" Is Added To Cognito User Pool'
                )
                return cognito_user

            else:
                logger.info(
                    'Cognito -> Failed To Add User To Cognito User Pool: Invalid Username/Password.'
                )
                return None

        except Exception as exception_error:
            logger.error(
                f'Cognito -> Failed To Add User "{email_id}" To Cognito User Pool {exception_error}.'
            )
            return None

    @classmethod
    def confirm_verification_code(cls):
        data = request.get_json(force=True)
        field_types = {'email': str, 'verification_code': str}
        required_fields = ['email', 'verification_code']
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

        email = data.get('email')
        verification_code = data.get('verification_code')

        user = User.get_by_email(email)
        if not user:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_NOT_EXIST.value, data=None,
                                      error=None)

        email_verified = user.email_verified_at
        if email_verified:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_ALREADY_CONFIRMED.value, data=None,
                                      error=None)

        current_datetime = datetime.now()
        try:
            # Confirm user sign-up
            COGNITO_CLIENT.confirm_sign_up(
                ClientId=config_data.get('COGNITO_APP_CLIENT_ID'),
                Username=email,
                ConfirmationCode=verification_code
            )

            user = User.get_by_email(email)
            user.email_verified_at = current_datetime
            User.update()

            logger.info(
                f'Cognito -> User "{email}" Is Verified Successfully.'
            )

            email_data = {
                'email_to': email,
                'subject': EmailSubject.WELCOME.value,
                'template': 'emails/welcome.html',
                'email_type': EmailTypes.WELCOME.value,
                'org_id': user.account_uuid,
                'email_data': {
                    'first_name': user.first_name
                }
            }

            EmailWorker.send(email_data)

            user_data = User.serialize(user, single_object=True)

            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.USER_VERIFICATION_SUCCESS.value, data=user_data,
                                      error=None)

        except COGNITO_CLIENT.exceptions.UserNotFoundException:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_NOT_EXIST.value, data=None,
                                      error=None)
        except COGNITO_CLIENT.exceptions.CodeMismatchException:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_VERIFICATION_CONFIRMED.value, data=None,
                                      error=None)
        except COGNITO_CLIENT.exceptions.NotAuthorizedException:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_ALREADY_CONFIRMED.value, data=None,
                                      error=None)
        except Exception as exception_error:
            logger.error(
                f'POST -> Confirm user verification code failed: {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.UNKNOWN_ERROR.value, data=None,
                                      error=None)

    @classmethod
    def resend_verification_code(cls):
        data = request.get_json(force=True)
        field_types = {'email': str}
        required_fields = ['email']
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

        email = data.get('email')
        if not validate_email(email):
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, data=None,
                                      error=None)

        user = User.get_by_email(email)
        if not user:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_NOT_EXIST.value, data=None,
                                      error=None)

        email_verified = user.email_verified_at
        if email_verified:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_ALREADY_CONFIRMED.value, data=None,
                                      error=None)
        else:
            try:
                COGNITO_CLIENT.resend_confirmation_code(
                    ClientId=config_data.get('COGNITO_APP_CLIENT_ID'),
                    Username=email,
                )
            except COGNITO_CLIENT.exceptions.UserNotFoundException:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.USER_NOT_EXIST.value, data=None,
                                          error=None)

            except Exception as exception_error:
                logger.error(
                    f'Cognito -> {exception_error}.'
                )
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.UNKNOWN_ERROR.value, data=None,
                                          error=None)

            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.VERIFICATION_CODE_RESEND_SUCCESS.value, data=None,
                                      error=None)

    @classmethod
    def get_user_by_token(cls):
        try:
            authorization_header = request.headers.get('Authorization')
            access_token = authorization_header.replace('Bearer ', '').strip()
            if access_token:
                user_info = COGNITO_CLIENT.get_user(AccessToken=access_token)
            else:
                return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False, message_key=ResponseMessageKeys.UNKNOWN_ERROR.value, data=None, error=None)

            user_email = [data.get('Value') for data in user_info.get(
                'UserAttributes') if data.get('Name') == 'email'][0]

            user_object = User.get_by_email(user_email)

            user_data = User.serialize(user_object, single_object=True)
            if user_object is None:
                return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False, message_key=ResponseMessageKeys.USER_DETAILS_NOT_FOUND.value, data=None, error=None)

            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.SUCCESS.value, data=user_data,
                                      error=None)

        except Exception as exception_error:
            logger.error(f'Get User Failed: {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.UNKNOWN_ERROR.value, data=None,
                                      error=None)

    @classmethod
    def create_admin(cls):
        try:
            user_details = User.get_by_email(
                config_data['ADMIN']['PRIMARY_EMAIL'])
            if user_details:
                logger.info('User already exists!')
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.EMAIL_ALREADY_EXIST.value.format(config_data['ADMIN']['PRIMARY_EMAIL']), data=None,
                                          error=None)

            account_uuid = Account.create_uuid()

            account_data = {
                'uuid': account_uuid,
                'legal_name': '',
                'display_name': '',
                'vat_percentage': '',
                'address': '',
                'postal_code': '',
                'city': '',
                'state': '',
                'country': ''
            }

            account = Account.add(account_data)
            if account is None:
                logger.info('Create Admin :: Account added with {}.'.format(
                    config_data['ADMIN']['PRIMARY_EMAIL']))
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.USER_CREATION_FAILED.value, data=None,
                                          error=None)

            user_uuid = User.create_uuid()
            user_data = {
                'uuid': user_uuid,
                'account_uuid': account.uuid,
                'first_name': config_data['ADMIN']['FIRST_NAME'],
                'last_name': config_data['ADMIN']['LAST_NAME'],
                'email': config_data['ADMIN']['PRIMARY_EMAIL'],
                'force_password_update': False,
                'password': generate_password_hash(config_data['ADMIN']['PASSWORD']),
                'mobile_number': config_data['ADMIN']['MOBILE_NUMBER'],
                'user_type': UserType.SUPER_ADMIN.value
            }

            user = User.add(user_data)
            logger.info('Create Admin :: User added in DB.')
            if user is None:
                logger.error(
                    'Could not create user in database. Please check the input.')
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.FAILED.value, data=None,
                                          error=None)

            # Add User in Cognito User Pool
            COGNITO_CLIENT.admin_create_user(
                UserPoolId=config_data.get('COGNITO_USER_POOL_ID'),
                Username=config_data['ADMIN']['PRIMARY_EMAIL'],
                UserAttributes=[
                    {'Name': 'email',
                        'Value': config_data['ADMIN']['PRIMARY_EMAIL']},
                    {'Name': 'email_verified', 'Value': 'true'}
                ],
                ForceAliasCreation=True,
                MessageAction='SUPPRESS',
                DesiredDeliveryMediums=[
                    'EMAIL',
                ],
            )
            logger.info('Create Admin :: User added in Cognito.')

            # Set User Password
            COGNITO_CLIENT.admin_set_user_password(
                UserPoolId=config_data.get('COGNITO_USER_POOL_ID'),
                Username=config_data['ADMIN']['PRIMARY_EMAIL'],
                Password=config_data['ADMIN']['PASSWORD'],
                Permanent=True | False,
            )
            logger.info('Create Admin :: User password updated in Cognito.')

            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.ADMIN_REGISTER_SUCCESSFULLY.value, data=None,
                                      error=None)

        except COGNITO_CLIENT.exceptions.UsernameExistsException as exception_error:
            logger.error(exception_error)
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.EMAIL_ALREADY_EXIST.value.format(config_data['ADMIN']['PRIMARY_EMAIL']), data=None,
                                      error=None)

        except Exception as exception_error:
            User.delete_by_id(user.id)
            Account.delete_by_id(account.id)
            logger.error(f'Get User Failed: {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

    @classmethod
    def _get_token_by_cognito(cls, email_id: str, password: str):
        try:
            if email_id and password:
                auth_token = (
                    COGNITO_CLIENT.initiate_auth(
                        AuthFlow='USER_PASSWORD_AUTH',
                        AuthParameters={
                            'USERNAME': email_id,
                            'PASSWORD': password,
                        },
                        ClientId=config_data.get('COGNITO_APP_CLIENT_ID'),
                    )
                    .get('AuthenticationResult')
                    .get('AccessToken')
                )

                return auth_token

            else:
                logger.error('Email id or password not found')
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.LOGIN_FAILED.value, data=None,
                                          error=None)

        except COGNITO_CLIENT.exceptions.UserNotFoundException as exception_error:
            logger.error(
                f'POST -> User Not Registered: {exception_error}')
            return send_json_response(
                http_status=HttpStatusCode.BAD_REQUEST.value,
                response_status=False,
                message_key=ResponseMessageKeys.USER_NOT_EXIST.value,
            )

        except AttributeError as exception_error:
            logger.error(
                f'POST -> User Not Confirmed: {exception_error}')
            return send_json_response(
                http_status=HttpStatusCode.BAD_REQUEST.value,
                response_status=False,
                message_key=ResponseMessageKeys.USER_NOT_CONFIRMED.value,
            )

        except COGNITO_CLIENT.exceptions.NotAuthorizedException as exception_error:
            logger.error(
                f'POST -> Auth Token Generation Failed: {exception_error}')
            return send_json_response(
                http_status=HttpStatusCode.BAD_REQUEST.value,
                response_status=False,
                message_key=ResponseMessageKeys.LOGIN_FAILED.value,
            )

        except BadRequest as exception_error:
            logger.error(f'POST -> User Login Failed: {exception_error}')
            return send_json_response(
                http_status=HttpStatusCode.BAD_REQUEST.value,
                response_status=False,
                message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value,
            )

        except Exception as exception_error:
            logger.error(f'POST -> User Login Failed: {exception_error}')
            return send_json_response(
                http_status=500,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
            )

    @classmethod
    def google_login(cls):
        """ Initiate Google login url """
        try:
            logger.info('Initiate Google login')
            # The OAuth response type, which can be code for code grant flow and token for implicit flow.
            response_type = 'token'
            client_id = config_data.get('COGNITO_APP_CLIENT_ID')
            auth_url = config_data.get('COGNITO_DOMAIN_URL')
            # Cognito will send details on this url
            redirect_uri = config_data.get('COGNITO_IDP_CALLBACK_URL')
            identity_provider = 'Google'
            scope = 'aws.cognito.signin.user.admin email openid profile'
            authorization_uri = f'{auth_url}/oauth2/authorize?identity_provider={identity_provider}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type={response_type}&client_id={client_id}&scope={scope}'

            logger.info(f'Initiate Google login url: {authorization_uri}')

            return send_json_response(
                http_status=200,
                response_status=True,
                message_key=ResponseMessageKeys.SUCCESS.value,
                data={'authorization_uri': authorization_uri},
            )

        except Exception as exception_error:
            logger.error(f'Google app authorisation failed: {exception_error}')
            return send_json_response(
                http_status=500,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
            )

    @classmethod
    def idp_callback(cls):
        """ Fetch user details by token sent by amazon cognito for IDP """
        try:
            data = request.get_json(force=True)
            field_types = {'access_token': str}
            required_fields = ['access_token']
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

            access_token = data.get('access_token')

            logger.info('access_token')
            logger.info(access_token)

            response = COGNITO_CLIENT.get_user(
                AccessToken=access_token
            )

            logger.info('cognito response for access token')
            logger.info(response)

            if response:
                # Extract the desired user attributes
                first_name = None
                last_name = None
                email = None
                for attr in response['UserAttributes']:
                    if attr['Name'] == 'given_name':
                        first_name = attr['Value']
                    if attr['Name'] == 'family_name':
                        last_name = attr['Value']
                    if attr['Name'] == 'email':
                        email = attr['Value']

                user_obj = User.get_by_email(email)
                logger.info('user_obj')
                logger.info(user_obj)
                data = {
                    'token': access_token
                }
                if not user_obj:
                    """ Sync user in local db from cognito """
                    logger.info('Sync user in local db from cognito ')
                    account_uuid = Account.create_uuid()

                    account_data = {
                        'uuid': account_uuid,
                        'legal_name': '',
                        'display_name': '',
                        'vat_percentage': '',
                        'address': '',
                        'postal_code': '',
                        'city': '',
                        'state': '',
                        'country': ''
                    }

                    account = Account.add(account_data)
                    if account is None:
                        return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                                  message_key=ResponseMessageKeys.USER_CREATION_FAILED.value, data=None,
                                                  error=None)

                    user_uuid = User.create_uuid()
                    temp_password = generate_temporary_password()
                    user_data = {
                        'uuid': user_uuid,
                        'account_uuid': account.uuid,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'force_password_update': False,
                        'password': temp_password,
                        'user_type': UserType.PRIMARY_USER.value
                    }

                    user = User.add(user_data)
                    if user is None:
                        return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                                  message_key=ResponseMessageKeys.FAILED.value, data=None,
                                                  error=None)

                    logger.info('User created')

                    email_data = {
                        'email_to': email,
                        'subject': EmailSubject.WELCOME.value,
                        'template': 'emails/welcome.html',
                        'email_type': EmailTypes.WELCOME.value,
                        'org_id': account.uuid,
                        'email_data': {
                            'first_name': first_name
                        }
                    }

                    EmailWorker.send(email_data)
                    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                              message_key=ResponseMessageKeys.LOGIN_SUCCESSFULLY.value, data=data,
                                              error=None)

                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.LOGIN_SUCCESSFULLY.value, data=data,
                                          error=None)

            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_TOKEN.value,
                                      data=None,
                                      error=None)

        except Exception as exception_error:
            logger.error(
                f'Google app authorisation callback failed: {exception_error}')
            return send_json_response(
                http_status=500,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
            )

    @classmethod
    def idp_logout(cls):
        """ Logout url for IDP """
        try:
            # The OAuth response type, which can be code for code grant flow and token for implicit flow.
            response_type = 'token'
            client_id = config_data.get('COGNITO_APP_CLIENT_ID')
            auth_url = config_data.get('COGNITO_DOMAIN_URL')
            # Cognito will send details on this url
            redirect_uri = config_data.get('COGNITO_IDP_CALLBACK_URL')

            scope = 'aws.cognito.signin.user.admin openid phone profile'

            logout_uri = f'{auth_url}/logout?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}'
            return send_json_response(
                http_status=200,
                response_status=True,
                message_key=ResponseMessageKeys.LOGOUT_SUCCESSFULLY.value,
                data={'logout_uri': logout_uri},
            )

        except Exception as exception_error:
            logger.error(f'Google app authorisation failed: {exception_error}')
            return send_json_response(
                http_status=500,
                response_status=False,
                message_key=ResponseMessageKeys.FAILED.value,
            )

    @classmethod
    def email_verification(cls):
        """Verify code for new email - Update user profile feature"""
        data = request.get_json(force=True)
        field_types = {'new_email': str,
                       'old_email': str, 'verification_code': str}
        required_fields = ['new_email', 'old_email', 'verification_code']
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

        new_email = data.get('new_email').lower()
        old_email = data.get('old_email').lower()
        if not validate_email(new_email):
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_EMAIL_FORMAT.value + new_email, data=None,
                                      error=None)
        if not validate_email(old_email):
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_EMAIL_FORMAT.value + old_email, data=None,
                                      error=None)

        verification_code = data.get('verification_code')

        user = User.get_by_email(old_email)
        if not user:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_NOT_EXIST.value, data=None,
                                      error=None)

        try:
            # Confirm user sign-up
            COGNITO_CLIENT.confirm_sign_up(
                ClientId=config_data.get('COGNITO_APP_CLIENT_ID'),
                Username=new_email,
                ConfirmationCode=verification_code
            )
        except COGNITO_CLIENT.exceptions.UserNotFoundException:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_NOT_EXIST.value, data=None,
                                      error=None)
        except COGNITO_CLIENT.exceptions.CodeMismatchException:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_VERIFICATION_CONFIRMED.value, data=None,
                                      error=None)
        except COGNITO_CLIENT.exceptions.NotAuthorizedException:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_ALREADY_CONFIRMED.value, data=None,
                                      error=None)
        except Exception as exception_error:
            logger.error(
                f'POST -> Confirm user verification code failed: {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.UNKNOWN_ERROR.value, data=None,
                                      error=None)

        user.email = new_email
        User.update()

        try:
            authorization_header = request.headers.get('Authorization')
            access_token = authorization_header.replace('Bearer ', '').strip()
            COGNITO_CLIENT.delete_user(
                AccessToken=access_token
            )
        except COGNITO_CLIENT.exceptions.UserNotFoundException:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.USER_NOT_EXIST.value, data=None,
                                      error=None)
        except Exception as exception_error:
            logger.error(
                f'POST -> Confirm user verification code failed: {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.UNKNOWN_ERROR.value, data=None,
                                      error=None)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.EMAIL_UPDATED_SUCCESSFULLY.value, data=None,
                                  error=None)

    @staticmethod
    def disable_users_from_cognito_pool(usernames):
        """ Disable users for cognito pool """
        for username in usernames:
            logger.info(f'Disabling user {username} from cognito')
            try:
                COGNITO_CLIENT.admin_disable_user(
                    UserPoolId=config_data.get('COGNITO_USER_POOL_ID'),
                    Username=username
                )

                logger.info(
                    f'Cognito Accounto  -> User Account "{username}" Deactivated.'
                )

            except Exception as exception_error:
                logger.error(
                    f'Cognito Account -> User Account "{username}" Deactivated Failed: {exception_error}'
                )

    @staticmethod
    def delete_users_from_cognito(usernames):
        """ Delete users for cognito pool """
        for username in usernames:
            logger.info(f'Deleting user {username} from cognito')
            try:
                COGNITO_CLIENT.admin_delete_user(
                    UserPoolId=config_data.get('COGNITO_USER_POOL_ID'),
                    Username=username
                )

                logger.info(
                    f'Cognito Account -> User Account "{username}" Deleted.'
                )

            except Exception as exception_error:
                logger.error(
                    f'Cognito Account -> User Account "{username}" Delete Failed: {exception_error}'
                )
