"""Added payment table

Revision ID: 0010
Revises: 0009
Create Date: 2023-10-09 19:19:36.532637

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.String(), nullable=False),
    sa.Column('account_uuid', sa.String(), nullable=False),
    sa.Column('amount', sa.Numeric(), nullable=True),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('reference_payment_id', sa.String(length=255), nullable=True),
    sa.Column('response', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['account_uuid'], ['account.uuid'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('reference_payment_id'),
    sa.UniqueConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    # ### end Alembic commands ###
