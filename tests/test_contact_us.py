"""
    This file contains the test cases for the contact us module.
"""

from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import ValidationMessages
from app.helpers.utility import get_pagination_meta
from app.models.contact_us import ContactUs
from flask import jsonify
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code


def test_create(user_client):
    """
        TEST CASE: Generate Contact Us Request
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'email': 'john.doe@example.com',
        'company_size': 20,
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {
        'message': ResponseMessageKeys.MESSAGE_RECEIVED_SUCCESSFULLY.value, 'status': True}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_without_optional_field_first_name(user_client):
    """
        TEST CASE: Generate Contact Us Request without optional field first name
    """
    data = {
        'last_name': 'PotterHead',
        'email': 'john.doe@example.com',
        'company_size': 20,
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {
        'message': ResponseMessageKeys.MESSAGE_RECEIVED_SUCCESSFULLY.value, 'status': True}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_without_optional_field_last_name(user_client):
    """
        TEST CASE: Generate Contact Us Request without optional field last name
    """
    data = {
        'first_name': 'Meraki',
        'email': 'john.doe@example.com',
        'company_size': 20,
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {
        'message': ResponseMessageKeys.MESSAGE_RECEIVED_SUCCESSFULLY.value, 'status': True}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_email(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request without required field email
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'company_size': 20,
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {'error': {'email': ValidationMessages.EMAIL_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_without_optional_field_company_size(user_client):
    """
        TEST CASE: Generate Contact Us Request without optional field company size
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'email': 'john.doe@example.com',
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {
        'message': ResponseMessageKeys.MESSAGE_RECEIVED_SUCCESSFULLY.value, 'status': True}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_no_company_name(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request without required field company name
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'email': 'john.doe@example.com',
        'company_size': 20,
        'message': 'Hey There!'
    }

    expected_response = {'error': {'company_name': ValidationMessages.COMPANY_NAME_REQUIRED.value},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_without_optional_field_message(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request without optional field message
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'email': 'john.doe@example.com',
        'company_size': 20,
        'company_name': 'MJ',
    }

    expected_response = {
        'message': ResponseMessageKeys.MESSAGE_RECEIVED_SUCCESSFULLY.value, 'status': True}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_first_name(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request with missmatch first name type
    """
    data = {
        'first_name': 123,
        'last_name': 'PotterHead',
        'email': 'john.doe@example.com',
        'company_size': 20,
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {'error': {'first_name': 'First Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_last_name(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request with missmatch last name type
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 1234,
        'email': 'john.doe@example.com',
        'company_size': 20,
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {'error': {'last_name': 'Last Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_email(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request with missmatch email type
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'email': 1234,
        'company_size': 20,
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {'error': {'email': 'Email should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_invalid_email_string(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request with invalid email string
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'email': 'john.doe.example',
        'company_size': 20,
        'company_name': 'MJ',
        'message': 'Hey There!'
    }

    expected_response = {
        'message': ResponseMessageKeys.INVALID_EMAIL_FORMAT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_company_name(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request with missmatch company name type
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'email': 'john.doe@example.com',
        'company_size': 20,
        'company_name': 1234,
        'message': 'Hey There!'
    }

    expected_response = {'error': {'company_name': 'Company Name should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_create_negative_type_missmatch_message(user_client):
    """
        TEST CASE: (Negative) Generate Contact Us Request with missmatch message type
    """
    data = {
        'first_name': 'Meraki',
        'last_name': 'PotterHead',
        'email': 'john.doe@example.com',
        'company_size': 20,
        'company_name': 'MJ',
        'message': 123456
    }

    expected_response = {'error': {'message': 'Message should be string value.'},
                         'message': ResponseMessageKeys.ENTER_CORRECT_INPUT.value, 'status': False}

    api_response = user_client.post(
        '/api/v1/contact-us/create', json=data, content_type='application/json'
    )

    assert validate_status_code(
        expected=400, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list(super_admin_client):
    """
       TEST CASE: Get contact us queries by page, size, sort - user : SUPER ADMIN
    """

    auth_token = get_auth_token_by_user_type(
        client=super_admin_client, is_super_admin=True)

    api_response = super_admin_client.get(
        '/api/v1/contact-us/list?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    contact_us_objs, objects_count = ContactUs.get_contact_us_list(
        q=q, sort=sort, page=page, size=size)
    contact_us_list = ContactUs.serialize(contact_us_objs)

    data = {'result': jsonify(contact_us_list).json,
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
       TEST CASE: (Negative) Get contact us queries, USER not Logged in
    """
    api_response = super_admin_client.get(
        '/api/v1/contact-us/list?page=1&size=10&sort=asc',
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
       TEST CASE: (Negative) Get contact us queries - user : NOT SUPER ADMIN
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/contact-us/list?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.NOT_ALLOWED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid(super_admin_client):
    """
       TEST CASE: Get contact us query by uuid - user : SUPER ADMIN
    """
    auth_token = get_auth_token_by_user_type(
        client=super_admin_client, is_super_admin=True)

    contact_us_obj = ContactUs.get_by_id(1)
    uuid = contact_us_obj.uuid
    api_response = super_admin_client.get(
        '/api/v1/contact-us/get/' + uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    contact_us_obj = ContactUs.get_by_id(1)
    contact_us_data = ContactUs.serialize(contact_us_obj)

    expected_response = {'data': jsonify(contact_us_data).json, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_not_logged_in(super_admin_client):
    """
       TEST CASE: (Negative) Get contact us query by id - user : Not logged in
    """
    contact_us_obj = ContactUs.get_by_id(1)
    uuid = contact_us_obj.uuid
    api_response = super_admin_client.get(
        '/api/v1/contact-us/get/' + uuid,
        content_type='application/json'
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_uuid_negative_not_super_admin(user_client):
    """
       TEST CASE: (Negative) Get contact us query by id - user : Not SUPER ADMIN
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    contact_us_obj = ContactUs.get_by_id(1)
    uuid = contact_us_obj.uuid
    api_response = user_client.get(
        '/api/v1/contact-us/get/' + uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.NOT_ALLOWED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
