"""Added quizzes

Revision ID: 163498ee547e
Revises: 64f699018569
Create Date: 2024-05-01 01:01:59.607163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '163498ee547e'
down_revision: Union[str, None] = '64f699018569'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('quizzes',
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('frequency_days', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('questions',
    sa.Column('question_text', sa.String(length=255), nullable=False),
    sa.Column('quiz_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('answers',
    sa.Column('answer_text', sa.String(length=255), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('question_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_foreign_key(None, 'actions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'actions', 'company', ['company_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('_company_user_uc', 'company_members', ['company_id', 'user_id'])
    op.create_foreign_key(None, 'company_members', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'company_members', 'company', ['company_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint(None, 'company_members', type_='foreignkey')
    op.drop_constraint(None, 'company_members', type_='foreignkey')
    op.drop_constraint('_company_user_uc', 'company_members', type_='unique')
    op.drop_constraint(None, 'actions', type_='foreignkey')
    op.drop_constraint(None, 'actions', type_='foreignkey')
    op.drop_table('answers')
    op.drop_table('questions')
    op.drop_table('quizzes')
