"""This file contains the test cases for the contract module."""
import pytest

from app.helpers.constants import ResponseMessageKeys, CurrencyCode
from app.helpers.constants import ValidationMessages
from app.helpers.utility import get_pagination_meta
from app.models.client import Client
from app.models.contract import Contract
from app.models.contract_signee import ContractSignee
from app.models.signee import Signee
from app.models.user import User
from flask import jsonify
from tests.conftest import CONTRACT_DEMO_CONTENT
from tests.conftest import CONTRACT_PURPOSE
from tests.conftest import CONTRACT_BRIEF
from tests.conftest import CONTRACT_SERVICE_NAME
from tests.conftest import CONTRACT_DURATION
from tests.conftest import CONTRACT_AMOUNT
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import TEST_USER_PRIMARY_EMAIL
from tests.conftest import validate_response
from tests.conftest import validate_status_code
from app.models.folder import Folder
from app import logger


@pytest.mark.run(order=8)
def test_create_with_optional_fields(user_client):
    """
    TEST CASE: Create contract with optional fields
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    client_country = client_obj.country
    currency_code = CurrencyCode.get(client_country)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = [obj.uuid for obj in signee_objs]
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT,
                     'currency_code': currency_code}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {'contract_uuid': '*'},
        'message': ResponseMessageKeys.CONTRACT_CREATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=9)
def test_create_without_optional_fields(user_client):
    """
    TEST CASE: Create contract without optional fields
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = [obj.uuid for obj in signee_objs]
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF,
                     'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {'contract_uuid': '*'},
        'message': ResponseMessageKeys.CONTRACT_CREATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Create contract - USER not Logged in
    """
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {
        'purpose': CONTRACT_PURPOSE,
        'client_uuid': client_obj.uuid,
        'folder_uuid': folder_uuid,
        'template_uuid': None,
        'brief': CONTRACT_BRIEF,
        'content': CONTRACT_DEMO_CONTENT,
        'service_name': CONTRACT_SERVICE_NAME,
        'duration': CONTRACT_DURATION,
        'amount': CONTRACT_AMOUNT,
    }

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json')

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_incorrect_folder_uuid(user_client):
    """
    TEST CASE: (Negative) Update contract data with incorrect folder uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid
    folder_uuid = '123'

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = [obj.uuid for obj in signee_objs]
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.FOLDER_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_no_purpose(user_client):
    """
    TEST CASE: (Negative) Create contract without required field purpose
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'purpose': ValidationMessages.PURPOSE_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_no_client_uuid(user_client):
    """
    TEST CASE: (Negative) Create contract without required field client_uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': ValidationMessages.CLIENT_UUID_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_no_folder_uuid(user_client):
    """
    TEST CASE: (Negative) Create contract without required field folder_uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'folder_uuid': ValidationMessages.FOLDER_IS_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_no_signees(user_client):
    """
    TEST CASE: (Negative) Create contract without required field signees
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'template_uuid': None,
                     'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME, 'duration': CONTRACT_DURATION,
                     'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signees': ValidationMessages.SIGNEES_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_no_brief(user_client):
    """
    TEST CASE: (Negative) Create contract without required field brief
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'service_name': CONTRACT_SERVICE_NAME, 'duration': CONTRACT_DURATION,
                     'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'brief': ValidationMessages.BRIEF_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=10)
def test_create_no_service_name(user_client):
    """
    TEST CASE: Create contract without field service name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = [obj.uuid for obj in signee_objs]

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'duration': CONTRACT_DURATION,
                     'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    logger.info('api_response.json')
    logger.info(api_response.json)

    expected_response = {
        'data': {'contract_uuid': '*'},
        'message': ResponseMessageKeys.CONTRACT_CREATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_no_content(user_client):
    """
    TEST CASE: (Negative) Create contract without required field content
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'content': ValidationMessages.CONTENT_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_type_missmatch_purpose(user_client):
    """
    TEST CASE: (Negative) Create contract with missmatch purpose type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': 123, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'purpose': 'Purpose should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_type_missmatch_client_uuid(user_client):
    """
    TEST CASE: (Negative) Create contract with missmatch client_uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': 123, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': 'Client Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_type_missmatch_signees(user_client):
    """
    TEST CASE: (Negative) Create contract with missmatch signees type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': 123,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signees': 'Signees should be list value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_type_missmatch_brief(user_client):
    """
    TEST CASE: (Negative) Create contract with missmatch brief type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': 123, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'brief': 'Brief should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_type_missmatch_service_name(user_client):
    """
    TEST CASE: (Negative) Create contract with missmatch service name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': 123,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'service_name': 'Service Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_type_missmatch_duration(user_client):
    """
    TEST CASE: (Negative) Create contract with missmatch duration type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': '1 Month', 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'duration': 'Duration should be integer value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_type_missmatch_amount(user_client):
    """
    TEST CASE: (Negative) Create contract with missmatch amount type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': '$100', 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'amount': 'Amount should be float value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_type_missmatch_content(user_client):
    """
    TEST CASE: (Negative) Create contract with missmatch content type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': 123}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'content': 'Content should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=11)
def test_update(user_client):
    """
    TEST CASE: Update contract data
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    contract_obj = Contract.get_by_id(1)
    client_uuid = contract_obj.client_uuid
    client_obj = Client.get_by_uuid(uuid=client_uuid)
    client_country = client_obj.country
    currency_code = CurrencyCode.get(client_country)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_signees = ContractSignee.get_by_account_client_and_contract(account_uuid=account_uuid,
                                                                         client_uuid=client_uuid,
                                                                         contract_uuid=contract_obj.uuid)
    signees = [obj.signee_uuid for obj in contract_signees]
    contract_data = {
        'contract_uuid': contract_obj.uuid,
        'purpose': contract_obj.purpose,
        'client_uuid': contract_obj.client_uuid,
        'folder_uuid': folder_uuid,
        'signees': signees,
        'template_uuid': None,
        'brief': CONTRACT_BRIEF,
        'content': CONTRACT_DEMO_CONTENT,
        'service_name': CONTRACT_SERVICE_NAME,
        'duration': CONTRACT_DURATION,
        'amount': CONTRACT_AMOUNT,
        'currency_code': currency_code
    }

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {'contract_uuid': contract_obj.uuid},
        'message': ResponseMessageKeys.CONTRACT_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_not_logged_in(user_client):
    """
    TEST CASE: (negative) Update contract data - USER not logged-in
    """
    contract_obj = Contract.get_by_id(1)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {
        'purpose': CONTRACT_PURPOSE,
        'client_uuid': contract_obj.client_uuid,
        'folder_uuid': folder_uuid,
        'signees': [],
        'template_uuid': None,
        'brief': CONTRACT_BRIEF,
        'content': CONTRACT_DEMO_CONTENT,
        'service_name': CONTRACT_SERVICE_NAME,
        'duration': CONTRACT_DURATION,
        'amount': CONTRACT_AMOUNT,
    }

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json')

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_incorrect_contract_uuid(user_client):
    """
    TEST CASE: (Negative) Update contract data with incorrect contract uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    contract_obj = Contract.get_by_id(1)
    client_uuid = contract_obj.client_uuid
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_signees = ContractSignee.get_by_account_client_and_contract(account_uuid=account_uuid,
                                                                         client_uuid=client_uuid,
                                                                         contract_uuid=contract_obj.uuid)
    signees = [obj.uuid for obj in contract_signees]

    contract_data = {
        'contract_uuid': '123',
        'purpose': CONTRACT_PURPOSE,
        'client_uuid': '1234',
        'folder_uuid': folder_uuid,
        'signees': signees,
        'template_uuid': None,
        'brief': CONTRACT_BRIEF,
        'content': CONTRACT_DEMO_CONTENT,
        'service_name': CONTRACT_SERVICE_NAME,
        'duration': CONTRACT_DURATION,
        'amount': CONTRACT_AMOUNT,
    }

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CONTRACT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_incorrect_folder_uuid(user_client):
    """
    TEST CASE: (Negative) Update contract data with incorrect folder uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    contract_obj = Contract.get_by_id(1)
    client_uuid = contract_obj.client_uuid
    folder_uuid = '123'

    contract_signees = ContractSignee.get_by_account_client_and_contract(account_uuid=account_uuid,
                                                                         client_uuid=client_uuid,
                                                                         contract_uuid=contract_obj.uuid)
    signees = [obj.uuid for obj in contract_signees]

    contract_data = {
        'contract_uuid': '123',
        'purpose': CONTRACT_PURPOSE,
        'client_uuid': '1234',
        'folder_uuid': folder_uuid,
        'signees': signees,
        'template_uuid': None,
        'brief': CONTRACT_BRIEF,
        'content': CONTRACT_DEMO_CONTENT,
        'service_name': CONTRACT_SERVICE_NAME,
        'duration': CONTRACT_DURATION,
        'amount': CONTRACT_AMOUNT,
    }

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.FOLDER_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_no_purpose(user_client):
    """
    TEST CASE: (Negative) Update contract without required field purpose
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'contract_uuid': contract_obj.uuid, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'purpose': ValidationMessages.PURPOSE_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_no_client_uuid(user_client):
    """
    TEST CASE: (Negative) Update contract without required field client_uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': ValidationMessages.CLIENT_UUID_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_no_folder_uuid(user_client):
    """
    TEST CASE: (Negative) update contract without required field folder_uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)

    contract_data = {'contract_uuid': contract_obj.uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'folder_uuid': ValidationMessages.FOLDER_IS_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_no_signees(user_client):
    """
    TEST CASE: (Negative) Update contract without required field signees
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'contract_uuid': contract_obj.uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'folder_uuid': folder_uuid, 'template_uuid': None,
                     'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME, 'duration': CONTRACT_DURATION,
                     'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signees': ValidationMessages.SIGNEES_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_no_brief(user_client):
    """
    TEST CASE: (Negative) Update contract without required field brief
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'service_name': CONTRACT_SERVICE_NAME, 'duration': CONTRACT_DURATION,
                     'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'brief': ValidationMessages.BRIEF_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=12)
def test_update_no_service_name(user_client):
    """
    TEST CASE:  Update contract without field service name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    contract_obj = Contract.get_by_id(1)
    client_uuid = contract_obj.client_uuid
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_signees = ContractSignee.get_by_account_client_and_contract(account_uuid=account_uuid,
                                                                         client_uuid=client_uuid,
                                                                         contract_uuid=contract_obj.uuid)
    signees = [obj.signee_uuid for obj in contract_signees]
    contract_data = {
        'contract_uuid': contract_obj.uuid,
        'purpose': contract_obj.purpose,
        'client_uuid': contract_obj.client_uuid,
        'folder_uuid': folder_uuid,
        'signees': signees,
        'template_uuid': None,
        'brief': CONTRACT_BRIEF,
        'content': CONTRACT_DEMO_CONTENT,
        'duration': CONTRACT_DURATION,
        'amount': CONTRACT_AMOUNT,
    }

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'data': {'contract_uuid': contract_obj.uuid},
        'message': ResponseMessageKeys.CONTRACT_DATA_UPDATED_SUCCESSFULLY.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_no_content(user_client):
    """
    TEST CASE: (Negative) Update contract without required field content
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'content': ValidationMessages.CONTENT_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_purpose(user_client):
    """
    TEST CASE: (Negative) Update contract with missmatch purpose type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': 123, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'purpose': 'Purpose should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_client_uuid(user_client):
    """
    TEST CASE: (Negative) Update contract with missmatch client_uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': 123, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': 'Client Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_signees(user_client):
    """
    TEST CASE: (Negative) Update contract with missmatch signees type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': 123,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signees': 'Signees should be list value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_brief(user_client):
    """
    TEST CASE: (Negative) Update contract with missmatch brief type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': 123, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'brief': 'Brief should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_service_name(user_client):
    """
    TEST CASE: (Negative) Update contract with missmatch service name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': 123,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'service_name': 'Service Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_duration(user_client):
    """
    TEST CASE: (Negative) Update contract with missmatch duration type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': '1 Month', 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'duration': 'Duration should be integer value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_amount(user_client):
    """
    TEST CASE: (Negative) Update contract with missmatch amount type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': '$100', 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'amount': 'Amount should be float value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_type_missmatch_content(user_client):
    """
    TEST CASE: (Negative) Update contract with missmatch content type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_obj = Contract.get_by_id(1)
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid
    contract_data = {'contract_uuid': contract_obj.uuid, 'folder_uuid': folder_uuid, 'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': 123}

    api_response = user_client.post(
        '/api/v1/contract/create-update', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'content': 'Content should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list_with_folder_uuid(user_client):
    """
    TEST CASE: Get contract for logged-in user without folder_uuid by page, size, sort
    User : Any User Type
    """

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    api_response = user_client.get(
        f'/api/v1/contract/list/{folder_uuid}?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    contract_objs, objects_count = Contract.get_contracts_list(account_uuid=account_uuid, folder_uuid=folder_uuid, q=q, sort=sort, page=page,
                                                               size=size)
    contract_list = Contract.serialize(contract_objs)

    data = {'result': jsonify(contract_list).json,
            'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                       page_size=int(size), total_items=objects_count)}

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list_without_folder_uuid(user_client):
    """
    TEST CASE: Get contract for logged-in user with folder_uuid by page, size, sort
    User : Any User Type
    """

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)

    api_response = user_client.get(
        '/api/v1/contract/list?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    account_uuid = user_obj.account_uuid
    contract_objs, objects_count = Contract.get_contracts_list(account_uuid=account_uuid, q=q, sort=sort, page=page,
                                                               size=size)
    contract_list = Contract.serialize(contract_objs)

    data = {'result': jsonify(contract_list).json,
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
    TEST CASE: (Negative) Get contracts but USER not logged-in
    """
    data = {}

    api_response = user_client.get(
        '/api/v1/contract/list?page=1&size=10&sort=asc',
        json=data,
        content_type='application/json')

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid(user_client):
    """
    TEST CASE: Get contract by uuid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    contract_obj = Contract.get_by_id(1)
    uuid = contract_obj.uuid
    api_response = user_client.get(
        '/api/v1/contract/get/' + uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    contract_data = Contract.serialize(contract_obj)

    expected_response = {'data': jsonify(contract_data).json, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get contract by uuid - USER not logged-in
    """
    contract_obj = Contract.get_by_id(1)
    uuid = contract_obj.uuid
    api_response = user_client.get(
        '/api/v1/contract/get/' + uuid,
        content_type='application/json'
    )
    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_contract_not_found(user_client):
    """
    TEST CASE: Get contract by uuid - contract uuid invalid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/contract/get/' + '1234',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CONTRACT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_send(user_client):
    """
    TEST CASE: Send contract
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    contract_obj = Contract.get_by_id(1)
    contract_data = {'contract_uuid': contract_obj.uuid}

    api_response = user_client.post(
        '/api/v1/contract/send', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CONTRACT_IS_SENT.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_send_not_logged_in(user_client):
    """
    TEST CASE: Send contract - USER not logged in
    """
    contract_obj = Contract.get_by_id(1)
    contract_data = {'contract_uuid': contract_obj.uuid}

    api_response = user_client.post(
        '/api/v1/contract/send', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {
        'message': ResponseMessageKeys.ACCESS_DENIED.value, 'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_send_incorrect_contract_uuid(user_client):
    """
    TEST CASE: Send contract
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    contract_data = {'contract_uuid': '1234'}

    api_response = user_client.post(
        '/api/v1/contract/send', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CONTRACT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_send_type_missmatch_contract_uuid(user_client):
    """
    TEST CASE: (Negative) Send contract with missmatch contract uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    contract_data = {'contract_uuid': 1234}

    api_response = user_client.post(
        '/api/v1/contract/send', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'contract_uuid': 'Contract Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_cancel(user_client):
    """
    TEST CASE: Cancel contract
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    contract_obj = Contract.get_by_id(1)
    contract_data = {'contract_uuid': contract_obj.uuid}

    api_response = user_client.post(
        '/api/v1/contract/cancel', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CONTRACT_IS_CANCELLED.value, 'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_cancel_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Cancel contract - USER not logged in
    """
    contract_obj = Contract.get_by_id(1)
    contract_data = {'contract_uuid': contract_obj.uuid}

    api_response = user_client.post(
        '/api/v1/contract/cancel', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {
        'message': ResponseMessageKeys.ACCESS_DENIED.value, 'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_cancel_incorrect_contract_uuid(user_client):
    """
    TEST CASE: (Negative) Cancel contract with incorrect contract uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    contract_data = {'contract_uuid': '1234'}

    api_response = user_client.post(
        '/api/v1/contract/cancel', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CONTRACT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_cancel_type_missmatch_contract_uuid(user_client):
    """
    TEST CASE: (Negative) Cancel Contract with missmatch contract uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    contract_data = {'contract_uuid': 1234}

    api_response = user_client.post(
        '/api/v1/contract/cancel', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'contract_uuid': 'Contract Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template(user_client):
    """
    TEST CASE: Get AI generated template for contract
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = [obj.uuid for obj in signee_objs]
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_contract_data = {
        'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
        'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
        'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT
    }
    expected_response = {
        'data': {
            'contract_data': expected_contract_data,
            'content': '*',
            'sections': '*',
            'contract_currency_code': '*',
            'updated_amount': '*'
        },
        'message': ResponseMessageKeys.SUCCESS.value, 'status': True
    }
    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get AI generated template for contract - USER not logged in
    """
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {
        'message': ResponseMessageKeys.ACCESS_DENIED.value, 'status': False
    }

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_no_purpose(user_client):
    """
    TEST CASE: (Negative) Get AI generated template without required field purpose
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'purpose': ValidationMessages.PURPOSE_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_no_client_uuid(user_client):
    """
    TEST CASE: (Negative) Get AI generated template without required field client_uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': ValidationMessages.CLIENT_UUID_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_no_signees(user_client):
    """
    TEST CASE: (Negative) Get AI generated template without required field signees
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'template_uuid': None,
                     'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME, 'duration': CONTRACT_DURATION,
                     'amount': CONTRACT_AMOUNT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signees': ValidationMessages.SIGNEES_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_no_brief(user_client):
    """
    TEST CASE: (Negative) Get AI generated template without required field brief
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'service_name': CONTRACT_SERVICE_NAME, 'duration': CONTRACT_DURATION,
                     'amount': CONTRACT_AMOUNT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'brief': ValidationMessages.BRIEF_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_type_missmatch_purpose(user_client):
    """
    TEST CASE: (Negative) Get AI generated template with missmatch purpose type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': 123, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'purpose': 'Purpose should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_type_missmatch_client_uuid(user_client):
    """
    TEST CASE: (Negative) Get AI generated template with missmatch client_uuid type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': 123, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'client_uuid': 'Client Uuid should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_type_missmatch_signees(user_client):
    """
    TEST CASE: (Negative) Get AI generated template with missmatch signees type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': 123,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'signees': 'Signees should be list value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_type_missmatch_brief(user_client):
    """
    TEST CASE: (Negative) Get AI generated template with missmatch brief type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': 123, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'brief': 'Brief should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_type_missmatch_service_name(user_client):
    """
    TEST CASE: (Negative) Get AI generated template with missmatch service name type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': 123,
                     'duration': CONTRACT_DURATION, 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'service_name': 'Service Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_type_missmatch_duration(user_client):
    """
    TEST CASE: (Negative) Get AI generated template with missmatch duration type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': '1 Month', 'amount': CONTRACT_AMOUNT, 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'duration': 'Duration should be integer value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_generated_template_type_missmatch_amount(user_client):
    """
    TEST CASE: (Negative) Get AI generated template with missmatch amount type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)
    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    user_uuid = user_obj.uuid

    client_obj = Client.get_by_user_uuid(user_uuid=user_uuid)
    signee_objs = Signee.get_all_by_client_uuid(
        account_uuid=account_uuid, client_uuid=client_obj.uuid)
    signee_list = Signee.serialize(signee_objs)
    contract_data = {'purpose': CONTRACT_PURPOSE, 'client_uuid': client_obj.uuid, 'signees': signee_list,
                     'template_uuid': None, 'brief': CONTRACT_BRIEF, 'service_name': CONTRACT_SERVICE_NAME,
                     'duration': CONTRACT_DURATION, 'amount': '$100', 'content': CONTRACT_DEMO_CONTENT}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-generated-template', json=contract_data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'amount': 'Amount should be float value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_download_as_pdf_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Download contract as pdf - USER not logged-in
    """
    contract_obj = Contract.get_by_id(1)
    uuid = contract_obj.uuid
    api_response = user_client.get(
        '/api/v1/contract/download-as-pdf/' + uuid,
        content_type='application/json'
    )
    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_download_as_pdf_negative_contract_not_found(user_client):
    """
    TEST CASE: (Negative) Download contract as pdf - contract uuid invalid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/contract/download-as-pdf/' + '1234',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.CONTRACT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)

