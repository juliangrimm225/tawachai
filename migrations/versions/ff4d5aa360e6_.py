"""empty message

Revision ID: ff4d5aa360e6
Revises: 
Create Date: 2020-06-16 16:40:13.867708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff4d5aa360e6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_timestamp'), ['timestamp'], unique=False)

    op.create_table('node',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=140), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('edge',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('sink_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['sink_id'], ['node.id'], ),
    sa.ForeignKeyConstraint(['source_id'], ['node.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('edge')
    op.drop_table('node')
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_timestamp'))

    op.drop_table('project')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    # ### end Alembic commands ###
