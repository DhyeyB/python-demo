"""This file contains the test cases for the client module."""
import pytest

from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import ValidationMessages
from app.models.client import Client
from app.models.signee import Signee
from app.models.user import User
from flask import jsonify
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import SIGNEE1_EMAIL
from tests.conftest import SIGNEE1_FULL_NAME
from tests.conftest import SIGNEE2_EMAIL
from tests.conftest import SIGNEE2_FULL_NAME
from tests.conftest import TEST_USER_PRIMARY_EMAIL
from tests.conftest import validate_response
from tests.conftest import validate_status_code
from app import logger


@pytest.mark.run(order=3)
def test_create(user_client):
    """
    TEST CASE: Create Signee
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    signees = Signee.get_all_signee_uuid_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_uuids = [item[0] for item in signees]

    expected_response = {
        'data': signee_uuids,
        'message': ResponseMessageKeys.SIGNEES_CREATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_client_uuid(user_client):
    """
    TEST CASE: (Negative) Create Signee without required field client_uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': ValidationMessages.CLIENT_UUID_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_full_name(user_client):
    """
    TEST CASE: (Negative) Create Signee without required field full name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'full_name': ValidationMessages.FULL_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_email(user_client):
    """
    TEST CASE: (Negative) Create Signee without required field email
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email': ValidationMessages.EMAIL_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_signing_sequence(user_client):
    """
    TEST CASE: (Negative) Create Signee without required field signing_sequence
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signing_sequence': ValidationMessages.SIGNING_SEQUENCE_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_client_uuid(user_client):
    """
    TEST CASE: (Negative) Create Signee with missmatch client_uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': 123,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': 'Client Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_full_name(user_client):
    """
    TEST CASE: (Negative) Create Signee with missmatch full name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': 124,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'full_name': 'Full Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_email(user_client):
    """
    TEST CASE: (Negative) Create Signee with missmatch email type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': 123,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
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
    TEST CASE: (Negative) Create Signee with invalid email string
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': 'abcgmail.com',
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_signing_sequence(user_client):
    """
    TEST CASE: (Negative) Create Signee with missmatch signing_sequence type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 'ABC'
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signing_sequence': 'Signing Sequence should be integer value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_not_logged_in(user_client):
    """
    TEST CASE: (negative) Create Signee - USER not logged-in
    """
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_already_exists(user_client):
    """
    TEST CASE: (Negative) Create Signee - email already exists
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 1
            },
            {
                'client_uuid': client_obj.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/create', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.SIGNEE_EMAIL_ALREADY_EXISTS.value.format(SIGNEE1_EMAIL),
                         'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_client(user_client):
    """
    TEST CASE: Get Signees by client
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    client_uuid = client_obj.uuid

    api_response = user_client.get(
        '/api/v1/signee/get-by-client/' + client_uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_uuid)
    signee_list = Signee.serialize(signee_objs)

    data = {'result': signee_list}

    expected_response = {'data': jsonify(data).json, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_client_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get Signees by client - user not logged-in
    User : Any User Type
    """
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    client_uuid = client_obj.uuid

    api_response = user_client.get(
        '/api/v1/signee/get-by-client/' + client_uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid(user_client):
    """
    TEST CASE: Get Signee by uuid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    signee_obj = Signee.get_by_id(1)
    signee_uuid = signee_obj.uuid

    api_response = user_client.get(
        '/api/v1/signee/get/' + signee_uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    signee_data = Signee.serialize(signee_obj)

    expected_response = {'data': jsonify(signee_data).json, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get Signee by uuid - user not logged-in
    User : Any User Type
    """
    signee_obj = Signee.get_by_id(1)
    signee_uuid = signee_obj.uuid

    api_response = user_client.get(
        '/api/v1/signee/get/' + signee_uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_incorrect_uuid(user_client):
    """
    TEST CASE: (Negative) Get Signee by incorrect uuid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/signee/get/' + '123',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.SIGNEE_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=4)
def test_update_by_client_uuid(user_client):
    """
    TEST CASE: Update Signee
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': ['*'],
        'message': ResponseMessageKeys.SIGNEE_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_delete_signee(user_client):
    """
    TEST CASE: Update Signee - add new signee on update page
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': '*', 'status': True}

    # assert validate_status_code(
    #     expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_no_client_uuid(user_client):
    """
    TEST CASE: (Negative) Update Signee without required field client_uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': ValidationMessages.CLIENT_UUID_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_no_full_name(user_client):
    """
    TEST CASE: (Negative) Update Signee without required field full name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'full_name': ValidationMessages.FULL_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_no_email(user_client):
    """
    TEST CASE: (Negative) Update Signee without required field email
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email': ValidationMessages.EMAIL_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_no_signing_sequence(user_client):
    """
    TEST CASE: (Negative) Update Signee without required field signing_sequence
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signing_sequence': ValidationMessages.SIGNING_SEQUENCE_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Update Signee - USER not logged-in
    """
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_type_missmatch_client_uuid(user_client):
    """
    TEST CASE: (Negative) Update Signee with missmatch client_uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': 123,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': 'Client Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_type_missmatch_signee_uuid(user_client):
    """
    TEST CASE: (Negative) Update Signee with missmatch signee_uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': 123,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signee_uuid': 'Signee Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_type_missmatch_full_name(user_client):
    """
    TEST CASE: (Negative) Update Signee with missmatch full name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': 123,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'full_name': 'Full Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_type_missmatch_email(user_client):
    """
    TEST CASE: (Negative) Update Signee with missmatch email type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': 123,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email': 'Email should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_type_missmatch_signing_sequence(user_client):
    """
    TEST CASE: (Negative) Update Signee with missmatch signing_sequence type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 'ABC'
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signing_sequence': 'Signing Sequence should be integer value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_invalid_email_string(user_client):
    """
    TEST CASE: (Negative) Update Signee with invalid email string
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': 'abcgmail.com',
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_incorrect_client_uuid(user_client):
    """
    TEST CASE: (Negative) Update Signee - incorrect client_uuid passed
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': '123',
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE2_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + '123', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CLIENT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_client_uuid_negative_with_existing_email(user_client):
    """
    TEST CASE: (Negative) Update Signee but email already exists
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    client_obj = Client.get_by_user_uuid(user_obj.uuid)
    signee1 = Signee.get_by_email(SIGNEE1_EMAIL)
    signee2 = Signee.get_by_email(SIGNEE2_EMAIL)

    data = {
        'client_data': {
            'client_uuid': client_obj.uuid,
            'priority_required': True
        },
        'signees_data': [
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee1.uuid,
                'full_name': SIGNEE1_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 2
            },
            {
                'client_uuid': client_obj.uuid,
                'signee_uuid': signee2.uuid,
                'full_name': SIGNEE2_FULL_NAME,
                'email': SIGNEE1_EMAIL,
                'signing_sequence': 1
            },
        ]
    }

    api_response = user_client.post(
        '/api/v1/signee/update/' + client_obj.uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.SIGNEE_EMAIL_ALREADY_EXISTS.value.format(SIGNEE1_EMAIL),
                         'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
