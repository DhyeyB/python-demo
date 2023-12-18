"""
    This file contains the test cases for the email template module.
"""
from app.helpers.constants import ResponseMessageKeys
from app.models.account import Account
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code
from app.models.email_template import EmailTemplate
from app.helpers.utility import get_pagination_meta
from flask import jsonify
from app.helpers.constants import EmailSubject
from app.helpers.constants import CONTRACT_CANCELLED
from app.helpers.constants import ValidationMessages


def test_get_email_list(user_client):
    """
        TEST CASE: Get Email list
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid

    api_response = user_client.get(
        '/api/v1/email-template/list?page=1&size=10&sort=asc', content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    email_template_objs, objects_count = EmailTemplate.get_email_template_list(
        account_uuid=account_uuid, page=page, q=q, size=size, sort=sort)

    email_template_list = EmailTemplate.serialize(email_template_objs)

    data = {'result': jsonify(email_template_list).json,
            'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                       page_size=objects_count if size is None else int(
                size),
        total_items=objects_count)}

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_email_list_negative_not_logged_in(user_client):
    """
        TEST CASE: (Negative) Get Email list, USER not Logged in
    """
    api_response = user_client.get(
        '/api/v1/email-template/list?page=1&size=10&sort=asc', content_type='application/json',
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid(user_client):
    """
    TEST CASE: Get Email Template by uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    email_template_obj = EmailTemplate.get_by_id(1)
    email_template_uuid = email_template_obj.uuid

    api_response = user_client.get(
        '/api/v1/email-template/get/' + email_template_uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    emai_template_data = EmailTemplate.serialize(email_template_obj)

    expected_response = {'data': jsonify(emai_template_data).json, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get Email Template by uuid - user not logged-in
    """
    email_template_obj = EmailTemplate.get_by_id(1)
    email_template_uuid = email_template_obj.uuid

    api_response = user_client.get(
        '/api/v1/email-template/get/' + email_template_uuid,
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
    TEST CASE: (Negative) Get Email Template by incorrect uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/email-template/get/' + '123',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.EMAIL_TEMPLATE_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_email_template_uuid(user_client):
    """
        TEST CASE: Update Email Template
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    email_template_obj = EmailTemplate.get_by_id(1)
    email_template_uuid = email_template_obj.uuid

    data = {
        'email_subject': EmailSubject.CONTRACT_CANCELLED.value,
        'email_body': CONTRACT_CANCELLED
    }

    api_response = user_client.post(
        '/api/v1/email-template/update/' + email_template_uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value,
        'status': True
    }

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_email_template_uuid_negative_not_logged_in(user_client):
    """
        TEST CASE: (Negative) Update Email Template by uuid - user not logged-in
    """
    email_template_obj = EmailTemplate.get_by_id(1)
    email_template_uuid = email_template_obj.uuid

    data = {
        'email_subject': EmailSubject.CONTRACT_CANCELLED.value,
        'email_body': CONTRACT_CANCELLED
    }

    api_response = user_client.post(
        '/api/v1/email-template/update/' + email_template_uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer'}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_email_template_uuid_negative_incorrect_uuid(user_client):
    """
    TEST CASE: (Negative) Update Email Template by incorrect uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'email_subject': EmailSubject.CONTRACT_CANCELLED.value,
        'email_body': CONTRACT_CANCELLED
    }

    api_response = user_client.post(
        '/api/v1/email-template/update/' + '123', json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {
        'message': ResponseMessageKeys.EMAIL_TEMPLATE_NOT_FOUND.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_email_template_uuid_negative_no_email_subject(user_client):
    """
    TEST CASE: (Negative) Update Email Template by uuid without required field email_subject
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'email_body': CONTRACT_CANCELLED
    }

    email_template_obj = EmailTemplate.get_by_id(1)
    email_template_uuid = email_template_obj.uuid

    api_response = user_client.post(
        '/api/v1/email-template/update/' + email_template_uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email_subject': ValidationMessages.EMAIL_SUBJECT_IS_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_email_template_uuid_negative_no_email_body(user_client):
    """
    TEST CASE: (Negative) Update Email Template by uuid without required field email_body
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'email_subject': EmailSubject.CONTRACT_CANCELLED.value
    }

    email_template_obj = EmailTemplate.get_by_id(1)
    email_template_uuid = email_template_obj.uuid

    api_response = user_client.post(
        '/api/v1/email-template/update/' + email_template_uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email_body': ValidationMessages.EMAIL_BODY_IS_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_email_template_uuid_negative_type_missmatch_email_subject(user_client):
    """
    TEST CASE: (Negative) Update Email Template by uuid with type missmatch email_subject
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'email_subject': 123,
        'email_body': CONTRACT_CANCELLED
    }

    email_template_obj = EmailTemplate.get_by_id(1)
    email_template_uuid = email_template_obj.uuid

    api_response = user_client.post(
        '/api/v1/email-template/update/' + email_template_uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email_subject': 'Email Subject should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_update_by_email_template_uuid_negative_type_missmatch_email_body(user_client):
    """
    TEST CASE: (Negative) Update Email Template by uuid with type missmatch email_body
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    data = {
        'email_subject': EmailSubject.CONTRACT_CANCELLED.value,
        'email_body': 123
    }

    email_template_obj = EmailTemplate.get_by_id(1)
    email_template_uuid = email_template_obj.uuid

    api_response = user_client.post(
        '/api/v1/email-template/update/' + email_template_uuid, json=data, content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'error': {'email_body': 'Email Body should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
