"""Contains billing related API definitions."""
from app.views.base_view import BaseView
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import send_json_response
from app.models.subscription import Subscription
from app.models.user import User
from flask import request
from app.models.plan import Plan
from app.models.user_invite import UserInvite


class BillingView(BaseView):
    @classmethod
    def get_details(cls):
        user_obj = BillingView.get_logged_in_user(request=request)

        subscription = Subscription.get_active_subscription_by_account_uuid(
            user_obj.account_uuid)

        if subscription is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.SUBSCRIPTION_NOT_FOUND.value, data=None,
                                      error=None)

        plan = Plan.get_by_uuid(subscription.plan_uuid)
        if plan is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.PLAN_NOT_FOUND.value, data=None,
                                      error=None)

        primary_user = User.get_primary_user_of_account(user_obj.account_uuid)

        activated_user = User.get_user_count_by_account(user_obj.account_uuid)
        invited_user = UserInvite.get_invited_user_count_by_account(
            user_obj.account_uuid)

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

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=plan_obj,
                                  error=None)
