"""initial

Revision ID: 7249263b6e93
Revises: 
Create Date: 2025-04-18 08:36:54.724795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7249263b6e93'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hourly_bitcoin_prices',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('unix_timestamp', sa.BigInteger(), nullable=False),
    sa.Column('high', sa.Float(), nullable=False),
    sa.Column('low', sa.Float(), nullable=False),
    sa.Column('open', sa.Float(), nullable=False),
    sa.Column('close', sa.Float(), nullable=False),
    sa.Column('volumefrom', sa.Float(), nullable=False),
    sa.Column('volumeto', sa.Float(), nullable=False),
    sa.CheckConstraint('unix_timestamp >= 1279328400', name='valid_unix_timestamp'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hourly_bitcoin_prices_id'), 'hourly_bitcoin_prices', ['id'], unique=False)
    op.create_index(op.f('ix_hourly_bitcoin_prices_unix_timestamp'), 'hourly_bitcoin_prices', ['unix_timestamp'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_hourly_bitcoin_prices_unix_timestamp'), table_name='hourly_bitcoin_prices')
    op.drop_index(op.f('ix_hourly_bitcoin_prices_id'), table_name='hourly_bitcoin_prices')
    op.drop_table('hourly_bitcoin_prices')
    # ### end Alembic commands ###
