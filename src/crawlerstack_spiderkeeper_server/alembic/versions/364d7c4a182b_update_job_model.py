"""update job model

Revision ID: 364d7c4a182b
Revises: 39ec906ccd00
Create Date: 2023-05-05 13:49:19.561330

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '364d7c4a182b'
down_revision = '39ec906ccd00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job', sa.Column('cpu_limit', sa.Integer(), nullable=False, comment='资源上限cpu核心数millicores微核',
                                   server_default='1000'))
    op.add_column('job', sa.Column('memory_limit', sa.Integer(), nullable=False, comment='资源上限内存大小Mi',
                                   server_default='1024'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('job', 'memory_limit')
    op.drop_column('job', 'cpu_limit')
    # ### end Alembic commands ###
