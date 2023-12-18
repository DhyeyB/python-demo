from app.helpers.constants import HttpStatusCode, SupportedImageTypes
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import field_type_validator
from app.helpers.utility import required_validator
from app.helpers.utility import send_json_response
from app.views.base_view import BaseView
from flask import request
from app.models.account import Account
from app.models.branding import Branding
from workers.s3_worker import upload_file_and_get_object_details
import os
from datetime import datetime
from magic import Magic
from app import config_data


class BrandingView(BaseView):
    @classmethod
    def create(cls, account_uuid: str):
        data = request.form
        field_types = {'cover_page': str}
        required_fields = ['cover_page']
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

        account = Account.get_by_uuid(account_uuid)

        if account is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                      error=None)

        company_logo = request.files.get('company_logo')

        if company_logo:
            # Check if the company_logo file is empty
            temp_path = os.path.join(config_data['UPLOAD_FOLDER'], company_logo.filename)  # type: ignore  # noqa: FKA100
            company_logo.save(temp_path)
            content_type = Magic(mime=True).from_file(temp_path)
            if content_type not in SupportedImageTypes.values():
                os.remove(temp_path)
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.ENTER_CORRECT_INPUT.value, data=None,
                                          error={
                                              'company_logo': ResponseMessageKeys.INVALID_IMAGE_FORMAT.value.format('Company logo', list(SupportedImageTypes.keys()))
                                          })

            time_stamp = str(int(datetime.now().timestamp()))
            file_name = 'company_logo_{}.{}'.format(
                time_stamp, temp_path.split('.')[-1])

            s3_folder_path = f'media/{account_uuid}/logo'.lower()
            s3_file_path = upload_file_and_get_object_details(file_path=temp_path,
                                                              file_name=file_name,
                                                              s3_folder_path=s3_folder_path)

        else:
            s3_file_path = None

        # Check if there are any existing branding details for the account
        existing_branding_details = Branding.query.filter_by(
            account_uuid=account.uuid).first()

        if existing_branding_details is None:
            # If there are no existing branding details, add branding details
            branding_uuid = Branding.create_uuid()
            branding_data = {
                'uuid': branding_uuid,
                'account_uuid': account.uuid,
                'company_logo': s3_file_path,
                'cover_page': data.get('cover_page'),
            }

            branding = Branding.add(branding_data)
            if branding is None:
                return send_json_response(http_status=HttpStatusCode.BAD_REQUEST.value, response_status=False,
                                          message_key=ResponseMessageKeys.FAILED.value, data=None,
                                          error=None)

            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.RECORD_ADDED_SUCCESSFULLY.value, data=None,
                                      error=None)

        else:
            # If there is existing branding detail, update the branding detail
            if company_logo:
                # if new company logo is passed, update the s3 path
                existing_branding_details.company_logo = s3_file_path
                existing_branding_details.cover_page = data.get('cover_page')
            else:
                # if new comapny logo is not pased, don't update the s3 path
                existing_branding_details.cover_page = data.get('cover_page')

            Branding.update()
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.RECORD_UPDATED_SUCCESSFULLY.value, data=None,
                                      error=None)

    @classmethod
    def get_details(cls, account_uuid: str):
        account = Account.get_by_uuid(account_uuid)
        if account is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=False,
                                      message_key=ResponseMessageKeys.ACCOUNT_NOT_FOUND.value, data=None,
                                      error=None)

        branding_details = Branding.get_branding_details_by_account_uuid(
            account.uuid)
        if branding_details is None:
            return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                      message_key=ResponseMessageKeys.SUCCESS.value, data={},
                                      error=None)

        branding_data = Branding.serialize(
            branding_details, single_object=True)

        return send_json_response(http_status=HttpStatusCode.OK.value, response_status=True,
                                  message_key=ResponseMessageKeys.SUCCESS.value, data=branding_data,
                                  error=None)
