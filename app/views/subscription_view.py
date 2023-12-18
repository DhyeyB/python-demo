"""Contains user related API definitions."""
from datetime import datetime, timedelta
import json
from app import config_data
from app import logger
from app.helpers.constants import EmailSubject
from app.helpers.constants import EmailTypes
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import SubscriptionDays
from app.helpers.constants import SubscriptionStatus
from app.helpers.utility import field_type_validator, get_pagination_meta
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.models.account import Account
from app.models.payment import Payment
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.user import User
from app.views.base_view import BaseView
from flask import request
import stripe
from stripe.error import StripeError
from workers.email_worker import EmailWorker


class SubscriptionView(BaseView):
    @classmethod
    def create_subscription(cls):
        try:
            data = request.get_json(force=True)
            field_types = {'user_uuid': str,
                           'account_uuid': str, 'plan_uuid': str}
            required_fields = ['user_uuid', 'account_uuid', 'plan_uuid']
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

            selected_plan = Plan.get_by_uuid(data.get('plan_uuid'))
            if selected_plan is None:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.PLAN_NOT_FOUND.value, data=None,
                                          error=None)

            account = Account.get_by_uuid(data.get('account_uuid'))
            if account is None:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                          error=None)

            user = User.get_by_uuid(data.get('user_uuid'))
            if user is None:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.USER_NOT_FOUND.value, data=None,
                                          error=None)

            is_user_with_account_id = User.is_user_with_account_id(
                user_uuid=user.uuid, account_uuid=account.uuid)
            if is_user_with_account_id is None:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.USER_DOES_BELONG_TO_GIVEN_ACCOUNT.value, data=None,
                                          error=None)

            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=user.first_name
            )
            logger.info('stripe_customer.id')
            logger.info(stripe_customer.id)

            account.reference_customer_id = stripe_customer.id
            Account.update()

            logger.info('account.reference_customer_id')
            logger.info(account.reference_customer_id)

            expired_or_cancelled_subscription = Subscription.get_expired_or_cancelled_subscription(
                account.uuid)

            if expired_or_cancelled_subscription:
                stripe_subscription = stripe.checkout.Session.create(
                    customer=stripe_customer.id,
                    billing_address_collection='auto',
                    success_url=config_data['APP_URL']
                    + '/account?success=true&account_uuid='
                    + data.get('account_uuid'),
                    cancel_url=config_data['APP_URL']
                    + '/account?canceled=true',
                    line_items=[
                        {
                            'price': selected_plan.reference_plan_id,
                            'quantity': 1,
                        },
                    ],
                    mode='subscription'
                )
            else:
                stripe_subscription = stripe.checkout.Session.create(
                    customer=stripe_customer.id,
                    billing_address_collection='auto',
                    success_url=config_data['APP_URL']
                    + '/account?success=true&account_uuid='
                    + data.get('account_uuid'),
                    cancel_url=config_data['APP_URL']
                    + '/account?canceled=true',
                    line_items=[
                        {
                            'price': selected_plan.reference_plan_id,
                            'quantity': 1,
                        },
                    ],
                    mode='subscription',
                    subscription_data={
                        'trial_period_days': SubscriptionDays.TRIAL_PERIOD_DAYS.value
                    }
                )

            subscription_uuid = Subscription.create_uuid()

            # Get the current date and time
            now = datetime.now()

            # Calculate the date 15 days from now
            date_with_trial_period = now + timedelta(days=15)

            # Format the date_in_15_days as a string
            trial_period_end_date = date_with_trial_period.strftime(
                '%Y-%m-%d %H:%M:%S')

            subscription_data = {
                'uuid': subscription_uuid,
                'account_uuid': account.uuid,
                'plan_uuid': selected_plan.uuid,
                'status': SubscriptionStatus.INACTIVE.value,
                'trial_period_end_date': trial_period_end_date
            }

            subscription = Subscription.add(subscription_data)
            if subscription is None:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.FAILED.value, data=None,
                                          error=None)

            logger.info('Subscription created successfully in DB')

            stripe_response = {'url': stripe_subscription.url}
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.RECORD_ADDED_SUCCESSFULLY.value, data=stripe_response,
                                      error=None)

        except StripeError as exception_error:
            logger.error(
                f'POST -> Error while creating stripe subscription: {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.STRIPE_ERROR.value, data=None, error=None)

        except Exception as exception_error:
            logger.error(
                f'POST -> Error while creating subscription: {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None, error=None)

    @classmethod
    def get_all_subscriptions(cls):
        subscriptions = Subscription.get_all()
        subscription_data = Subscription.serialize_subscription(subscriptions)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=subscription_data,
                                  error=None)

    @classmethod
    def get_subscription_by_uuid(cls, subscription_uuid: str):
        subscription = Subscription.get_by_uuid(subscription_uuid)
        if subscription is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.SUBSCRIPTION_NOT_FOUND.value, data=None,
                                      error=None)

        subscription_data = Subscription.serialize_subscription(
            subscription, single_object=True)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=subscription_data,
                                  error=None)

    @classmethod
    def update_subscription(cls, subscription_uuid: str):
        data = request.get_json(force=True)
        field_types = {'plan_uuid': str, 'status': str,
                       'start_date': str, 'end_date': str}
        required_fields = ['plan_uuid', 'status', 'start_date', 'end_date']
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

        subscription = Subscription.get_by_uuid(subscription_uuid)
        if subscription is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.SUBSCRIPTION_NOT_FOUND.value, data=None,
                                      error=None)

        subscription.plan_uuid = data.get('plan_uuid')
        subscription.status = data.get('status')
        subscription.start_date = data.get('start_date')
        subscription.end_date = data.get('end_date')
        Subscription.update()

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                  error=None)

    @classmethod
    def handle_webhook(cls):  # noqa
        try:
            webhook_secret = config_data['STRIPE_WEBHOOK_SECRET']
            request_data = json.loads(request.data)

            if webhook_secret:
                signature = request.headers.get('stripe-signature')
                try:
                    event = stripe.Webhook.construct_event(
                        payload=request.data, sig_header=signature, secret=webhook_secret)
                    data = event['data']
                except Exception as e:
                    logger.error(
                        f'POST -> Error while constructing event in webhooks: {e}')
                    return e
                event_type = event['type']
            else:
                data = request_data['data']
                event_type = request_data['type']

            data_object = data['object']
            #  Occurs whenever a new customer is created.
            if event_type == 'customer.created':
                logger.info('Customer created')
                logger.info('Customer id')
                logger.info(data_object['id'])
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                          error=None)

            #  Occurs whenever a failed charge attempt occurs.
            if event_type == 'charge.failed':
                logger.info('Charge failed')
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                          error=None)

            # Occurs when a Checkout Session is expired.
            if event_type == 'checkout.session.expired':
                logger.info('Checkout session expired')
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                          error=None)

            #  Occurs whenever a customer is signed up for a new subscription.
            if event_type == 'customer.subscription.created':
                logger.info('Subscriptio Created')

                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.RECORD_ADDED_SUCCESSFULLY.value, data=None,
                                          error=None)

            #  Occurs when the invoice is successfully paid.
            if event_type == 'invoice.paid':
                logger.info('Invoice Paid')

                stripe_subscription_id = data_object['subscription']

                logger.info('stripe_subscription_id')
                logger.info(stripe_subscription_id)

                subscription_start_date = datetime.fromtimestamp(
                    data_object['lines']['data'][0]['period']['start'])

                # Added one day extra as stripe document suggested to add leeway af a day or two.
                subscription_end_date = datetime.fromtimestamp(
                    data_object['lines']['data'][0]['period']['end']) + timedelta(days=1)

                reference_customer_id = data_object['customer']

                logger.info('reference_customer_id')
                logger.info(reference_customer_id)

                # Getting account object by stripe customer id
                account = Account.get_account_by_reference_customer_id(
                    reference_customer_id)

                if account is None:
                    return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                              message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                              error=None)

                # Determine the email data and template based on subscription renewal
                has_used_free_trial = Subscription.check_has_used_free_trial(
                    account.uuid)

                """
                    Check if there is an active subscription for the account.
                    If an active subscription is found, it indicates that the 'invoice.paid' function
                    is being called for subscription renewal.
                """
                subscription = Subscription.get_active_subscription_by_account_uuid(
                    account.uuid)

                if subscription is None:
                    subscription = Subscription.get_latest_inactive_subscription_by_account_uuid(
                        account.uuid)
                """
                    If no active subscription is found, check for the latest inactive subscription.
                    The presence of an inactive subscription suggests that the 'invoice.paid' function
                    is being called for subscription creation.
                """

                if subscription is None:
                    return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                              message_key=ResponseMessageKeys.SUBSCRIPTION_NOT_FOUND.value, data=None,
                                              error=None)

                stripe_customer = stripe.Customer.retrieve(
                    reference_customer_id)

                logger.info('stripe_customer')
                logger.info(stripe_customer)

                # updateing subscripiton status, start,end date.
                subscription.reference_subscription_id = stripe_subscription_id
                subscription.status = SubscriptionStatus.ACTIVE.value
                subscription.start_date = subscription_start_date
                subscription.end_date = subscription_end_date

                Subscription.update()

                human_readable_format_start_date = subscription_start_date.strftime(
                    '%A, %B %d, %Y %I:%M:%S %p')
                human_readable_format_end_date = subscription_end_date.strftime(
                    '%A, %B %d, %Y %I:%M:%S %p')

                logger.info('Subscription created successfully')

                if has_used_free_trial:
                    email_data = {
                        'email_to': stripe_customer.email,
                        'subject': EmailSubject.SUBSCRIPTION_CREATED_WITHOUT_FREE_TRIAL.value,
                        'template': 'emails/subscription_start.html',
                        'email_type': EmailTypes.SUBSCRIPTION_CREATED_WITHOUT_FREE_TRIAL.value,
                        'org_id': account.uuid,
                        'email_data': {
                            'first_name': stripe_customer.name,
                            'subscription_start_date': human_readable_format_start_date,
                            'subscription_end_date': human_readable_format_end_date
                        }
                    }

                else:
                    email_data = {
                        'email_to': stripe_customer.email,
                        'subject': EmailSubject.SUBSCRIPTION_CREATED_WITH_FREE_TRIAL.value,
                        'template': 'emails/free_trial_start.html',
                        'email_type': EmailTypes.SUBSCRIPTION_CREATED_WITH_FREE_TRIAL.value,
                        'org_id': account.uuid,
                        'email_data': {
                            'first_name': stripe_customer.name,
                            'trial_start_date': human_readable_format_start_date,
                            'trial_duration': SubscriptionDays.TRIAL_PERIOD_DAYS.value
                        }
                    }

                EmailWorker.send(email_data)
                logger.info('Subscription Email Sent successfully')

                # Creating a new entry in payment table for each subscription
                logger.info('Creating new entry for payment in db')
                payment_uuid = Payment.create_uuid()
                payment_data = {
                    'uuid': payment_uuid,
                    'account_uuid': account.uuid,
                    'amount': data_object['amount_paid'],
                    'status': data_object['status'],
                    'currency': data_object['currency'],
                    'reference_payment_id': data_object['id'],
                    'response': data_object,
                }
                payment = Payment.add(payment_data)
                if payment is None:
                    logger.error('Add Payment details to DB failure')
                    return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                              message_key=ResponseMessageKeys.FAILED.value, data=None,
                                              error=None)

                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                          error=None)

            #  Occurs three days before a subscription’s trial period is scheduled to end, or when a trial is ended immediately (using trial_end=now).
            if event_type == 'customer.subscription.trial_will_end':
                logger.info('Subscription trial will end')
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                          error=None)

            #  Occurs whenever a customer’s subscription ends.
            if event_type == 'customer.subscription.deleted':
                logger.info('Customer subscription deleted')
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                          message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                          error=None)

            if event_type == 'payment_intent.succeeded':
                logger.info('Payment intent succeeded')

            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.SUCCESS.value, data=None,
                                      error=None)

        except Exception as exception_error:
            logger.error(f'POST -> Error in webhooks: {exception_error}')
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None, error=None)

    @classmethod
    def get_all_payments_by_account(cls):
        """Get all the payment history of account owner"""
        user_obj = cls.get_logged_in_user(request=request)
        account_uuid = user_obj.account_uuid

        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        account_payments, objects_count = Payment.get_by_account(account_uuid=account_uuid, q=q, sort=sort, page=page,
                                                                 size=size)
        payment_data = Payment.serialize(account_payments)

        data = {'result': payment_data,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=objects_count if size is None else int(
                                                               size), total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)
