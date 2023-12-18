"""
    This file contains the configuration of settings and initialization of the testing framework for the project.
"""
import json

from slugify import slugify

from app import app_set_configurations
from app import config_data
from app import db
from app import initialize_extensions
from app import ratelimit_handler
from app import register_blueprints
from app import register_swagger_blueprints
from app.helpers.constants import UserType, SubscriptionStatus
from app.models.account import Account
from app.models.client import Client
from app.models.contact_us import ContactUs
from app.models.plan import Plan
from app.models.signee import Signee
from app.models.subscription import Subscription
from app.models.user import User
from flask import Flask
import pytest
from werkzeug.security import generate_password_hash
from app.models.email_template import EmailTemplate
from app.helpers.constants import EmailSubject, EmailTypes
from app.helpers.constants import SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE, CONTRACT_CANCELLED

"""Sample data values for testing"""
SUPER_ADMIN_FIRST_NAME = 'ADMIN'
SUPER_ADMIN_LAST_NAME = 'USER'
SUPER_ADMIN_PRIMARY_EMAIL = 'adminvs@project.com'
SUPER_ADMIN_PASSWORD = 'Abc@1234'
SUPER_ADMIN_MOBILE_NUMBER = '1000000001'

TEST_USER_FIRST_NAME = 'FARRUKH'
TEST_USER_LAST_NAME = 'JAMAL'
TEST_USER_PRIMARY_EMAIL = 'divyjain161+102@gmail.com'
TEST_USER_PASSWORD = 'Thj@7134'
TEST_USER_MOBILE_NUMBER = '9700000000'

ACCOUNT_LEGAL_NAME = 'Account1'
ACCOUNT_DISPLAY_NAME = 'Account1'

PLAN_NAME = 'Monthly Premium TESTPLAN GBP3'
PLAN_PERIOD = 'month'
PLAN_STATUS = 'active'
PLAN_AMOUNT = '800'
PLAN_DISCOUNT = '10'
PLAN_DESCRIPTION = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
PLAN_FEATURE = [
    {
        'id': '1',
        'feature_name': 'Unlimited access upto 7 users'
    },
    {
        'id': '2',
        'feature_name': 'Unlimited access upto 7 users'
    }
]

CONTACT_US_FIRST_NAME = 'Sam'
CONTACT_US_LAST_NAME = 'Black'
CONTACT_US_EMAIL = 'sam.black@example.com'
CONTACT_US_COMPANY_SIZE = 20
CONTACT_US_COMPANY_NAME = 'SB_Company'
CONTACT_US_MESSAGE = 'Demo Message!'

CLIENT_LEGAL_NAME = 'Edugem'
CLIENT_DISPLAY_NAME = 'Bombay Softwares'
CLIENT_EMAIL = 'b.s@email.com'
CLIENT_PHONE_NUMBER = '987654321'
CLIENT_COMPANY_NAME = 'BS'
CLIENT_STREET_NAME = 'Iscon'
CLIENT_POSTAL_CODE = '380015'
CLIENT_CITY = 'Ahmedabad'
CLIENT_STATE = 'Gujarat'
CLIENT_COUNTRY = 'India'

SIGNEE1_FULL_NAME = 'signee1'
SIGNEE1_EMAIL = 'signee1@email.com'

SIGNEE2_FULL_NAME = 'signee2'
SIGNEE2_EMAIL = 'signee2@email.com'

CONTRACT_PURPOSE = 'Make me a NDA document'
CONTRACT_BRIEF = 'i.e. be their development partner for the corporation Account.'
CONTRACT_SERVICE_NAME = 'Project creation'
CONTRACT_DURATION = 1
CONTRACT_AMOUNT = 10000000000.500
CONTRACT_DEMO_CONTENT = '<!DOCTYPE html><html><head><title>Dummy HTML Text</title></head><body><h1>Hello, World!</h1><p>This is some dummy HTML text.</p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p></body></html>'

TEST_FILE_PATH_PDF = 'tests/assets/demo.pdf'

CANCEL_EMAIL_TEMPLATE_TYPE = EmailTypes.CONTRACT_CANCELLED.value,
CANCEL_EMAIL_TEMPLATE_EMAIL_SUBJECT = EmailSubject.CONTRACT_CANCELLED.value,
CANCEL_EMAIL_TEMPLATE_EMAIL_BODY = CONTRACT_CANCELLED

SEND_CONTRACT_TO_SIGNEEE_EMAIL_TEMPLATE_TYPE = EmailTypes.SEND_CONTRACT_TO_SIGNEE.value,
SEND_CONTRACT_TO_SIGNEEE_EMAIL_TEMPLATE_EMAIL_SUBJECT = EmailSubject.SEND_CONTRACT_TO_SIGNEE.value,
SEND_CONTRACT_TO_SIGNEEE_EMAIL_TEMPLATE_EMAIL_BODY = SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE


@pytest.fixture(scope='session')
def app():
    """
        Initialize the new application instance for the testing with following settings :
            - Default db to test database.
            - Create Schema in the test db as per the models.
            - Yield the application Object.
            - Once test session is ended drop all the tables.
    """

    application = Flask(__name__, instance_relative_config=True)
    application.config.from_object(config_data)

    application.register_error_handler(429, ratelimit_handler)  # type: ignore  # noqa: FKA100
    app_set_configurations(application=application,
                           config_data=config_data)
    application.config.update({
        'TESTING': True,
    })
    config_data.update({
        'TESTING': True,
    })
    application.config.update({
        'SQLALCHEMY_DATABASE_URI': config_data.get('SQLALCHEMY_TEST_DATABASE_URI')
    })

    initialize_extensions(application)
    register_blueprints(application)
    register_swagger_blueprints(application)
    with application.app_context():
        db.create_all()  # creates all the tables

    ctx = application.app_context()
    ctx.push()

    # do the testing
    yield application

    # tear down
    with application.app_context():
        db.session.remove()
        db.drop_all()

    ctx.pop()


@pytest.fixture(scope='session')
def user_client(app):
    """
        This method is being used to fetch the app object to test the admin user test cases.
            - Admin User is created on app object initialization
            - Getting Authenticated
            - Added Auth_token to test_client.
            - At the end of session, User is being deleted from cognito user pool.
    """
    account = Account(uuid=Account.create_uuid(),
                      legal_name='',
                      display_name='',
                      vat_percentage='',
                      address='',
                      postal_code='',
                      city='',
                      state='',
                      country=''
                      )
    db.session.add(account)
    db.session.commit()

    user = User(uuid=User.create_uuid(),
                account_uuid=account.uuid,
                first_name=TEST_USER_FIRST_NAME,
                last_name=TEST_USER_LAST_NAME,
                email=TEST_USER_PRIMARY_EMAIL,
                force_password_update=False,
                password=generate_password_hash(TEST_USER_PASSWORD),
                mobile_number=TEST_USER_MOBILE_NUMBER,
                user_type=UserType.PRIMARY_USER.value
                )
    db.session.add(user)
    db.session.commit()

    plan = Plan(uuid=Plan.create_uuid(),
                name=PLAN_NAME,
                period=PLAN_PERIOD,
                status=PLAN_STATUS,
                amount=PLAN_AMOUNT,
                discount=PLAN_DISCOUNT,
                feature=PLAN_FEATURE,
                description=PLAN_DESCRIPTION
                )
    db.session.add(plan)
    db.session.commit()

    subscription = Subscription(uuid=Subscription.create_uuid(),
                                account_uuid=account.uuid,
                                plan_uuid=plan.uuid,
                                status=SubscriptionStatus.ACTIVE.value
                                )
    db.session.add(subscription)
    db.session.commit()

    account.legal_name = ACCOUNT_LEGAL_NAME
    account.display_name = ACCOUNT_DISPLAY_NAME
    Account.update()

    account_client = Client(uuid=Client.create_uuid(),
                            account_uuid=account.uuid,
                            created_by=user.uuid,
                            legal_name=ACCOUNT_LEGAL_NAME,
                            legal_name_slug=slugify(ACCOUNT_LEGAL_NAME),
                            display_name=ACCOUNT_DISPLAY_NAME,
                            email=TEST_USER_PRIMARY_EMAIL,
                            phone=TEST_USER_MOBILE_NUMBER,
                            street_name='',
                            postal_code='',
                            city='',
                            state='',
                            country='',
                            priority_required=False,
                            is_account_client=True)
    db.session.add(account_client)
    db.session.commit()

    account_signee = Signee(uuid=Signee.create_uuid(),
                            client_uuid=account_client.uuid,
                            account_uuid=account.uuid,
                            created_by=user.uuid,
                            full_name=user.first_name + ' ' + user.last_name,
                            email=user.email.lower(),
                            signing_sequence=None)
    db.session.add(account_signee)
    db.session.commit()

    test_contact_us_request = ContactUs(uuid=ContactUs.create_uuid(),
                                        first_name=CONTACT_US_FIRST_NAME,
                                        last_name=CONTACT_US_LAST_NAME,
                                        email=CONTACT_US_EMAIL,
                                        company_size=CONTACT_US_COMPANY_SIZE,
                                        company_name=CONTACT_US_COMPANY_NAME,
                                        message=CONTACT_US_MESSAGE)
    db.session.add(test_contact_us_request)

    cancel_contract_email_template_data = EmailTemplate(uuid=EmailTemplate.create_uuid(),
                                                        account_uuid=account.uuid,
                                                        email_type=CANCEL_EMAIL_TEMPLATE_TYPE,
                                                        email_subject=CANCEL_EMAIL_TEMPLATE_EMAIL_SUBJECT,
                                                        email_body=CANCEL_EMAIL_TEMPLATE_EMAIL_BODY)
    db.session.add(cancel_contract_email_template_data)

    send_contract_to_signee_email_template_data = EmailTemplate(uuid=EmailTemplate.create_uuid(),
                                                                account_uuid=account.uuid,
                                                                email_type=SEND_CONTRACT_TO_SIGNEEE_EMAIL_TEMPLATE_TYPE,
                                                                email_subject=SEND_CONTRACT_TO_SIGNEEE_EMAIL_TEMPLATE_EMAIL_SUBJECT,
                                                                email_body=SEND_CONTRACT_TO_SIGNEEE_EMAIL_TEMPLATE_EMAIL_BODY)
    db.session.add(send_contract_to_signee_email_template_data)

    db.session.commit()
    yield app.test_client()


@pytest.fixture(scope='session')
def super_admin_client(app):
    """
        This method is being used to fetch the app object to test the admin user test cases.
            - Admin User is created on app object initialization
            - Getting Authenticated
            - Added auth_token to test_client.
            - At the end of session, User is being deleted from cognito user pool.
    """
    account = Account(uuid=Account.create_uuid(),
                      legal_name='',
                      display_name='',
                      vat_percentage='',
                      address='',
                      postal_code='',
                      city='',
                      state='',
                      country=''
                      )
    db.session.add(account)
    db.session.commit()

    super_admin = User(uuid=User.create_uuid(),
                       account_uuid=account.uuid,
                       first_name=SUPER_ADMIN_FIRST_NAME,
                       last_name=SUPER_ADMIN_LAST_NAME,
                       email=SUPER_ADMIN_PRIMARY_EMAIL,
                       force_password_update=False,
                       password=generate_password_hash(SUPER_ADMIN_PASSWORD),
                       mobile_number=SUPER_ADMIN_MOBILE_NUMBER,
                       user_type=UserType.SUPER_ADMIN.value
                       )
    db.session.add(super_admin)
    db.session.commit()

    yield app.test_client()


def validate_status_code(**kwargs):
    """
        This method is a generic method being used to validate the status_code.
            - Checking if received response status code matches expected status code.
    """

    return kwargs.get('expected') == kwargs.get('received')


def validate_response(**kwargs):
    """
        This method is a generic method being used to validate the response.
            - Checking if received response matches expected.
        1. checks if received and expected are dict
                if they are dict then sort them key wise so that seq of keys in both dict is same
                then iterate over all keys and check if they match
                now recursively call validate response on expected and received value of that key
        2. checks if received and expected are lists and then iterates over the list
                    and if yes then recursively calls validate response on each index  of expected  and received
        3. if received and expected are not dicts neither lists then it directly tries matching them and returns true if matched
    """
    received = kwargs.get('received')
    expected = kwargs.get('expected')

    if type(received) == dict and type(expected) == dict:
        received_keys = list(kwargs.get('received').keys())
        received_keys.sort()
        sorted_received_dict = {i: kwargs.get(
            'received')[i] for i in received_keys}
        expected_keys = list(kwargs.get('expected').keys())
        expected_keys.sort()
        sorted_expected_dict = {i: kwargs.get(
            'expected')[i] for i in expected_keys}
        for (r_key, r_val), (e_key, e_val) in zip(sorted_received_dict.items(), sorted_expected_dict.items()):
            if r_key == e_key:
                if not validate_response(received=r_val, expected=e_val):
                    return False
            else:
                return False
        return True

    if type(received) == list and type(expected) == list:

        for rec, exp in zip(received, expected):
            if not validate_response(received=rec, expected=exp):
                return False
        return True

    if received == expected or expected == '*':
        return True


def get_auth_token_by_user_type(client, is_super_admin):
    """Get user auth token from Cognito"""
    if is_super_admin:
        email = SUPER_ADMIN_PRIMARY_EMAIL
        password = SUPER_ADMIN_PASSWORD
    else:
        email = TEST_USER_PRIMARY_EMAIL
        password = TEST_USER_PASSWORD

    authentication_api_response = client.post(
        '/api/v1/user/authenticate',
        json={'email': email, 'password': password},
        content_type='application/json'
    )
    auth_token = json.loads(authentication_api_response.data.decode(
        'utf-8')).get('data').get('auth_token')
    return auth_token
