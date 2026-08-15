"""initial

Revision ID: f8a0814a170b
Revises:
Create Date: 2026-08-15 13:27:13.974615

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f8a0814a170b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "backups",
        sa.Column("celery_id", sa.UUID(), nullable=False),
        sa.Column(
            "trigger_method",
            sa.Enum(
                "MANUAL", "SCHEDULED", name="backuptriggermethod", native_enum=False
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "RUNNING",
                "SUCCESS",
                "FAILURE",
                "UPLOADED",
                name="backupstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "backup_type",
            sa.Enum(
                "FULL",
                "INCREMENTAL",
                "DIFFERENTIAL",
                "LOGICAL",
                name="backuptype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("error_traceback", sa.String(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "meta",
        sa.Column("backup_id", sa.UUID(), nullable=False),
        sa.Column("database_alembic_version", sa.String(), nullable=False),
        sa.Column("app_version", sa.String(), nullable=False),
        sa.Column("algorithm", sa.String(), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("last_verified", sa.DateTime(), nullable=True),
        sa.Column("tool_used", sa.String(), nullable=False),
        sa.Column("tool_version", sa.String(), nullable=False),
        sa.Column("date_range_start", sa.DateTime(), nullable=False),
        sa.Column("date_range_end", sa.DateTime(), nullable=False),
        sa.Column("zip_filename", sa.String(), nullable=False),
        sa.Column("zip_path", sa.String(), nullable=False),
        sa.Column("zip_size_bytes", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["backup_id"], ["backups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("meta")
    op.drop_table("backups")
