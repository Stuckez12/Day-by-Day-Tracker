"""Converting personal into an account table

Revision ID: 6350c32c93b3
Revises: a73d754c162c
Create Date: 2026-04-21 21:28:03.200018

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

from src.common.password_hash import pwd_hash

# revision identifiers, used by Alembic.
revision: str = "6350c32c93b3"
down_revision: Union[str, Sequence[str], None] = "a73d754c162c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("personal", sa.Column("email", sa.String(), nullable=True))
    op.add_column("personal", sa.Column("password", sa.String(), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(text("SELECT id FROM personal")).fetchall()

    for i, row in enumerate(rows):
        unique_email = f"user{i+1}@example.com"

        conn.execute(
            text("""
                UPDATE personal
                SET email = :email,
                    password = :password
                WHERE id = :id
            """),
            {
                "id": row.id,
                "email": unique_email,
                "password": pwd_hash.hash("password"),
            },
        )

    op.alter_column("personal", "email", nullable=False)
    op.alter_column("personal", "password", nullable=False)
    op.create_unique_constraint("unq_cns_email", "personal", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("unq_cns_email", "personal", type_="unique")
    op.drop_column("personal", "password")
    op.drop_column("personal", "email")
