"""Add title, description and published column in post

Revision ID: 1b2a290575f2
Revises: 1af61d973096
Create Date: 2024-04-05 22:49:00.132371

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b2a290575f2"
down_revision: Union[str, None] = "1af61d973096"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("post", sa.Column("title", sa.String(), nullable=False))
    op.add_column("post", sa.Column("description", sa.String(), nullable=True))
    op.add_column(
        "post",
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("post", "published")
    op.drop_column("post", "description")
    op.drop_column("post", "title")
