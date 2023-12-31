"""updated_email_templates_body

Revision ID: 0039
Revises: 0038
Create Date: 2023-11-15 16:08:25.951084

"""
from alembic import op
from sqlalchemy import text
from app.helpers.constants import SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE, SEND_REMINDER_TO_SIGNEE

# revision identifiers, used by Alembic.
revision = '0039'
down_revision = '0038'
branch_labels = None
depends_on = None


def upgrade():
    # Update predefined templates
    op.execute(text('''
        UPDATE email_template
        SET email_body = :template_value
        WHERE email_type = 'SEND_CONTRACT_TO_SIGNEE'
    ''').bindparams(template_value=SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE))

    op.execute(text('''
        UPDATE email_template
        SET email_body = :template_value
        WHERE email_type = 'SEND_REMINDER_TO_SIGNEE'
    ''').bindparams(template_value=SEND_REMINDER_TO_SIGNEE))

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
