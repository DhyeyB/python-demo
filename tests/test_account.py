"""
    This file contains the test cases for the Account module.
"""
import pytest
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import get_pagination_meta
from app.models.account import Account
from flask import jsonify
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code


def test_list(super_admin_client):
    """
       TEST CASE: Get Accounts by page, size, sort
       user : SUPER ADMIN
    """

    auth_token = get_auth_token_by_user_type(
        client=super_admin_client, is_super_admin=True)

    api_response = super_admin_client.get(
        '/api/v1/account/list?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    account_objs, objects_count = Account.get_account_list(
        q=q, sort=sort, page=page, size=size)
    account_list = [row._asdict() for row in account_objs]

    data = {'result': jsonify(account_list).json,
            'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                       page_size=int(size), total_items=objects_count)}

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list_download_true(super_admin_client):
    """
       TEST CASE: Dwonload Accounts list CSV with query param download == True
       user : SUPER ADMIN
    """

    auth_token = get_auth_token_by_user_type(
        client=super_admin_client, is_super_admin=True)

    api_response = super_admin_client.get(
        '/api/v1/account/list?page=1&size=10&sort=asc&download=True',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    data = {
        'download_link': '*'
    }

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json
    )


def test_list_download_false(super_admin_client):
    """
       TEST CASE: Dwonload Accounts list CSV with query param download == False
       user : SUPER ADMIN
    """

    auth_token = get_auth_token_by_user_type(
        client=super_admin_client, is_super_admin=True)

    api_response = super_admin_client.get(
        '/api/v1/account/list?page=1&size=10&sort=asc&download=False',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    account_objs, objects_count = Account.get_account_list(
        q=q, sort=sort, page=page, size=size)
    account_list = [row._asdict() for row in account_objs]

    data = {'result': jsonify(account_list).json,
            'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                       page_size=int(size), total_items=objects_count)}

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list_negative_not_logged_in(super_admin_client):
    """
       TEST CASE: (Negative) Get Accounts
       user: not Logged in
    """
    api_response = super_admin_client.get(
        '/api/v1/account/list?page=1&size=10&sort=asc',
        content_type='application/json'
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list_negative_not_super_admin(user_client):
    """
       TEST CASE: (Negative) Get Accounts
       user : NOT SUPER ADMIN
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/account/list?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.NOT_ALLOWED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_initiate_delete_negative_not_logged_in(user_client):
    """
        TEST CASE: (negative) Initiate delete account request - USER not logged-in
    """
    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    api_response = user_client.post(
        '/api/v1/account/initiate-delete/' + account_uuid, content_type='application/json',
        headers={'Authorization': 'Bearer'}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_initiate_delete_negative_invalid_account_uuid(user_client):
    """
        TEST CASE: (negative) Initiate delete Account with invalid account uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    account_uuid = '123'

    expected_response = {
        'message': ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/account/initiate-delete/' + account_uuid, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
