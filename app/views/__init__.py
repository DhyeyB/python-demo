"""Contain all the urls of apis"""
from app import COGNITO_CLIENT  # noqa nosort
from app import config_data  # noqa nosort
from app import logger  # noqa nosort
from app.helpers.constants import ErrorCode  # noqa nosort
from app.helpers.constants import HttpStatusCode  # noqa nosort
from app.helpers.constants import ResponseMessageKeys  # noqa nosort
from app.helpers.constants import UserType  # noqa nosort
from app.helpers.utility import send_json_response  # noqa nosort
from app.models.account import Account  # noqa nosort
from app.models.subscription import Subscription  # noqa nosort
from app.models.user import User  # noqa nosort
from flask import Blueprint  # noqa nosort
from flask import g  # noqa nosort
from flask import request  # noqa nosort

from app.views.contract_view import ContractView  # noqa nosort
from app.views.contract_signee_view import ContractSigneeView  # noqa nosort
from app.views.contract_log_view import ContractLogView  # noqa nosort
from app.views.user_view import UserView  # noqa nosort
from app.views.account_view import AccountView  # noqa nosort
from app.views.client_view import ClientView  # noqa nosort
from app.views.common_view import get_audit_log_details  # noqa nosort
from app.views.common_view import get_health_check  # noqa nosort
from app.views.common_view import list_audit_log  # noqa nosort
from app.views.contact_us_view import ContactUsView  # noqa nosort
from app.views.plan_view import PlanView  # noqa nosort
from app.views.signee_view import SigneeView  # noqa nosort
from app.views.subscription_view import SubscriptionView  # noqa nosort
from app.views.branding_view import BrandingView  # noqa nosort
from app.views.template_view import create_template  # noqa nosort
from app.views.template_view import get_all_templates  # noqa nosort
from app.views.template_view import get_all_templates_by_account  # noqa nosort
from app.views.template_view import get_template_by_id  # noqa nosort
from app.views.template_view import update_template  # noqa nosort
from app.views.user_invite_view import UserInviteView  # noqa nosort
from app.views.dashboard_view import DashboardView  # noqa nosort
from app.views.billing_view import BillingView  # noqa nosort
from app.views.folder_view import FolderView  # noa nosort
from app.views.email_template_view import EmailTemplateView  # noa nosort

# template_dir = os.path.abspath('app/views/users')
v1_blueprints = Blueprint(name='v1', import_name='api1')


@v1_blueprints.before_request
def before_blueprint():
    """This method executed in the beginning of the request."""
    g.time_log = 0
    g.request_path = request.path
    logger.info(f'request.path : {request.path}')
    try:
        if request.path not in config_data.get('OPEN_URLS') and not request.path.startswith('/api/v1/account/update/') and not request.path.startswith('/api/v1/contract/view/'):
            authorization_header = request.headers.get('Authorization')

            access_token = authorization_header.replace('Bearer ', '').strip()
            if access_token:
                user_info = COGNITO_CLIENT.get_user(AccessToken=access_token)
            else:
                return send_json_response(http_status=401, response_status=False, message_key=ResponseMessageKeys.ACCESS_DENIED.value, data=None, error=None)

            user_email = [data.get('Value') for data in user_info.get(
                'UserAttributes') if data.get('Name') == 'email'][0]

            user_object = User.get_by_email(user_email)
            if user_object is None:
                return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False, message_key=ResponseMessageKeys.USER_DETAILS_NOT_FOUND.value, data=None, error=None)

            # Check if there are any active subscription for the user
            existing_subscription = Subscription.get_active_subscription_by_account_uuid(
                account_uuid=user_object.account_uuid)
            user_data = User.serialize(user_object, single_object=True)

            if not existing_subscription and user_object.user_type != UserType.SUPER_ADMIN.value:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True, message_key=ResponseMessageKeys.USER_DOES_NOT_HAVE_ACTIVE_PLAN.value, data=user_data, error=None, error_code=ErrorCode.SUBSCRIPTION_NOT_FOUND.value)

            account_object = Account.get_by_uuid(user_object.account_uuid)
            account_legal_name = account_object.legal_name
            account_display_name = account_object.display_name

            if account_legal_name == '' and account_display_name == '' and user_object.user_type != UserType.SUPER_ADMIN.value:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True, message_key=ResponseMessageKeys.USER_ACCOUNT_NOT_SETUP.value, data=user_data, error=None, error_code=ErrorCode.ACCOUNT_NOT_SETUP.value)

            setattr(request, 'user', user_object)
            if user_object.deactivated_at is not None:
                return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False, message_key=ResponseMessageKeys.ACCESS_DENIED.value, data=None, error=None)

    except Exception as exception_error:
        logger.error(f'Authorization Failed: {exception_error}')
        return send_json_response(
            http_status=HttpStatusCode.UNAUTHORIZED.value,
            response_status=False,
            message_key=ResponseMessageKeys.ACCESS_DENIED.value,
        )


@v1_blueprints.after_request
def after_blueprint(response):
    """This method executed in the end of the request."""
    response.headers['Time-Log'] = g.time_log
    # logger.info(f'{response.status_code}: {g.request_path}: {g.time_log}')
    # Uncomment above line while debugging to see API response time in logger file.
    return response


##### Health Check URL #####
v1_blueprints.add_url_rule(
    '/health-check', view_func=get_health_check, methods=['GET'])

# Audit APIs:
v1_blueprints.add_url_rule(
    '/log/audit', view_func=list_audit_log, methods=['GET'])
v1_blueprints.add_url_rule(
    '/log/audit-detail', view_func=get_audit_log_details, methods=['GET'])

# Account APIs:
v1_blueprints.add_url_rule(
    '/account/get-account/<string:account_uuid>', view_func=AccountView.get_account_by_uuid, methods=['GET'])
v1_blueprints.add_url_rule(
    '/account/update/<string:account_uuid>', view_func=AccountView.update_account, methods=['POST'])
v1_blueprints.add_url_rule(
    '/account/list', endpoint='account_list', view_func=AccountView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/account/initiate-delete/<string:account_uuid>', endpoint='delete_account', view_func=AccountView.delete, methods=['POST'])

# User APIs:
v1_blueprints.add_url_rule(
    '/user/create', view_func=UserView.create_user, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user/authenticate', view_func=UserView.authenticate, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user/confirm-verification-code', view_func=UserView.confirm_verification_code, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user/resend-verification-code', view_func=UserView.resend_verification_code, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user/get-user/<string:user_uuid>', view_func=UserView.get_user_by_uuid, methods=['GET'])
v1_blueprints.add_url_rule(
    '/user/update/<string:user_uuid>', view_func=UserView.update_user, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user/list', endpoint='user_list', view_func=UserView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/user/get-user-by-token', view_func=UserView.get_user_by_token, methods=['GET'])
v1_blueprints.add_url_rule(
    '/user/create-admin', view_func=UserView.create_admin, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user/login-with-google', view_func=UserView.google_login, methods=['GET'])
v1_blueprints.add_url_rule(
    '/user/idp-callback', view_func=UserView.idp_callback, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user/idp-logout', view_func=UserView.idp_logout, methods=['GET'])
v1_blueprints.add_url_rule(
    '/user/email-verification', view_func=UserView.email_verification, methods=['POST'])


# User Invite APIs:
v1_blueprints.add_url_rule(
    '/user-invite/send-invite', view_func=UserInviteView.send_invite, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user-invite/set-password', view_func=UserInviteView.verify_token, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user-invite/accept', view_func=UserInviteView.accept_invite, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user-invite/resend-user-invite', view_func=UserInviteView.resend_user_invite, methods=['POST'])
v1_blueprints.add_url_rule(
    '/user-invite/list', endpoint='user_invite_list', view_func=UserInviteView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/user-invite/delete/<string:uuid>', endpoint='user_invite_delete', view_func=UserInviteView.delete,
    methods=['POST'])


# Plan APIs:
v1_blueprints.add_url_rule(
    '/plan/create', view_func=PlanView.create_plan, methods=['POST'])
v1_blueprints.add_url_rule(
    '/plan/get-plan/<string:plan_uuid>', view_func=PlanView.get_plan_by_uuid, methods=['GET'])
v1_blueprints.add_url_rule(
    '/plan/update/<string:plan_uuid>', view_func=PlanView.update_plan, methods=['POST'])
v1_blueprints.add_url_rule(
    '/plan/get-all-plans', view_func=PlanView.get_all_plans, methods=['GET'])

# Subscription APIs:
v1_blueprints.add_url_rule(
    '/subscription/create', view_func=SubscriptionView.create_subscription, methods=['POST'])
v1_blueprints.add_url_rule(
    '/subscription/get-subscription/<string:subscription_uuid>', view_func=SubscriptionView.get_subscription_by_uuid, methods=['GET'])
v1_blueprints.add_url_rule(
    '/subscription/update/<string:subscription_uuid>', view_func=SubscriptionView.update_subscription, methods=['POST'])
v1_blueprints.add_url_rule(
    '/subscription/get-all-subscriptions', view_func=SubscriptionView.get_all_subscriptions, methods=['GET'])

# Payment APIs:
v1_blueprints.add_url_rule(
    '/payment/get-by-account', view_func=SubscriptionView.get_all_payments_by_account, methods=['GET'])

# Webhook API:
v1_blueprints.add_url_rule(
    '/handle-webhook', view_func=SubscriptionView.handle_webhook, methods=['POST'])

# Contract APIs:
v1_blueprints.add_url_rule(
    '/contract/get-ai-generated-template', endpoint='get_ai_generated_template',
    view_func=ContractView.get_ai_generated_template, methods=['POST'])

v1_blueprints.add_url_rule(
    '/contract/create-update', endpoint='contract_create_update', view_func=ContractView.create_update,
    methods=['POST'])
v1_blueprints.add_url_rule(
    '/contract/view/<string:contract_uuid>', endpoint='contract_view', view_func=ContractView.view_contract, methods=['GET'])
v1_blueprints.add_url_rule(
    '/contract/list/<string:folder_uuid>', endpoint='contract_list', view_func=ContractView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/contract/list', endpoint='contract_list', view_func=ContractView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/contract/get/<string:contract_uuid>', endpoint='contract_get_by_uuid', view_func=ContractView.get_by_uuid,
    methods=['GET'])
v1_blueprints.add_url_rule(
    '/contract/send', endpoint='contract_send', view_func=ContractView.send, methods=['POST'])
v1_blueprints.add_url_rule(
    '/contract/cancel', endpoint='contract_cancel', view_func=ContractView.cancel, methods=['POST'])

v1_blueprints.add_url_rule(
    '/contract/list-signees/<string:contract_uuid>', endpoint='contract_list_signees',
    view_func=ContractSigneeView.list_signees, methods=['GET'])
v1_blueprints.add_url_rule(
    '/contract/get-signature-s3-link', endpoint='contract_get_s3_link',
    view_func=ContractSigneeView.get_signature_s3_link, methods=['POST'])
v1_blueprints.add_url_rule(
    '/contract/submit', endpoint='contract_submit',
    view_func=ContractSigneeView.submit, methods=['POST'])

v1_blueprints.add_url_rule(
    '/contract/track-open', endpoint='contract_track_open',
    view_func=ContractLogView.add_log_on_open, methods=['POST'])
v1_blueprints.add_url_rule(
    '/contract/list-logs/<string:contract_uuid>', endpoint='contract_list_logs',
    view_func=ContractLogView.list_logs, methods=['GET'])

v1_blueprints.add_url_rule(
    '/contract/get-dashboard-details/<string:account_uuid>', view_func=ContractView.get_dashboard_details,
    methods=['GET'])

v1_blueprints.add_url_rule(
    '/contract/verify-contract-token', view_func=ContractView.verify_contract_token,
    methods=['POST'])

v1_blueprints.add_url_rule(
    '/contract/get-ai-popup-response', endpoint='get-ai-popup-response',
    view_func=ContractView.get_ai_popup_response, methods=['POST'])
v1_blueprints.add_url_rule(
    '/contract/download-as-pdf/<string:contract_uuid>', view_func=ContractView.download_as_pdf,
    methods=['GET'])

# Client APIs:
v1_blueprints.add_url_rule(
    '/client/create-update', endpoint='client_create_update', view_func=ClientView.create_update, methods=['POST'])
v1_blueprints.add_url_rule(
    '/client/bulk-upload', endpoint='client_bulk_upload', view_func=ClientView.bulk_upload, methods=['POST'])
v1_blueprints.add_url_rule(
    '/client/list', endpoint='client_list', view_func=ClientView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/client/get/<string:client_uuid>', endpoint='client_get_by_uuid', view_func=ClientView.get_by_uuid,
    methods=['GET'])

# Super Admin APIs:
v1_blueprints.add_url_rule(
    'admin/client/list', endpoint='client_admin_list', view_func=DashboardView.client_list, methods=['GET'])
v1_blueprints.add_url_rule(
    'admin/get-dashboard-details', endpoint='client_dashboard_list', view_func=DashboardView.get_dashboard_details, methods=['GET'])

# Signee APIs:
v1_blueprints.add_url_rule(
    '/signee/create', endpoint='signee_create', view_func=SigneeView.create, methods=['POST'])
v1_blueprints.add_url_rule(
    '/signee/get-by-client/<string:client_uuid>', endpoint='signee_get_by_client_uuid',
    view_func=SigneeView.get_by_client_uuid, methods=['GET'])
v1_blueprints.add_url_rule(
    '/signee/get/<string:signee_uuid>', endpoint='signee_get_by_uuid',
    view_func=SigneeView.get_by_uuid, methods=['GET'])
v1_blueprints.add_url_rule(
    '/signee/update/<string:client_uuid>', endpoint='signee_update_by_client_uuid',
    view_func=SigneeView.update_by_client_uuid, methods=['POST'])

# Template APIs:
v1_blueprints.add_url_rule(
    '/template/create', view_func=create_template, methods=['POST'])
v1_blueprints.add_url_rule(
    '/template/get-template/<string:template_id>', view_func=get_template_by_id, methods=['GET'])
v1_blueprints.add_url_rule(
    '/template/update/<string:template_id>', view_func=update_template, methods=['POST'])
v1_blueprints.add_url_rule(
    '/template/get-all-templates', view_func=get_all_templates, methods=['GET'])
v1_blueprints.add_url_rule(
    '/template/get-all-templates-by-account/<string:account_id>', view_func=get_all_templates_by_account, methods=['GET'])

# Contact-Us APIs:
v1_blueprints.add_url_rule(
    '/contact-us/create', endpoint='contact_us_create', view_func=ContactUsView.create, methods=['POST'])
v1_blueprints.add_url_rule(
    '/contact-us/list', endpoint='contact_us_list', view_func=ContactUsView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/contact-us/get/<string:contact_us_request_uuid>', endpoint='contact_us_get_by_uuid',
    view_func=ContactUsView.get_by_uuid, methods=['GET'])

# Branding APIs:
v1_blueprints.add_url_rule(
    '/branding/get-branding-details/<string:account_uuid>', view_func=BrandingView.get_details, methods=['GET'])
v1_blueprints.add_url_rule(
    '/branding/add-branding-details/<string:account_uuid>', endpoint='branding_details_create', view_func=BrandingView.create, methods=['POST'])

# Billing APIs:
v1_blueprints.add_url_rule(
    '/billing/get-details', endpoint='get_billing_details', view_func=BillingView.get_details, methods=['GET'])

# Folder APIs:
v1_blueprints.add_url_rule(
    '/folder/create-update', endpoint='create_update_folder', view_func=FolderView.create_update, methods=['POST'])
v1_blueprints.add_url_rule(
    '/folder/list', endpoint='folder_list', view_func=FolderView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/folder/delete/<string:folder_uuid>', endpoint='folder_delete', view_func=FolderView.delete, methods=['POST'])

# Email Template APIs:
v1_blueprints.add_url_rule(
    '/email-template/list', endpoint='email_template_list', view_func=EmailTemplateView.list, methods=['GET'])
v1_blueprints.add_url_rule(
    '/email-template/get/<string:email_template_uuid>', endpoint='get_email_template', view_func=EmailTemplateView.get_by_uuid, methods=['GET'])
v1_blueprints.add_url_rule(
    '/email-template/update/<string:email_template_uuid>', endpoint='update_email_template', view_func=EmailTemplateView.update_by_uuid, methods=['POST'])
