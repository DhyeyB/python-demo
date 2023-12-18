"""This file used to define custom commands.
    ex. python manage.py seed_default_category
"""
from app import app
from app import COGNITO_CLIENT
from app import config_data
from app import db
from app import logger
from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import UserType
from app.models.account import Account
from app.models.user import User
import click
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from flask_script import Manager
from werkzeug.security import generate_password_hash

migrate = Migrate(app=app, db=db)
# keeps track of all the commands and handles how they are called from the command line
manager = Manager(app)
manager.add_command('db', MigrateCommand)  # type: ignore  # noqa: FKA100

logger.info('Manage.py :: Create Commands')


@manager.command
def create_admin():
    """This command is used for creating first user(admin)."""
    try:
        user_details = User.get_by_email(
            config_data['ADMIN']['PRIMARY_EMAIL'])

        if user_details:
            logger.info('User already exists!')
            return None

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
        logger.info('Create Admin :: Account added with {}.'.format(
            config_data['ADMIN']['PRIMARY_EMAIL']))
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
            return None

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

        click.echo(ResponseMessageKeys.ADMIN_USER_ADDED_SUCCESSFULLY.value)

    except COGNITO_CLIENT.exceptions.UsernameExistsException as exception_error:
        raise click.UsageError('\n{}:{}'.format(
            ResponseMessageKeys.EMAIL_ALREADY_EXIST.value.format(
                config_data['ADMIN']['PRIMARY_EMAIL']),
            exception_error))

    except Exception as exception_error:
        raise click.UsageError('\n{}:{}'.format(
            ResponseMessageKeys.FAILED.value, exception_error))


if __name__ == '__main__':
    manager.run()
