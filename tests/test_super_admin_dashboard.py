"""This file contains the test cases for the  super admin dashboard module."""

from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import get_pagination_meta
from flask import jsonify
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code
from app.models.contract import Contract
from app.models.client import Client
from app.models.signee import Signee
from app.models.account import Account
from app.helpers.constants import ContractStatus


def test_client_list(super_admin_client):
    """
       TEST CASE: Get client list by page, size, sort - user : SUPER ADMIN
    """

    auth_token = get_auth_token_by_user_type(
        client=super_admin_client, is_super_admin=True)

    api_response = super_admin_client.get(
        '/api/v1/admin/client/list?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    page = 1
    size = 10
    q = None
    sort = 'asc'

    client_objs, objects_count = Contract.get_all_client_with_contract_count(
        q=q, sort=sort, page=page, size=size)
    client_list = [row._asdict() for row in client_objs]

    data = {'result': jsonify(client_list).json,
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


def test_client_list_negative_not_logged_in(super_admin_client):
    """
       TEST CASE: (Negative) Get client list, USER not Logged in
    """

    api_response = super_admin_client.get(
        '/api/v1/admin/client/list?page=1&size=10&sort=asc',
        content_type='application/json',
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_client_list_negative_not_super_admin(user_client):
    """
       TEST CASE: (Negative) Get client list - user : NOT SUPER ADMIN
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/admin/client/list?page=1&size=10&sort=asc',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.NOT_ALLOWED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_dashboard_details(super_admin_client):
    """
       TEST CASE: Get dashboard details - user : SUPER ADMIN
    """

    auth_token = get_auth_token_by_user_type(
        client=super_admin_client, is_super_admin=True)

    start_timestamp = 1667556665
    end_timestamp = 1699092665

    api_response = super_admin_client.get(
        f'/api/v1/admin/get-dashboard-details?start_date={start_timestamp}&end_date={end_timestamp}',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    client_count = Client.get_total_count(start_timestamp, end_timestamp)
    signee_count = Signee.get_total_count(start_timestamp, end_timestamp)
    account_count = Account.get_total_count(start_timestamp, end_timestamp)
    contract_count = Contract.get_total_count(
        start_timestamp, end_timestamp)

    contracts = Contract.get_contracts_status_details(
        start_timestamp=start_timestamp, end_timestamp=end_timestamp)

    dashboard_data_obj = {
        status.value: {'count': 0, 'amount': 0} for status in ContractStatus
    }

    for count, amount, status in contracts:
        if status in dashboard_data_obj:
            dashboard_data_obj[status]['count'] = count
            dashboard_data_obj[status]['amount'] = amount

    data = {
        'counts': {
            'client_count': client_count,
            'signee_count': signee_count,
            'account_count': account_count,
            'contract_count': contract_count
        },
        'contract_data': dashboard_data_obj
    }

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_dashboard_details_negative_not_logged_in(super_admin_client):
    """
       TEST CASE: (Negative) Get dashboard details , USER not Logged in
    """

    start_timestamp = 1667556665
    end_timestamp = 1699092665

    api_response = super_admin_client.get(
        f'/api/v1/admin/get-dashboard-details?start_date={start_timestamp}&end_date={end_timestamp}',
        content_type='application/json'
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_dashboard_details_negative_not_super_admin(user_client):
    """
       TEST CASE: (Negative) Get dashboard details - user : NOT SUPER ADMIN
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    start_timestamp = 1667556665
    end_timestamp = 1699092665

    api_response = user_client.get(
        f'/api/v1/admin/get-dashboard-details?start_date={start_timestamp}&end_date={end_timestamp}',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    expected_response = {'message': ResponseMessageKeys.NOT_ALLOWED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
