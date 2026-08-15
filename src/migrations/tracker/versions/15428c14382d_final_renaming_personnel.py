"""Final renaming personnel

Revision ID: 15428c14382d
Revises: 234712e32dc0
Create Date: 2026-08-09 17:12:11.530252

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "15428c14382d"
down_revision: Union[str, Sequence[str], None] = "234712e32dc0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "ranker",
        "personal_id",
        new_column_name="personnel_id",
    )
    op.drop_constraint(
        op.f("fk_ranker_personal_id"),
        "ranker",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "ranker_personnel_personnel_id_fk",
        "ranker",
        "personal",
        ["personnel_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ranker_personnel_personnel_id_fk",
        "ranker",
        type_="foreignkey",
    )

    op.alter_column(
        "ranker",
        "personnel_id",
        new_column_name="personal_id",
    )

    op.create_foreign_key(
        "fk_ranker_personal_id",
        "ranker",
        "personal",
        ["personal_id"],
        ["id"],
        ondelete="CASCADE",
    )
