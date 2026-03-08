"""Performance: change controls.status from VARCHAR to VARCHAR-backed Enum

Changes controls.status from a plain String(50) column to a VARCHAR column
backed by the ControlStatus enum (native_enum=False).  Because native_enum
is False, the underlying PostgreSQL column stays VARCHAR and no native ENUM
type is created.  The column length is trimmed to match the longest valid
ControlStatus value ("not_applicable" = 14 chars), which both saves storage
and makes the indexed column more cache-efficient.

Revision ID: f1a2b3c4d5e6
Revises: 8f1c2d3e4f5a
Create Date: 2026-03-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "8f1c2d3e4f5a"
branch_labels = None
depends_on = None

# The longest ControlStatus value is "not_applicable" (14 chars).
# Leave a small margin so adding values later doesn't require another migration.
_NEW_STATUS_LEN = 20
_OLD_STATUS_LEN = 50


def upgrade() -> None:
    # Shrink the column to a tighter VARCHAR length that still covers all
    # valid ControlStatus values.  PostgreSQL accepts this without data loss
    # as long as all existing values fit within the new length.
    op.alter_column(
        "controls",
        "status",
        existing_type=sa.String(_OLD_STATUS_LEN),
        type_=sa.String(_NEW_STATUS_LEN),
        existing_nullable=True,
    )
    # Ensure the index exists (idempotent – earlier migration already created
    # it, but this guard ensures the index is present regardless of the
    # migration order applied in any environment).
    op.create_index("ix_controls_status", "controls", ["status"], unique=False, if_not_exists=True)


def downgrade() -> None:
    op.alter_column(
        "controls",
        "status",
        existing_type=sa.String(_NEW_STATUS_LEN),
        type_=sa.String(_OLD_STATUS_LEN),
        existing_nullable=True,
    )
