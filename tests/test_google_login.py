"""
    This file contains the test cases for google login module.
"""

from app.helpers.constants import ResponseMessageKeys
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code


def test_login_with_google(user_client):
    """
        TEST CASE: Get Login Url for Google
    """

    expected_response = {'data': {'authorization_uri': '*'},
                         'message': ResponseMessageKeys.SUCCESS.value, 'status': True}

    api_response = user_client.get(
        '/api/v1/user/login-with-google', content_type='application/json'
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_idp_logout(user_client):
    """
        TEST CASE: Get Logout Url
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    expected_response = {'data': {'logout_uri': '*'},
                         'message': ResponseMessageKeys.LOGOUT_SUCCESSFULLY.value, 'status': True}

    api_response = user_client.get(
        '/api/v1/user/idp-logout', content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_idp_logout_negative_not_logged_in(user_client):
    """
        TEST CASE: (negative) Get Logut Url - USER not logged-in
    """
    api_response = user_client.get(
        '/api/v1/user/idp-logout', content_type='application/json'
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
