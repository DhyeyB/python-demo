"""
    This file contains the test cases for the folder module.
"""
import pytest
from app.helpers.constants import ResponseMessageKeys
from app.models.account import Account
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code
from app.helpers.constants import ValidationMessages
from app.models.folder import Folder
from flask import jsonify
from app.helpers.utility import get_pagination_meta
from flask import jsonify


@pytest.mark.run(order=5)
def test_create(user_client):
    """
        TEST CASE: Add Folder
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'folder_name': 'test_folder'
    }

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    folder = Folder.get_by_id(1)
    folder_obj = Folder.serialize(folder)

    expected_response = {
        'data': jsonify(folder_obj).json,
        'message': ResponseMessageKeys.RECORD_ADDED_SUCCESSFULLY.value,
        'status': True
    }

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_invalid_folder_name(user_client):
    """
        TEST CASE: Add Folder - Invalid folder name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'folder_name': 'test@folder'
    }

    expected_response = {
        'message': ResponseMessageKeys.INVALID_FOLDER_NAME.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=7)
def test_create_negative_same_folder_name(user_client):
    """
        TEST CASE: Add Folder with same folder name
    """

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'folder_name': 'test_folder_update',
    }

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.FOLDER_ALREADY_EXISTS.value.format(data.get('folder_name')), 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_folder_name(user_client):
    """
        TEST CASE: Add Folder without folder name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {}

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'folder_name': ValidationMessages.FOLDER_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_not_logged_in(user_client):
    """
        TEST CASE: (negative) Create Folder - USER not logged-in
    """
    data = {
        'folder_name': 'test_folder'
    }

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_folder_list(user_client):
    """
        TEST CASE: Get folder list
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    api_response = user_client.get(
        '/api/v1/folder/list?page=1&size=10&sort=asc', content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    folder_list_objs, objects_count = Folder.get_folder_list(
        q=q, sort=sort, page=page, size=size, account_uuid=account_uuid)
    folder_list = Folder.serialize(folder_list_objs)

    data = {'result': jsonify(folder_list).json,
            'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                       page_size=int(size), total_items=objects_count)}

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_folder_list_not_logged_in(user_client):
    """
        TEST CASE: (Negative) Get folder list, USER not Logged in
    """
    api_response = user_client.get(
        '/api/v1/folder/list?page=1&size=10&sort=asc', content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=6)
def test_update(user_client):
    """
        TEST CASE: Update Folder
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    data = {
        'folder_name': 'test_folder_update',
        'folder_uuid': folder_uuid
    }

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    updated_folder = Folder.get_by_id(1)
    folder_obj = Folder.serialize(updated_folder)

    expected_response = {
        'data': jsonify(folder_obj).json,
        'message': ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value,
        'status': True
    }

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_invalid_folder_name(user_client):
    """
        TEST CASE: update Folder - Invald folder name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    data = {
        'folder_name': 'test@folder',
        'folder_uuid': folder_uuid
    }

    expected_response = {
        'message': ResponseMessageKeys.INVALID_FOLDER_NAME.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_no_folder_name(user_client):
    """
        TEST CASE: (negative) Update Folder without folder name
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    data = {
        'folder_uuid': folder_uuid
    }

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'folder_name': ValidationMessages.FOLDER_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_not_logged_in(user_client):
    """
        TEST CASE: (negative) Update Folder - USER not logged-in
    """
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    data = {
        'folder_name': 'test_folder',
        'folder_uuid': folder_uuid
    }

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_negative_invalid_folder_uuid(user_client):
    """
        TEST CASE: (negative) Update folder with invalid folder uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    folder_uuid = '123'

    data = {
        'folder_name': 'test_folder_update',
        'folder_uuid': folder_uuid
    }

    expected_response = {
        'message': ResponseMessageKeys.FOLDER_NOT_FOUND.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_delete_negative_invalid_folder_uuid(user_client):
    """
        TEST CASE: (negative) Delete folder with invalid folder uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    folder_uuid = '123'

    expected_response = {
        'message': ResponseMessageKeys.FOLDER_NOT_FOUND.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/folder/delete/' + folder_uuid, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_delete_negative_not_logged_in(user_client):
    """
        TEST CASE: (negative) Delete Folder - USER not logged-in
    """
    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    api_response = user_client.post(
        '/api/v1/folder/delete/' + folder_uuid, content_type='application/json'
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=13)
def test_delete_negative_contracts_associated(user_client):
    """
        TEST CASE: (negative) Delete Folder - When contracts are associated with folder
    """

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    folder_obj = Folder.get_by_id(1)
    folder_uuid = folder_obj.uuid

    api_response = user_client.post(
        '/api/v1/folder/delete/' + folder_uuid, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.FOLDER_HAVE_CONTRACT_ASCCOCIATED_AND_CANT_BE_DELETED.value,
                         'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


@pytest.mark.run(order=14)
def test_delete(user_client):
    """
        TEST CASE: Delete Folder
    """

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'folder_name': 'test_folder_delete'
    }

    api_response = user_client.post(
        '/api/v1/folder/create-update', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    folder_obj = Folder.get_by_id(2)
    folder_uuid = folder_obj.uuid

    api_response = user_client.post(
        '/api/v1/folder/delete/' + folder_uuid, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.RECORD_DELETED_SUCCESSFULLY.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
