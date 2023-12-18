"""
    This file contains the test cases for the branding module.
"""

from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import ValidationMessages
from app.models.account import Account
from app.models.branding import Branding
from flask import jsonify
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code
from app.helpers.constants import SupportedImageTypes
from tests.conftest import TEST_FILE_PATH_PDF
from werkzeug.datastructures import FileStorage
from app import logger


def test_create(user_client):
    """
        TEST CASE: Add Branding Details
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    data = {
        'cover_page': 'test_cover_page'
    }

    expected_response = {
        'message': ResponseMessageKeys.RECORD_ADDED_SUCCESSFULLY.value, 'status': True}

    api_response = user_client.post(
        '/api/v1/branding/add-branding-details/' + account_uuid, data=data, content_type='multipart/form-data',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_cover_page(user_client):
    """
        TEST CASE: Add Branding Details without required field cover_page
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    data = {}

    expected_response = {'error': {'cover_page': ValidationMessages.COVER_PAGE_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/branding/add-branding-details/' + account_uuid, data=data, content_type='multipart/form-data',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_company_logo_negative_with_wrong_file_type(user_client):
    """
       TEST CASE: Update branding details company logo with wrong file type (PDF).
    """
    data = {
        'cover_page': 'test_cover_page',
        'company_logo': FileStorage(
            stream=open(file=TEST_FILE_PATH_PDF, mode='rb'),
            filename='demo.pdf',
            content_type='application/pdf',
        )
    }

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    api_response = user_client.post(
        '/api/v1/branding/add-branding-details/' + account_uuid, data=data, content_type='multipart/form-data',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value,
        'status': False,
        'error': {
            'company_logo': ResponseMessageKeys.INVALID_IMAGE_FORMAT.value.format('Company logo', list(SupportedImageTypes.keys()))
        }
    }

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Add Branding Details by account uuid - user not logged-in
    User : Any User Type
    """

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    data = {
        'cover_page': 'test_cover_page'
    }

    api_response = user_client.post(
        '/api/v1/branding/add-branding-details/' + account_uuid,
        content_type='multipart/form-data',
        data=data,
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_negative_incorrect_uuid(user_client):
    """
    TEST CASE: (Negative) Add Branding Details by incorrect account uuid
    User : Any User Type
    """

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'cover_page': 'test_cover_page'
    }

    api_response = user_client.post(
        '/api/v1/branding/add-branding-details/' + '123',
        content_type='multipart/form-data',
        data=data,
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json
    )


def test_get_by_account_uuid(user_client):
    """
    TEST CASE: Get Branding Details by account uuid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    api_response = user_client.get(
        '/api/v1/branding/get-branding-details/' + account_uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    branding_details = Branding.get_by_id(1)

    branding_data = Branding.serialize(
        branding_details, single_object=True)

    expected_response = {'data': jsonify(branding_data).json, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_account_uuid_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get Branding Details by account uuid - user not logged-in
    User : Any User Type
    """

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    api_response = user_client.get(
        '/api/v1/branding/get-branding-details/' + account_uuid,
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
    TEST CASE: (Negative) Get Branding Details by incorrect account uuid
    User : Any User Type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/branding/get-branding-details/' + '123',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json
    )
