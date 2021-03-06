"""empty message

Revision ID: 9f875c90ef45
Revises: 1f2abb8612b4
Create Date: 2016-11-18 08:07:17.086655

"""

# revision identifiers, used by Alembic.
revision = '9f875c90ef45'
down_revision = '1f2abb8612b4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'about_me')
    ### end Alembic commands ###
