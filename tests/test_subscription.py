"""This file contains the test cases for the Subscription module"""

from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import ValidationMessages
from app.helpers.utility import get_pagination_meta
from app.models.contact_us import ContactUs
from flask import jsonify

from app.models.payment import Payment
from app.models.user import User
from tests.conftest import get_auth_token_by_user_type, TEST_USER_PRIMARY_EMAIL
from tests.conftest import validate_response
from tests.conftest import validate_status_code


def test_get_payments_by_account(user_client):
    """
       TEST CASE: Get payment history of Account by page, size, sort
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    api_response = user_client.get(
        '/api/v1/payment/get-by-account?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    account_payments, objects_count = Payment.get_by_account(account_uuid=account_uuid, q=q, sort=sort, page=page,
                                                             size=size)
    payment_data = Payment.serialize(account_payments)

    data = {'result': jsonify(payment_data).json,
            'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                       page_size=objects_count if size is None else int(
                                                           size), total_items=objects_count)}

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list_negative_not_logged_in(user_client):
    """
       TEST CASE: (Negative) Get payment history of Account by page, size, sort, USER not Logged in
    """
    api_response = user_client.get(
        '/api/v1/payment/get-by-account?page=1&size=10&sort=asc',
        content_type='application/json'
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
