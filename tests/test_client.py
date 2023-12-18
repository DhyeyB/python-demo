"""This file contains the test cases for the client module."""
import pytest

from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import ValidationMessages
from app.helpers.utility import get_pagination_meta
from app.models.client import Client
from app.models.user import User
from flask import jsonify
from slugify import slugify
from tests.conftest import CLIENT_CITY
from tests.conftest import CLIENT_COUNTRY
from tests.conftest import CLIENT_DISPLAY_NAME
from tests.conftest import CLIENT_EMAIL
from tests.conftest import CLIENT_LEGAL_NAME
from tests.conftest import CLIENT_PHONE_NUMBER
from tests.conftest import CLIENT_POSTAL_CODE
from tests.conftest import CLIENT_STATE
from tests.conftest import CLIENT_STREET_NAME
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import TEST_USER_PRIMARY_EMAIL
from tests.conftest import validate_response
from tests.conftest import validate_status_code


@pytest.mark.run(order=1)
def test_create(user_client):
    """
    TEST CASE: Create client
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {
            'client': [{
                'id': '*',
                'uuid': '*',
                'account_uuid': account_uuid,
                'created_by': user_uuid,
                'legal_name': CLIENT_LEGAL_NAME,
                'legal_name_slug': slugify(CLIENT_LEGAL_NAME),
                'display_name': CLIENT_DISPLAY_NAME,
                'email': CLIENT_EMAIL,
                'phone': CLIENT_PHONE_NUMBER,
                'street_name': None,
                'postal_code': None,
                'city': None,
                'state': None,
                'country': None,
                'priority_required': '*',
                'is_account_client': False,
                'created_at': '*',
                'updated_at': '*',
            }]
        },
        'message': ResponseMessageKeys.CLIENT_CREATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Create client - USER not Logged in
    """
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'uuid': Client.create_uuid(),
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json')

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_already_exists(user_client):
    """
    TEST CASE: (Negative) Create client - client already exists in same account
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': 'client2',
        'email': 'email@email.com',
        'phone': '1234567890'
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.CLIENT_ALREADY_EXISTS.value.format(CLIENT_LEGAL_NAME),
                         'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_legal_name(user_client):
    """
    TEST CASE: (Negative) Create client with missmatch legal name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': 123,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'legal_name': 'Legal Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_display_name(user_client):
    """
    TEST CASE: (Negative) Create client with missmatch display name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': 123,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'display_name': 'Display Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_phone(user_client):
    """
    TEST CASE: (Negative) Create client with missmatch phone type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': 1234567890
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'phone': 'Phone should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_email(user_client):
    """
    TEST CASE: (Negative) Create client with missmatch email type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': 1234,
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email': 'Email should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_invalid_email_string(user_client):
    """
    TEST CASE: (Negative) Create client with missmatch invalid email string
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': 'abc.gmail.com',
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_legal_name(user_client):
    """
    TEST CASE: (Negative) Create client without required field legal name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token})

    expected_response = {'error': {'legal_name': ValidationMessages.LEGAL_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_display_name(user_client):
    """
    TEST CASE: (Negative) Create client without required field display name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token})

    expected_response = {'error': {'display_name': ValidationMessages.DISPLAY_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_email(user_client):
    """
    TEST CASE: (Negative) Create client without required field email
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'phone': CLIENT_PHONE_NUMBER
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token})

    expected_response = {'error': {'email': ValidationMessages.EMAIL_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_phone(user_client):
    """
    TEST CASE: (Negative) Create client without required field phone
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid
    account_uuid = user_obj.account_uuid

    client_data = {
        'account_uuid': account_uuid,
        'created_by': user_uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token})

    expected_response = {'error': {'phone': ValidationMessages.PHONE_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=2)
def test_update(user_client):
    """
    TEST CASE: Update client data
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {
            'client': [{
                'id': client_obj.id,
                'uuid': client_obj.uuid,
                'account_uuid': client_obj.account_uuid,
                'created_by': client_obj.created_by,
                'legal_name': CLIENT_LEGAL_NAME,
                'legal_name_slug': slugify(CLIENT_LEGAL_NAME),
                'display_name': CLIENT_DISPLAY_NAME,
                'email': CLIENT_EMAIL,
                'phone': CLIENT_PHONE_NUMBER,
                'street_name': CLIENT_STREET_NAME,
                'postal_code': CLIENT_POSTAL_CODE,
                'city': CLIENT_CITY,
                'state': CLIENT_STATE,
                'country': CLIENT_COUNTRY,
                'priority_required': '*',
                'is_account_client': False,
                'created_at': '*',
                'updated_at': '*',
            }]
        },
        'message': ResponseMessageKeys.CLIENT_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_not_logged_in(user_client):
    """
    TEST CASE: (negative) Update client data - USER not logged-in
    """
    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json')

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_incorrect_client_uuid(user_client):
    """
    TEST CASE: (Negative) Update client data with incorrect client uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_data = {
        'client_uuid': '123',
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CLIENT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_legal_name(user_client):
    """
    TEST CASE: (Negative) Update client data without required field legal name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token})

    expected_response = {'error': {'legal_name': ValidationMessages.LEGAL_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_display_name(user_client):
    """
    TEST CASE: (Negative) Update client data without required field display name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token})

    expected_response = {'error': {'display_name': ValidationMessages.DISPLAY_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_email(user_client):
    """
    TEST CASE: (Negative) Update client data without required field email
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token})

    expected_response = {'error': {'email': ValidationMessages.EMAIL_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_phone(user_client):
    """
    TEST CASE: (Negative) Update client data without required field phone
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token})

    expected_response = {'error': {'phone': ValidationMessages.PHONE_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_street_name(user_client):
    """
    TEST CASE: (Negative) Update client data without required field street_name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {
            'client': [{
                'id': client_obj.id,
                'uuid': client_obj.uuid,
                'account_uuid': client_obj.account_uuid,
                'created_by': client_obj.created_by,
                'legal_name': CLIENT_LEGAL_NAME,
                'legal_name_slug': slugify(CLIENT_LEGAL_NAME),
                'display_name': CLIENT_DISPLAY_NAME,
                'email': CLIENT_EMAIL,
                'phone': CLIENT_PHONE_NUMBER,
                'street_name': '*',
                'postal_code': CLIENT_POSTAL_CODE,
                'city': CLIENT_CITY,
                'state': CLIENT_STATE,
                'country': CLIENT_COUNTRY,
                'priority_required': '*',
                'is_account_client': False,
                'created_at': '*',
                'updated_at': '*',
            }]
        },
        'message': ResponseMessageKeys.CLIENT_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_postal_code(user_client):
    """
    TEST CASE: (Negative) Update client data without required field postal_code
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {
            'client': [{
                'id': client_obj.id,
                'uuid': client_obj.uuid,
                'account_uuid': client_obj.account_uuid,
                'created_by': client_obj.created_by,
                'legal_name': CLIENT_LEGAL_NAME,
                'legal_name_slug': slugify(CLIENT_LEGAL_NAME),
                'display_name': CLIENT_DISPLAY_NAME,
                'email': CLIENT_EMAIL,
                'phone': CLIENT_PHONE_NUMBER,
                'street_name': CLIENT_STREET_NAME,
                'postal_code': '*',
                'city': CLIENT_CITY,
                'state': CLIENT_STATE,
                'country': CLIENT_COUNTRY,
                'priority_required': '*',
                'is_account_client': False,
                'created_at': '*',
                'updated_at': '*',
            }]
        },
        'message': ResponseMessageKeys.CLIENT_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_city(user_client):
    """
    TEST CASE: (Negative) Update client data without required field city
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {
            'client': [{
                'id': client_obj.id,
                'uuid': client_obj.uuid,
                'account_uuid': client_obj.account_uuid,
                'created_by': client_obj.created_by,
                'legal_name': CLIENT_LEGAL_NAME,
                'legal_name_slug': slugify(CLIENT_LEGAL_NAME),
                'display_name': CLIENT_DISPLAY_NAME,
                'email': CLIENT_EMAIL,
                'phone': CLIENT_PHONE_NUMBER,
                'street_name': CLIENT_STREET_NAME,
                'postal_code': CLIENT_POSTAL_CODE,
                'city': '*',
                'state': CLIENT_STATE,
                'country': CLIENT_COUNTRY,
                'priority_required': '*',
                'is_account_client': False,
                'created_at': '*',
                'updated_at': '*',
            }]
        },
        'message': ResponseMessageKeys.CLIENT_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_state(user_client):
    """
    TEST CASE: (Negative) Update client data without required field state
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {
            'client': [{
                'id': client_obj.id,
                'uuid': client_obj.uuid,
                'account_uuid': client_obj.account_uuid,
                'created_by': client_obj.created_by,
                'legal_name': CLIENT_LEGAL_NAME,
                'legal_name_slug': slugify(CLIENT_LEGAL_NAME),
                'display_name': CLIENT_DISPLAY_NAME,
                'email': CLIENT_EMAIL,
                'phone': CLIENT_PHONE_NUMBER,
                'street_name': CLIENT_STREET_NAME,
                'postal_code': CLIENT_POSTAL_CODE,
                'city': CLIENT_CITY,
                'state': '*',
                'country': CLIENT_COUNTRY,
                'priority_required': '*',
                'is_account_client': False,
                'created_at': '*',
                'updated_at': '*',
            }]
        },
        'message': ResponseMessageKeys.CLIENT_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_country(user_client):
    """
    TEST CASE: (Negative) Update client data without required field country
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {
            'client': [{
                'id': client_obj.id,
                'uuid': client_obj.uuid,
                'account_uuid': client_obj.account_uuid,
                'created_by': client_obj.created_by,
                'legal_name': CLIENT_LEGAL_NAME,
                'legal_name_slug': slugify(CLIENT_LEGAL_NAME),
                'display_name': CLIENT_DISPLAY_NAME,
                'email': CLIENT_EMAIL,
                'phone': CLIENT_PHONE_NUMBER,
                'street_name': CLIENT_STREET_NAME,
                'postal_code': CLIENT_POSTAL_CODE,
                'city': CLIENT_CITY,
                'state': CLIENT_STATE,
                'priority_required': '*',
                'is_account_client': False,
                'country': '*',
                'created_at': '*',
                'updated_at': '*',
            }]
        },
        'message': ResponseMessageKeys.CLIENT_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_client_uuid(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch client uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_data = {
        'client_uuid': 123,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': 'Client Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_legal_name(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch legal name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': 12345,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'legal_name': 'Legal Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_display_name(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch display name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': 12345,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'display_name': 'Display Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_email(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch email type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': 12345,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email': 'Email should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_phone(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch phone type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': 1234567890,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'phone': 'Phone should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_street_name(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch street name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': 1234,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'street_name': 'Street Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_postal_code(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch postal code type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': 380015,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'postal_code': 'Postal Code should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_city(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch city type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': 987,
        'state': CLIENT_STATE,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'city': 'City should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_state(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch state type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': 567,
        'country': CLIENT_COUNTRY
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'state': 'State should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_country(user_client):
    """
    TEST CASE: (Negative) Update client data with missmatch country type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)

    client_data = {
        'client_uuid': client_obj.uuid,
        'legal_name': CLIENT_LEGAL_NAME,
        'display_name': CLIENT_DISPLAY_NAME,
        'email': CLIENT_EMAIL,
        'phone': CLIENT_PHONE_NUMBER,
        'street_name': CLIENT_STREET_NAME,
        'postal_code': CLIENT_POSTAL_CODE,
        'city': CLIENT_CITY,
        'state': CLIENT_STATE,
        'country': 876
    }

    api_response = user_client.post(
        '/api/v1/client/create-update', json=client_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'country': 'Country should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list(user_client):
    """
    TEST CASE: Get client for logged-in user by page, size, sort
    User : Any User Type
    """

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    api_response = user_client.get(
        '/api/v1/client/list?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    account_uuid = user_obj.account_uuid
    client_objs, objects_count = Client.get_all_by_account_uuid(q=q, sort=sort, page=page, size=size,
                                                                account_uuid=account_uuid)
    client_list = Client.serialize(client_objs)

    data = {'result': jsonify(client_list).json,
            'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                       page_size=int(size), total_items=objects_count)}

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get clients but USER not logged-in
    """
    api_response = user_client.get(
        '/api/v1/client/list?page=1&size=10&sort=asc',
        content_type='application/json')

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid(user_client):
    """
    TEST CASE: Get client by uuid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    client_obj = Client.get_by_id(2)
    uuid = client_obj.uuid
    api_response = user_client.get(
        '/api/v1/client/get/' + uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    client_data = Client.serialize(client_obj)

    expected_response = {'data': jsonify(client_data).json, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get client by uuid - USER not logged-in
    """
    client_obj = Client.get_by_id(2)
    uuid = client_obj.uuid
    api_response = user_client.get(
        '/api/v1/client/get/' + uuid,
        content_type='application/json'
    )
    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_client_not_found(user_client):
    """
    TEST CASE: Get client by uuid - client uuid invalid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/client/get/' + '1234',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CLIENT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
