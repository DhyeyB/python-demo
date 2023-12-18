from app import logger
from app.helpers.constants import ResponseMessageKeys
from app.helpers.utility import send_json_response
from flask.views import View


class BaseView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_logged_in_user(request):
        try:
            user_obj = getattr(request, 'user')
            return user_obj
        except AttributeError as e:
            # if user is not logged in
            logger.error(e)
            return send_json_response(http_status=401, response_status=False,
                                      message_key=ResponseMessageKeys.ACCESS_DENIED.value)
