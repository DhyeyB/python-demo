"""Updated plans table

Revision ID: 0004
Revises: 0003
Create Date: 2023-09-27 15:49:58.591141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plan', sa.Column('period', sa.String(), nullable=False))
    # op.drop_column('plan', 'yearly_price')
    # op.drop_column('plan', 'monthly_price')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('plan', sa.Column('monthly_price', sa.NUMERIC(), autoincrement=False, nullable=False))
    # op.add_column('plan', sa.Column('yearly_price', sa.NUMERIC(), autoincrement=False, nullable=False))
    op.drop_column('plan', 'period')
    # op.drop_column('plan', 'description')
    # op.drop_column('plan', 'amount')
    # op.drop_column('plan', 'status')
    # ### end Alembic commands ###
