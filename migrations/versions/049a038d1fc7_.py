"""empty message

Revision ID: 049a038d1fc7
Revises: 
Create Date: 2023-04-26 17:41:24.819568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '049a038d1fc7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stocks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stocktype', sa.String(length=16), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stocks', schema=None) as batch_op:
        batch_op.drop_column('stocktype')

    # ### end Alembic commands ###