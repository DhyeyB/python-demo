"""
    This file contains the test cases for the branding module.
"""

from app.helpers.constants import ResponseMessageKeys
from app.models.account import Account
from app.models.subscription import Subscription
from app.models.plan import Plan
from app.models.user import User
from app.models.user_invite import UserInvite
from tests.conftest import get_auth_token_by_user_type
from tests.conftest import validate_response
from tests.conftest import validate_status_code
from app import logger


def test_get_by_logged_in_user_account_uuid(user_client):
    """
    TEST CASE: Get Billing Details by logged in user account uuid
    """
    auth_token = get_auth_token_by_user_type(
        client=user_client, is_super_admin=False)

    api_response = user_client.get(
        '/api/v1/billing/get-details',
        content_type='application/json',
        headers={'Authorization': 'Bearer ' + auth_token}
    )

    account_obj = Account.get_by_id(1)
    account_uuid = account_obj.uuid
    subscription = Subscription.get_active_subscription_by_account_uuid(
        account_uuid)

    plan = Plan.get_by_uuid(subscription.plan_uuid)
    primary_user = User.get_primary_user_of_account(account_uuid)

    activated_user = User.get_user_count_by_account(account_uuid)
    invited_user = UserInvite.get_invited_user_count_by_account(
        account_uuid)

    total_users = invited_user + 1
    plan_obj = {
        'plan_name': plan.name,
        'subscription_amount': plan.amount,
        'period': plan.period,
        'status': subscription.status,
        'account_owner_email': primary_user.email,
        'activated_users': activated_user,
        'total_users': total_users,
        'subscripition_start_date': subscription.start_date,
        'subscription_end_date': subscription.end_date,
        'trial_period_end_date': subscription.trial_period_end_date
    }
    expected_response = {
        'data': plan_obj, 'message': ResponseMessageKeys.SUCCESS.value, 'status': True
    }

    assert validate_status_code(
        expected=200, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)


def test_get_by_account_uuid_negative_not_logged_in(user_client):
    """
    TEST CASE: (Negative) Get Billing Details by account uuid - user not logged-in
    """

    api_response = user_client.get(
        '/api/v1/billing/get-details',
        content_type='application/json'
    )

    expected_response = {'message': ResponseMessageKeys.ACCESS_DENIED.value,
                         'status': False}

    assert validate_status_code(
        expected=401, received=api_response.status_code)
    assert validate_response(
        expected=expected_response, received=api_response.json)
