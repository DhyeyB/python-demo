"""duration_type and payment_frequency added in contract

Revision ID: 0046
Revises: 0045
Create Date: 2023-12-11 11:58:05.259501

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0046'
down_revision = '0045'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contract', sa.Column('duration_type', sa.String(), server_default='month', nullable=True))
    op.add_column('contract', sa.Column('payment_frequency', sa.String(), server_default='one time', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contract', 'payment_frequency')
    op.drop_column('contract', 'duration_type')
    # ### end Alembic commands ###
