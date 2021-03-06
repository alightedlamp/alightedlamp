"""empty message

Revision ID: c2e520d3a8ae
Revises: 11307cbf9190
Create Date: 2017-01-15 20:25:53.999277

"""

# revision identifiers, used by Alembic.
revision = 'c2e520d3a8ae'
down_revision = '11307cbf9190'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('instagram_user', sa.String(length=20), nullable=True))
    op.add_column('user', sa.Column('twitter_user', sa.String(length=20), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'twitter_user')
    op.drop_column('user', 'instagram_user')
    ### end Alembic commands ###
