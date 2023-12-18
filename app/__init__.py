"""This file initializes Application."""
from functools import partial
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import subprocess
import sys
import traceback
from app.helpers.constants import HttpStatusCode
from app.helpers.constants import QueueName
from app.helpers.constants import ResponseMessageKeys
import boto3
from botocore.client import Config
from cloudwatch import cloudwatch
from flask import Flask
from flask import jsonify
from flask_limiter import Limiter
from flask_limiter import RequestLimit
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
import redis
from rq import Queue
from rq_scheduler import Scheduler
import stripe
import yaml

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
media_dir = os.path.join(base_dir, 'media')  # type: ignore  # noqa: FKA100
if not os.path.exists(media_dir):
    os.makedirs(media_dir)

# Initialising the configuration variable
environment = os.environ.get('APP_ENV')

ENVIRONMENT_LIST = ['prod', 'staging', 'dev']
AWS_BUCKET = None
if environment in ENVIRONMENT_LIST:
    config_data = yaml.safe_load(
        boto3.client(
            's3').get_object(
            Bucket=f'vs-backend-{environment}-config',
            Key=f'vs-backend-config-{environment}.yaml'
        ).get('Body'))
    AWS_BUCKET = f'vs-backend-{environment}-config'
else:
    with open(file='config/config.yml') as config_file:
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)


SHELL_COMMAND_TO_FETCH_TASK_ID = 'curl -s "$ECS_CONTAINER_METADATA_URI_V4/task" | jq -r ".TaskARN" | cut -d "/" -f 3'
TASK_ID = subprocess.getoutput(SHELL_COMMAND_TO_FETCH_TASK_ID)


# Initializing logging configuration object
formatter = logging.Formatter(
    '%(asctime)s: %(levelname)s {%(filename)s:%(lineno)d} -> %(message)s'
)

logger = logging.getLogger(__name__)

if environment in ENVIRONMENT_LIST:
    handler = cloudwatch.CloudwatchHandler(
        region=config_data.get('CLOUD_WATCH_REGION'),
        log_group=config_data.get('LOG_GROUP'),
        log_stream=config_data.get('LOG_STREAM'))
    handler.setFormatter(formatter)
    logger.addHandler(handler)
else:
    handler = TimedRotatingFileHandler(
        config_data.get('LOG_FILE_PATH'),
        when='midnight',
        interval=1,
        backupCount=7)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.error = partial(logger.error, exc_info=True)
logger.info = partial(logger.info, exc_info=True)
logger.warning = partial(logger.warning, exc_info=True)
logger.exception = partial(logger.exception, exc_info=True)
os.environ['OPENAI_LOG'] = 'debug'

COGNITO_CLIENT = boto3.client(
    'cognito-idp',
    region_name=config_data.get('COGNITO_REGION'),
    aws_access_key_id=config_data.get('AWS_KEY'),
    aws_secret_access_key=config_data.get('AWS_SECRET')
)

S3_RESOURCE = boto3.resource(
    's3',
    region_name=config_data.get('S3_REGION'),
    aws_access_key_id=config_data.get('AWS_KEY'),
    aws_secret_access_key=config_data.get('AWS_SECRET')
)

stripe_keys = {
    'secret_key': config_data['STRIPE_SECRET_KEY'],
    'publishable_key': config_data['STRIPE_PUBLISHABLE_KEY'],
}

stripe.api_key = stripe_keys['secret_key']


def ratelimit_handler(request_limit: RequestLimit) -> tuple:
    """
        This method will create custom json response for error 429 (Too Many Requests).
    """
    limit_string = request_limit.limit.limit
    time_limit = str(limit_string).split('per')[1]
    # Here, we get limit value in string like 1 per 30 seconds so, for getting time limit we are splitting above string.
    return jsonify({'status': False,
                    'message': ResponseMessageKeys.PLEASE_TRY_AFTER_SECONDS.value.format(time_limit)}), HttpStatusCode.TOO_MANY_REQUESTS.value


def create_app():
    """
    Create a Flask application instance. Register blueprints and updates celery configuration.

        :return: application instance
    """
    try:
        application = Flask(__name__, instance_relative_config=True)
        application.config.from_object(config_data)
        # CORS(application, resources={r'/api/*': {'origins': '*'}})
        # Global error handler for error code 429 (Too Many Requests)
        application.register_error_handler(429, ratelimit_handler)  # type: ignore  # noqa: FKA100
        app_set_configurations(application=application,
                               config_data=config_data)
        initialize_extensions(application)
        register_blueprints(application)
        register_swagger_blueprints(application)

        return application

    except Exception as exception_error:
        logger.error('Unable to create flask app instance : '
                     + str(exception_error))


def initialize_extensions(application):
    """
    Initialize extensions.
    :param application:
    :return:
    """
    try:
        db.init_app(application)
        migrate = Migrate(app=application, db=db, compare_type=True)
        return db, migrate

    except Exception as exception_error:
        logger.error('Unable to initialize extensions : '
                     + str(exception_error))


def register_blueprints(application):
    """
    Registers blueprints.
    :param application:
    :return: None
    """
    try:
        from app.views import v1_blueprints
        application.register_blueprint(v1_blueprints, url_prefix='/api/v1')

    except Exception as exception_error:
        trace = traceback.extract_tb(sys.exc_info()[2])
        # Add the event to the log
        output = 'Unable to register blueprints: %s.\n' % (exception_error)
        output += '\tTraceback is:\n'
        for (file, linenumber, affected, line) in trace:
            output += '\t> Error at function %s\n' % (affected)
            output += '\t  At: {}:{}\n'.format(file, linenumber)
            output += '\t  Source: %s\n' % (line)
        output += '\t> Exception: %s\n' % (exception_error)
        logger.error('Exception Stack Trace')
        logger.error(output)
        logger.error('=========END=========')


def register_swagger_blueprints(application):
    """
    Registers swagger blueprints.
    :param application:
    :return: None
    """
    try:
        swagger_url = '/api-docs/'
        api_url = '/static/swagger_json/swagger.json'
        swagger_config = {'app_name': 'Virtusign', 'deepLinking': False, }
        swagger_blueprint = get_swaggerui_blueprint(
            base_url=swagger_url,
            api_url=api_url,
            config=swagger_config
        )
        application.register_blueprint(
            swagger_blueprint, url_prefix=swagger_url)

    except Exception as exception_error:
        logger.error('Unable to register blueprints : '
                     + str(exception_error))


def app_set_configurations(application, config_data):
    """This method is used to setting configuration data from config.yml"""
    try:
        for config in config_data:
            application.config[config] = config_data[config]

    except Exception as exception_error:
        logger.error('problem setting app configuration : '
                     + str(exception_error))


app = Flask(__name__)
app_set_configurations(application=app, config_data=config_data)
db = SQLAlchemy(app, session_options={'expire_on_commit': False})
migrate = Migrate(app=app, db=db, compare_type=True)
# CORS(app, resources={r'/api/*': {'origins': '*'}})
r = redis.Redis(host=config_data.get('REDIS').get('HOST'), port=config_data.get(
    'REDIS').get('PORT'), db=config_data.get('REDIS').get('DB'))
send_mail_q = Queue(QueueName.SEND_MAIL, connection=r)
reminder_mail_q = Queue(QueueName.REMINDER_MAIL, connection=r)
delete_accounts_mail_q = Queue(QueueName.DELETE_ACCOUNT, connection=r)
check_subscription_expiry_q = Queue(
    QueueName.CHECK_SUBSCRIPTION_EXPIRY, connection=r)
reminder_scheduler = Scheduler(queue=reminder_mail_q, connection=r)
delete_accounts_scheduler = Scheduler(
    queue=delete_accounts_mail_q, connection=r)
check_subscription_expiry_scheduler = Scheduler(
    queue=check_subscription_expiry_q, connection=r)


def clear_scheduler():
    """ Method to delete scheduled jobs in scheduler. """
    scheduler = Scheduler(connection=r)
    for job in scheduler.get_jobs():
        scheduler.cancel(job)


def send_reminder_mail_scheduler(reminder_scheduler):
    """
            Scheduler to send reminder mail to signees whose signed status is pending.
            This scheduler runs every day at 5:15 AM UTC and sends email to signees.
        """
    from app.views import ContractView
    try:
        reminder_scheduler.cron(cron_string='15 5 * * *',
                                func=ContractView.send_reminder_to_signees, args=[],
                                repeat=None)
        logger.info('SCHEDULED JOB: send_reminder_to_signees')
    except Exception as exception_error:
        logger.error('\n%s' % exception_error)


def delete_accounts(delete_accounts_scheduler):
    """
        Scheduler for deleting accounts as per scheduled date.
        This scheduler runs every day at 12 PM UTC.
    """
    from app.views import AccountView
    try:
        delete_accounts_scheduler.cron(cron_string='0 12 * * *',
                                       func=AccountView.delete_scheduled_accounts, args=[],
                                       repeat=None)
        logger.info('SCHEDULED JOB: delete_accounts_scheduler')
    except Exception as exception_error:
        logger.error('\n%s' % exception_error)


def check_subscription_expiry(check_subscription_expiry_scheduler):
    """
        Scheduler for check subscription expiry for all accounts.
        This scheduler runs every day at 12 AM UTC.
    """
    from app.models.subscription import Subscription
    try:
        check_subscription_expiry_scheduler.cron(cron_string='0 0 * * *',
                                                 func=Subscription.update_all_expired_subscriptions, args=[],
                                                 repeat=None)
        logger.info('SCHEDULED JOB: check_subscription_expiry_scheduler')
    except Exception as exception_error:
        logger.error('\n%s' % exception_error)


clear_scheduler()

send_reminder_mail_scheduler(reminder_scheduler)
delete_accounts(delete_accounts_scheduler)
check_subscription_expiry(check_subscription_expiry_scheduler)


limiter = Limiter(app=app, key_func=None, strategy=config_data.get('STRATEGY'),  # Creating instance of Flask-Limiter for rate limiting.
                  key_prefix=config_data.get('KEY_PREFIX'), storage_uri='redis://{}:{}/{}'.format(
    config_data.get('REDIS').get('HOST'), config_data.get('REDIS').get('PORT'), config_data.get('RATE_LIMIT').get('REDIS_DB')))
