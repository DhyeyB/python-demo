"""updated_service_name_nullbale_in_contract_table

Revision ID: 0031
Revises: 0030
Create Date: 2023-11-08 13:55:00.187481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0031'
down_revision = '0030'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contract', 'service_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contract', 'service_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
