"""empty message

Revision ID: b06393c983b2
Revises: 
Create Date: 2021-12-28 17:58:30.634380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b06393c983b2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('user_name', sa.String(), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('user_name')
    )
    op.create_table('deck',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('owner_name', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['owner_name'], ['user.user_name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('flashcard',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('front', sa.Text(), nullable=True),
    sa.Column('back', sa.Text(), nullable=True),
    sa.Column('deck_id', sa.Integer(), nullable=True),
    sa.Column('difficulty_level', sa.Integer(), nullable=True),
    sa.Column('previous_repetitions', sa.Integer(), nullable=True),
    sa.Column('previous_ease_factor', sa.Float(), nullable=True),
    sa.Column('interval', sa.Integer(), nullable=True),
    sa.Column('date_to_review', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('flashcard')
    op.drop_table('deck')
    op.drop_table('user')
    # ### end Alembic commands ###