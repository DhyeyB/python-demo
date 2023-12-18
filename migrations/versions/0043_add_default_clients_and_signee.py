"""add default client and signee in all account

Revision ID: 0043
Revises: 0042
Create Date: 2023-11-15 12:51:25.951084

"""
from slugify import slugify

from app import logger
from app.models.account import Account
from app.models.client import Client
from app.models.signee import Signee
from app.models.user import User

# revision identifiers, used by Alembic.
revision = '0043'
down_revision = '0042'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # try:
    #     # Retrieve all accounts
    #     all_accounts = Account.get_all_with_not_null_legal_name_display_name()
    #
    #     for account_obj in all_accounts:
    #         account_owner = User.get_primary_user_of_account(
    #             account_uuid=account_obj.uuid)
    #         if account_owner is None:
    #             continue
    #         legal_name_slug = slugify(account_obj.legal_name)
    #         if Client.check_if_client_exits(account_uuid=account_obj.uuid, legal_name_slug=legal_name_slug):
    #             logger.info('Client already exists!')
    #             continue
    #
    #         client_data = {
    #             'uuid': Client.create_uuid(),
    #             'account_uuid': account_obj.uuid,
    #             'created_by': account_owner.uuid,
    #             'legal_name': account_obj.legal_name,
    #             'legal_name_slug': legal_name_slug,
    #             'display_name': account_obj.display_name,
    #             'email': account_owner.email.lower(),
    #             'phone': account_owner.mobile_number,
    #             'street_name': account_obj.address,
    #             'postal_code': account_obj.postal_code,
    #             'city': account_obj.city,
    #             'state': account_obj.state,
    #             'country': account_obj.country,
    #             'is_account_client': True
    #         }
    #         client = Client.add(client_data)
    #
    #         signee_data = {
    #             'uuid': Signee.create_uuid(),
    #             'client_uuid': client.uuid,
    #             'account_uuid': account_obj.uuid,
    #             'created_by': account_owner.uuid,
    #             'full_name': account_owner.first_name + ' ' + account_owner.last_name,
    #             'job_title': None,
    #             'email': account_owner.email.lower(),
    #             'signing_sequence': None
    #         }
    #         Signee.add(signee_data)
    #
    # except Exception as e:
    #     logger.info(f'Error during upgrade: {e}')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
