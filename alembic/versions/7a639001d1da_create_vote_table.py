"""create_vote_table

Revision ID: 7a639001d1da
Revises: 0513c8fff6c7
Create Date: 2024-04-05 22:38:01.058349

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7a639001d1da"
down_revision: Union[str, None] = "0513c8fff6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vote",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("post_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("vote")
