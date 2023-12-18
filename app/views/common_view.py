"""common view functions required by all modules"""

from datetime import datetime

from app import logger
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.decorators import api_time_logger
from app.helpers.decorators import token_required
from app.helpers.utility import send_json_response
from app.models.audit_log import AuditLog
from app.models.user import User
from flask import request


def get_health_check() -> tuple:
    """ API created for health check."""
    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                              message_key=ResponseMessageKeys.SUCCESS.value, data=None,
                              error=None)


@api_time_logger
@token_required
def list_audit_log(logged_in_user: User) -> tuple:
    """
    Returns list of audit logs with details like user_name, table_name, ip_address, etc. from audit log table.
    """
    page = request.args.get(key='page', default=None)
    pagination = request.args.get(key='pagination', default=None)
    sort = request.args.get(key='sort', default=None)
    user_id = request.args.get(key='user_id', default=None)
    action = request.args.get(key='action', default=None)
    start_date = request.args.get(key='start_date', default=None)
    end_date = request.args.get(key='end_date', default=None)
    user_ids = []
    if user_id:
        try:
            user_dict = user_id.split(',')
            user_ids = []
            for user_id in user_dict:
                if user_id:
                    user_ids.append(int(user_id))

        except Exception as error:
            logger.error(
                'Error while fetching Audit Log details : {}'.format(error))
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error={
                                          'user_id': 'Please enter valid user_id.'
                                      })

    if action:
        try:
            action = action.split(',')
        except Exception as error:
            logger.error(
                'Error while fetching Audit Log details : {}'.format(error))
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error={
                                          'action': 'Please enter valid action.'
                                      })

    if start_date:
        try:
            start_date = datetime.strptime(start_date + 'T00:00:00', '%d/%m/%YT%H:%M:%S')  # type: ignore  # noqa: FKA100
        except Exception as error:
            logger.error(
                'Error while fetching Audit Log details : {}'.format(error))
            logger.error('Error while fetching Audit Log details for user id  : {}'.format(
                logged_in_user.id))
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error={
                                          'start_date': 'Please enter valid start_Date.'
                                      })
    if end_date:
        try:
            end_date = datetime.strptime(end_date + 'T23:59:59', '%d/%m/%YT%H:%M:%S')  # type: ignore  # noqa: FKA100
        except Exception as error:
            logger.error(
                'Error while fetching Audit Log details : {}'.format(error))
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                      error={
                                          'end_date': 'Please enter valid end_date.'
                                      })
    audit_logs = AuditLog.get_logs(sort=sort, page=page, pagination=pagination, action=action,
                                   user_id=user_ids, start_date=start_date, end_date=end_date)

    current_page_count = audit_logs.count()
    audit_logs = audit_logs.all()
    user_dict = User.get_all_user_detail()
    audit_log_list = AuditLog.serialize(audit_logs=audit_logs)

    total_count = AuditLog.get_logs(
        action=action, user_id=user_id, start_date=start_date, end_date=end_date).count()
    data = {'result': audit_log_list, 'objects': {'user': user_dict}, 'current_page_count': current_page_count,
            'current_page': 1 if page is None else int(page),
            'next_page': '' if page is None else int(page) + 1, 'total_count': total_count} if current_page_count > 0 else None

    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True, message_key=ResponseMessageKeys.SUCCESS.value, data=data, error=None)


@api_time_logger
@token_required
def get_audit_log_details(logged_in_user: User) -> tuple:
    """
    Returns audit log details like action, args, body, created_at, headers, ip, method, object_id, etc.
    from audit log table of the passed id.
    """
    audit_log_id = request.args.get(key='id', default=None)
    if audit_log_id is None:
        return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False, message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None, error={
            'audit_log_id': 'audit_log_id is required.'
        })

    audit_log = AuditLog.get_by_id(int(audit_log_id))
    user = ''
    if audit_log.user_id:
        user = User.get_by_id(audit_log.user_id)
    data_dict = {
        'id': audit_log.id,
        'user_name': user.full_name if user else user,
        'object_id': audit_log.object_id,
        'action': audit_log.action,
        'state_before': audit_log.state_before,
        'state_after': audit_log.state_after,
        'method': audit_log.method,
        'url': audit_log.url,
        'headers': audit_log.headers,
        'body': audit_log.body,
        'args': audit_log.args,
        'ip': audit_log.ip,
        'created_at': audit_log.created_at
    }

    if audit_log is None:
        logger.error('Error while fetching Audit Log details for user id  : {}'.format(
            logged_in_user.id))
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                  message_key=ResponseMessageKeys.EMAIL_DETAILS_NOT_FOUND.value, data=None, error=None)
    return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                              message_key=ResponseMessageKeys.SUCCESS.value, data={'api_log_data': data_dict}, error=None)
