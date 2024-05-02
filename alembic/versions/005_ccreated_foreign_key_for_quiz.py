"""Added quizzes

Revision ID: be443ddebed0
Revises: 163498ee547e
Create Date: 2024-05-01 19:35:16.610978

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be443ddebed0'
down_revision: Union[str, None] = '163498ee547e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('quizzes', sa.Column('company_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'quizzes', 'company', ['company_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_constraint(None, 'quizzes', type_='foreignkey')
    op.drop_column('quizzes', 'company_id')

