"""post table foreign key user_id on user.id

Revision ID: 0513c8fff6c7
Revises: e05c97b4a6b3
Create Date: 2024-04-05 22:35:05.675927

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0513c8fff6c7"
down_revision: Union[str, None] = "e05c97b4a6b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("post", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_post_user_id", "user", ["user_id"], ["id"], ondelete="CASCADE"
        )


def downgrade() -> None:
    with op.batch_alter_table("post", schema=None) as batch_op:
        batch_op.drop_constraint("fk_post_user_id", type_="foreignkey")
