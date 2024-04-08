"""init

Revision ID: cf03bd6bae1d
Revises:
Create Date: 2024-04-03 19:41:48.871555

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cf03bd6bae1d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    projects_table = op.create_table(
        "projects",
        sa.Column("id", sa.Integer, primary_key=True),
        # TODO does the uniqueness constraint need to be named
        sa.Column("name", sa.String, nullable=False, unique=True),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_table(
        "traces",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_rowid", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        # TODO(mikeldking): might not be the right place for this
        sa.Column("session_id", sa.String, nullable=True),
        sa.Column("trace_id", sa.String, nullable=False, unique=True),
        sa.Column("start_time", sa.DateTime(), nullable=False, index=True),
        sa.Column("end_time", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "spans",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("trace_rowid", sa.Integer, sa.ForeignKey("traces.id"), nullable=False),
        sa.Column("span_id", sa.String, nullable=False, unique=True),
        sa.Column("parent_span_id", sa.String, nullable=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("kind", sa.String, nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("attributes", sa.JSON, nullable=False),
        sa.Column("events", sa.JSON, nullable=False),
        sa.Column(
            "status",
            sa.String,
            # TODO(mikeldking): this doesn't seem to work...
            sa.CheckConstraint("status IN ('OK', 'ERROR', 'UNSET')", "valid_status"),
            nullable=False,
            default="UNSET",
            server_default="UNSET",
        ),
        sa.Column("status_message", sa.String, nullable=False),
        sa.Column("latency_ms", sa.REAL, nullable=False),
        sa.Column("cumulative_error_count", sa.Integer, nullable=False),
        sa.Column("cumulative_llm_token_count_prompt", sa.Integer, nullable=False),
        sa.Column("cumulative_llm_token_count_completion", sa.Integer, nullable=False),
    )
    op.bulk_insert(
        projects_table,
        [
            {"name": "default", "description": "Default project"},
        ],
    )


def downgrade() -> None:
    op.drop_table("projects")
    op.drop_table("traces")
    op.drop_table("spans")