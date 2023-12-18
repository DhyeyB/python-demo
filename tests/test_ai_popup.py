"""
    This file contains the test cases for the ai popup module.
"""

from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import ValidationMessages
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code


def test_get_ai_popup_response(user_client):
    """
        TEST CASE: Get AI popup response
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'query': 'Generate me a disclaimer for Use of Information'
    }

    expected_response = {'data': {'answer': '*'},
                         'message': ResponseMessageKeys.SUCCESS.value, 'status': True}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-popup-response', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_popup_response_negative_no_query(user_client):
    """
    TEST CASE: (Negative)Get AI popup response without required field query
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-popup-response', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'query': ValidationMessages.QUERY_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_popup_response_negative_type_missmatch_full_name(user_client):
    """
    TEST CASE: (Negative)  AI popup response with missmatch query type
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'query': 1
    }

    expected_response = {'error': {'query': 'Query should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-popup-response', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_ai_popup_response_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative)  AI popup response  - user not logged-in
    """
    data = {
        'query': 'Generate me a disclaimer for Use of Information'
    }

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    api_response = user_client.post(
        '/api/v1/contract/get-ai-popup-response', json=data, content_type='application/json',
    )

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
