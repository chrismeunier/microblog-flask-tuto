"""add language to posts

Revision ID: 9538a2f9cedf
Revises: aed9f5ae91e6
Create Date: 2025-04-25 19:04:00.073922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9538a2f9cedf'
down_revision = 'aed9f5ae91e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('language', sa.String(length=5), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('language')

    # ### end Alembic commands ###
