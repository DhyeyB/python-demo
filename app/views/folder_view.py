"""Contains user related API definitions."""
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import required_validator, field_type_validator, get_pagination_meta
from app.helpers.utility import send_json_response
from app.models.folder import Folder
from app.views.base_view import BaseView
from flask import request
from app.models.contract import Contract
from app.helpers.utility import is_valid_folder_name


class FolderView(BaseView):

    @classmethod
    def create_update(cls):
        data = request.get_json(force=True)
        field_types = {'folder_name': str}
        required_fields = ['folder_name']
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

        folder_uuid = data.get('folder_uuid')
        user_obj = FolderView.get_logged_in_user(request=request)
        folder_name = data.get('folder_name').strip()

        is_name_valid = is_valid_folder_name(folder_name)
        if not is_name_valid:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.INVALID_FOLDER_NAME.value, data=None,
                                      error=None)

        folder_name_slug = folder_name.lower()

        if folder_uuid is not None:
            existing_folder_obj = Folder.get_by_uuid(folder_uuid)
            if existing_folder_obj is None:
                return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                          message_key=ResponseMessageKeys.FOLDER_NOT_FOUND.value, data=None,
                                          error=None)

            if Folder.check_if_folder_exist(account_uuid=user_obj.account_uuid, folder_name_slug=folder_name_slug, folder_uuid=folder_uuid):
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.FOLDER_ALREADY_EXISTS.value.format(data.get('folder_name')), data=None,
                                          error=None)

            existing_folder_obj.folder_name = folder_name
            existing_folder_obj.folder_name_slug = folder_name_slug

            Folder.update()

            folder = Folder.get_by_uuid(folder_uuid)
            folder_obj = Folder.serialize(folder)

            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=folder_obj,
                                      error=None)

        if Folder.check_if_folder_exist(account_uuid=user_obj.account_uuid, folder_name_slug=folder_name_slug):
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FOLDER_ALREADY_EXISTS.value.format(data.get('folder_name')), data=None,
                                      error=None)

        folder_data = {
            'uuid': Folder.create_uuid(),
            'account_uuid': user_obj.account_uuid,
            'folder_name': folder_name,
            'folder_name_slug': folder_name_slug
        }

        folder = Folder.add(folder_data)

        if folder is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FAILED.value, data=None,
                                      error=None)

        folder_obj = Folder.serialize(folder)
        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.RECORD_ADDED_SUCCESSFULLY.value, data=folder_obj,
                                  error=None)

    @classmethod
    def list(cls):
        page = request.args.get('page')
        size = request.args.get('size')
        q = request.args.get('q')
        sort = request.args.get('sort')

        user_obj = FolderView.get_logged_in_user(request=request)

        folder_objs, objects_count = Folder.get_folder_list(
            account_uuid=user_obj.account_uuid, page=page, q=q, size=size, sort=sort)
        folder_list = Folder.serialize(folder_objs)
        data = {'result': folder_list,
                'pagination_metadata': get_pagination_meta(current_page=1 if page is None else int(page),
                                                           page_size=objects_count if size is None else int(
                    size),
                    total_items=objects_count)}

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=data,
                                  error=None)

    @classmethod
    def delete(cls, folder_uuid: str):
        """Delete Folder"""
        user_obj = cls.get_logged_in_user(request)
        account_uuid = user_obj.account_uuid
        folder_obj = Folder.get_by_uuid(folder_uuid)
        if folder_obj is None:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FOLDER_NOT_FOUND.value, data=None,
                                      error=None)

        contract_count_in_folder = Contract.get_folder_contact_count(
            account_uuid=account_uuid, folder_uuid=folder_uuid)

        if contract_count_in_folder > 0:
            return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                      message_key=ResponseMessageKeys.FOLDER_HAVE_CONTRACT_ASCCOCIATED_AND_CANT_BE_DELETED.value, data=None,
                                      error=None)

        Folder.delete_by_uuid(folder_uuid)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.RECORD_DELETED_SUCCESSFULLY.value, data=None,
                                  error=None)
