"""Added quizzes

Revision ID: f9e7ce2b5291
Revises: be443ddebed0
Create Date: 2024-05-02 19:55:04.268331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'f9e7ce2b5291'
down_revision: Union[str, None] = 'be443ddebed0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('results',
    sa.Column('quiz_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('score', sa.Float(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_answer',
    sa.Column('result_id', sa.UUID(), nullable=False),
    sa.Column('question_id', sa.UUID(), nullable=False),
    sa.Column('answer_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['answer_id'], ['answers.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['result_id'], ['results.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('user_answer')
    op.drop_table('results')

