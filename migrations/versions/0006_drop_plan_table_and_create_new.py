"""Updated plans table

Revision ID: 0006
Revises: 0005
Create Date: 2023-09-27 15:49:58.591141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None



def upgrade():
    op.drop_table('subscription')
    op.drop_table('plan')

    op.create_table('plan',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('reference_plan_id', sa.String(length=255), nullable=True),
    sa.Column('period', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('amount', sa.Numeric(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('discount', sa.Numeric(), nullable=False),
    sa.Column('feature', sa.JSON(), nullable=False),
    sa.Column('deactivated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('reference_plan_id')
    )

    op.create_table('subscription',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('account_id', sa.BigInteger(), nullable=False),
    sa.Column('plan_id', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('trial_period_end_date', sa.DateTime(), nullable=False),
    sa.Column('deactivated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('subscription')
    op.drop_table('plan')
