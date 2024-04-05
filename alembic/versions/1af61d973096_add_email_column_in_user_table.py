"""Add email column in user table

Revision ID: 1af61d973096
Revises: 7a639001d1da
Create Date: 2024-04-05 22:47:18.801683

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import VARCHAR

# revision identifiers, used by Alembic.
revision: str = "1af61d973096"
down_revision: Union[str, None] = "7a639001d1da"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("email", VARCHAR(), nullable=False, unique=True))


def downgrade() -> None:
    op.drop_column("user", "email")
