"""This file contains the test cases for the contract_log module."""
from flask import jsonify

from app.helpers.constants import ResponseMessageKeys
from app.models.contract import Contract
from app.models.contract_signee import ContractSignee
from app.models.user import User

from tests.conftest import get_auth_token_by_user_type, TEST_USER_PRIMARY_EMAIL
from tests.conftest import validate_response
from tests.conftest import validate_status_code


def test_list(user_client):
    """
    TEST CASE: list contract signees by contract uuid
    User : Any User Type
    """

    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    user_obj = User.get_by_email(TEST_USER_PRIMARY_EMAIL)
    account_uuid = user_obj.account_uuid

    contract_obj = Contract.get_by_id(1)
    client_uuid = contract_obj.client_uuid
    contract_uuid = contract_obj.uuid

    api_response = user_client.get(
        '/api/v1/contract/list-signees/' + contract_uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )
    contract_signees = ContractSignee.get_by_account_client_and_contract(account_uuid=account_uuid,
                                                                         client_uuid=client_uuid,
                                                                         contract_uuid=contract_uuid)
    contract_signees_list = ContractSignee.serialize(contract_signees)
    data = {'result': jsonify(contract_signees_list).json}

    expected_response = {'data': data, 'message': ResponseMessageKeys.SUCCESS.value,
                         'status': True}

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_list_not_logged_in(user_client):
    """
    TEST CASE: (Negative) list contract signees - USER not logged in
    User : Any User Type
    """
    contract_obj = Contract.get_by_id(1)
    contract_uuid = contract_obj.uuid

    api_response = user_client.get(
        '/api/v1/contract/list-signees/' + contract_uuid,
        content_type='application/json',
        headers={'Authorization': 'Bearer '}
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
