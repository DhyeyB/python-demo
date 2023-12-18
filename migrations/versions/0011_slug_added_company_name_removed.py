"""client company_name removed and slug added

Revision ID: 0011
Revises: 0010
Create Date: 2023-10-10 11:56:02.307650

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('client', sa.Column('legal_name_slug', sa.String(), nullable=False))
    op.drop_column('client', 'company_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('client', sa.Column('company_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('client', 'legal_name_slug')
    # ### end Alembic commands ###
