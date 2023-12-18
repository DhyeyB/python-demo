"""Contains user related API definitions."""
from app import logger
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import field_type_validator
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.models.plan import Plan
from app.views.base_view import BaseView
from flask import request
import stripe
from stripe.error import StripeError


class PlanView(BaseView):
    @classmethod
    def create_plan(cls):
        try:
            data = request.get_json(force=True)
            field_types = {'name': str, 'period': str, 'status': str,
                           'amount': str, 'discount': str, 'description': str, 'feature': list}
            required_fields = ['name', 'period', 'status',
                               'amount', 'discount', 'description', 'feature']
            post_data = field_type_validator(
                request_data=data, field_types=field_types)
            if post_data['is_error']:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                          error=post_data['data'])

            is_valid = required_validator(
                request_data=data, required_fields=required_fields)
            if is_valid['is_error']:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                          error=is_valid['data'])

            stripe_price = None

            try:
                stripe_product = stripe.Product.create(name=data.get('name'))
                stripe_price = stripe.Price.create(
                    product=stripe_product.id,
                    unit_amount=data.get('amount'),
                    currency='GBP',
                    recurring={'interval': data.get('period')},
                )

            except StripeError as e:
                error_message = str(e)
                logger.error(f'Stripe Error: {error_message}')
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.FAILED.value, data=None,
                                          error=None)

            if stripe_price:
                plan_uuid = Plan.create_uuid()
                plan_data = {
                    'uuid': plan_uuid,
                    'reference_plan_id': stripe_price.id,
                    'name': data.get('name'),
                    'period': data.get('period'),
                    'status': data.get('status'),
                    'amount': data.get('amount'),
                    'discount': data.get('discount'),
                    'description': data.get('description'),
                    'feature': data.get('feature')
                }

                plan = Plan.add(plan_data)
                if plan is None:
                    stripe.Plan.delete(stripe_price.id)
                    return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                              message_key=ResponseMessageKeys.FAILED.value, data=None,
                                              error=None)

                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.RECORD_ADDED_SUCCESSFULLY.value, data=None,
                                          error=None)

            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

        except Exception as e:
            error_message = str(e)
            logger.error(f'Unexpected Error: {error_message}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

    @classmethod
    def get_all_plans(cls):
        plans = Plan.get_all()
        plan_data = Plan.serialize_plan(plans)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=plan_data,
                                  error=None)

    @classmethod
    def get_plan_by_uuid(cls, plan_uuid: str):
        plan = Plan.get_by_uuid(plan_uuid)
        if plan is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.PLAN_NOT_FOUND.value, data=None,
                                      error=None)

        plan_data = Plan.serialize_plan(plan, single_object=True)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=plan_data,
                                  error=None)

    @classmethod
    def update_plan(cls, plan_uuid: str):
        data = request.get_json(force=True)
        field_types = {'name': str, 'period': str, 'status': str,
                       'amount': str, 'discount': str, 'description': str, 'feature': list}
        required_fields = ['name', 'period', 'status',
                           'amount', 'discount', 'description', 'feature']
        post_data = field_type_validator(
            request_data=data, field_types=field_types)
        if post_data['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=post_data['data'])

        is_valid = required_validator(
            request_data=data, required_fields=required_fields)
        if is_valid['is_error']:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error=is_valid['data'])

        plan = Plan.get_by_uuid(plan_uuid)
        if plan is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.PLAN_NOT_FOUND.value, data=None,
                                      error=None)
        plan.name = data.get('name')
        plan.period = data.get('period')
        plan.status = data.get('status')
        plan.amount = data.get('amount')
        plan.discount = data.get('discount')
        plan.description = data.get('description')
        plan.feature = data.get('feature')

        Plan.update()

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                  error=None)
