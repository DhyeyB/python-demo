"""added_email_template_table

Revision ID: 0033
Revises: 0032
Create Date: 2023-11-15 12:51:25.951084

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.models.account import Account
from app.helpers.constants import EmailSubject, EmailTypes
from app.models.email_template import EmailTemplate
from app import logger
from app.helpers.utility import add_email_template
from app.helpers.constants import SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE, CONTRACT_CANCELLED, CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE, SEND_REMINDER_TO_SIGNEE

# revision identifiers, used by Alembic.
revision = '0033'
down_revision = '0032'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('email_template',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.String(), nullable=False),
    sa.Column('account_uuid', sa.String(), nullable=False),
    sa.Column('email_type', sa.String(), nullable=False),
    sa.Column('email_subject', sa.String(), nullable=False),
    sa.Column('email_body', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['account_uuid'], ['account.uuid'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    # ### end Alembic commands ###

    # # Create a new session
    # bind = op.get_bind()
    # session = Session(bind=bind)
    #
    # try:
    #     # Retrieve all accounts
    #     accounts = session.query(Account).all()
    #
    #     for account in accounts:
    #         # Create predefined templates
    #         add_email_template(account_uuid= account.uuid, email_type = EmailTypes.SEND_CONTRACT_TO_SIGNEE.value, email_subject= EmailSubject.SEND_CONTRACT_TO_SIGNEE.value, email_body=SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE)
    #         add_email_template(account_uuid= account.uuid, email_type = EmailTypes.CONTRACT_CANCELLED.value, email_subject= EmailSubject.CONTRACT_CANCELLED.value, email_body=CONTRACT_CANCELLED)
    #         add_email_template(account_uuid= account.uuid, email_type = EmailTypes.CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE.value, email_subject= EmailSubject.CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE.value, email_body=CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE)
    #         add_email_template(account_uuid= account.uuid, email_type = EmailTypes.SEND_REMINDER_TO_SIGNEE.value, email_subject= EmailSubject.SEND_REMINDER_TO_SIGNEE.value, email_body=SEND_REMINDER_TO_SIGNEE)
    #
    #     # Commit changes
    #     session.commit()
    #
    # except Exception as e:
    #     logger.info(f'Error during upgrade: {e}')
    #     session.rollback()
    # finally:
    #     session.close()



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('email_template')
    # ### end Alembic commands ###
