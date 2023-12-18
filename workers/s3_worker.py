import os

from app import config_data
from app import logger
from app import S3_RESOURCE
from app.helpers.constants import TimeInSeconds
from magic import Magic
"""entity_type means user, obj_name can be user name and attachment_type can be profile_photo"""


def upload_file_and_get_object_details(file_path, file_name, s3_folder_path):
    """This method will upload file to bitbucket and return file details."""
    if config_data.get('APP_ENV') == 'DEV':
        extra_args = {'ContentType': Magic(mime=True).from_file(file_path)}
    else:
        extra_args = {'ACL': 'public-read',
                      'ContentType': Magic(mime=True).from_file(file_path)}

    S3_RESOURCE.Bucket(config_data.get('S3_BUCKET')).upload_file(  # type: ignore  # noqa: FKA100
        file_path, f'{s3_folder_path}{file_name}', ExtraArgs=extra_args)
    os.remove(file_path)
    return f'{s3_folder_path}{file_name}'


def get_presigned_url(path: str) -> str:
    """Generate a presigned URL to share for S3 object.

        :Bucket: S3 bucket name.
        :Key: Path where file is saved.
        :ExpiresIn: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns Blank String.
        """
    if path is None:
        return ''
    else:
        bucket_name = config_data.get('S3_BUCKET')
        try:
            response = S3_RESOURCE.meta.client.generate_presigned_url('get_object',
                                                                      Params={'Bucket': bucket_name,
                                                                              'Key': path},
                                                                      ExpiresIn=TimeInSeconds.TWO_DAYS.value)
            return response
        except Exception as error:
            logger.error(
                'Error while generating pre-signed url for : {}'.format(path))
            logger.error(
                error
            )
            return ''
