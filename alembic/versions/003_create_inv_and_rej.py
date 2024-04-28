"""Added invitation

Revision ID: 64f699018569
Revises: 9ecaacad8de5
Create Date: 2024-04-27 19:20:51.002459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64f699018569'
down_revision: Union[str, None] = '9ecaacad8de5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('invitations',
    sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'CANCELLED', name='invitestatus'), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requests',
    sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'CANCELLED', name='requestsstatus'), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company_members',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )




def downgrade() -> None:

    op.drop_table('invitations')
    op.drop_table('company_members')
    op.drop_table('requests')
