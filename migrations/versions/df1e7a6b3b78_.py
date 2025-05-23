"""empty message

Revision ID: df1e7a6b3b78
Revises: 4a3de6011bb9
Create Date: 2025-04-05 15:19:45.229568

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'df1e7a6b3b78'
down_revision = '4a3de6011bb9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('landlord_details', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('vacant_houses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacant_houses', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('landlord_details', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', mysql.TEXT(), nullable=False))

    # ### end Alembic commands ###
