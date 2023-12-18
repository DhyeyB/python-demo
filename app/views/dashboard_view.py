"""Contains Client related API definitions."""

from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.constants import UserType
from app.helpers.utility import get_pagination_meta
from app.helpers.utility import send_json_response
from app.views.base_view import BaseView
from flask import request
from app.models.contract import Contract
from app.models.client import Client
from app.models.signee import Signee
from app.models.account import Account
from app.helpers.constants import ContractStatus


class DashboardView(BaseView):
    @classmethod
    def client_list(cls):
        """
        Get all clients according to given page, size, sort and q(filter query). .
        """
        user_obj = DashboardView.get_logged_in_user(request=request)

        if user_obj.user_type != UserType.SUPER_ADMIN.value:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.NOT_ALLOWED.value, data=None,
                                      error=None)

        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        client_objs, objects_count = Contract.get_all_client_with_contract_count(
            q=q, sort=sort, page=page, size=size)
        client_list = [row._asdict() for row in client_objs]

        data = {'result': client_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=objects_count if size is None else int(
                                                               size),
                                                           total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def get_dashboard_details(cls):
        """
        Get super admin dahboard details .
        """
        user_obj = DashboardView.get_logged_in_user(request=request)

        if user_obj.user_type != UserType.SUPER_ADMIN.value:
            return send_json_response(http_status=HttpStatusCode.UNAUTHORIZED.value, response_status=False,
                                      message_key=ResponseMessageKeys.NOT_ALLOWED.value, data=None,
                                      error=None)

        start_date_param = request.args.get('start_date')
        end_date_param = request.args.get('end_date')

        # Initialize the timestamps with None
        start_timestamp = None
        end_timestamp = None

        # Check if start_date_param is not None and is a valid integer
        if start_date_param:
            start_timestamp = int(start_date_param)

        # Check if end_date_param is not None and is a valid integer
        if end_date_param:
            end_timestamp = int(end_date_param)

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

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)
