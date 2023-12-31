"""created_at and updated_at added in ContractSignee

Revision ID: 0020
Revises: 0019
Create Date: 2023-10-18 18:18:32.173743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0020'
down_revision = '0019'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contract_signee', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('contract_signee', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contract_signee', 'updated_at')
    op.drop_column('contract_signee', 'created_at')
    # ### end Alembic commands ###
