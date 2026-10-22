"""Create or reconcile the baseline application schema.

Revision ID: 0001_baseline_schema
Revises:
Create Date: 2026-10-21
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_baseline_schema"
down_revision = None
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    tables = _table_names()

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(), nullable=False, unique=True),
            sa.Column("nickname", sa.String(), nullable=True),
            sa.Column("hashed_password", sa.String(), nullable=False),
            sa.Column("role", sa.String(), nullable=False, server_default="user"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
    if "detections" not in tables:
        op.create_table(
            "detections",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("image_path", sa.String(), nullable=False),
            sa.Column("heatmap_path", sa.String(), nullable=True),
            sa.Column("is_fake", sa.Boolean(), nullable=False),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("fake_probability", sa.Float(), nullable=False),
            sa.Column("analysis_report", sa.JSON(), nullable=True),
            sa.Column("llm_explanation", sa.JSON(), nullable=True),
            sa.Column("cert_id", sa.String(), nullable=False, unique=True),
            sa.Column("cert_signature", sa.String(), nullable=True),
            sa.Column("sha256", sa.String(), nullable=True),
            sa.Column("phash", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_detections_user_id", "detections", ["user_id"])
        op.create_index("ix_detections_created_at", "detections", ["created_at"])
    else:
        columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("detections")}
        if "llm_explanation" not in columns:
            op.add_column("detections", sa.Column("llm_explanation", sa.JSON(), nullable=True))

    tables = _table_names()
    if "trace_records" not in tables:
        op.create_table(
            "trace_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("detection_id", sa.Integer(), sa.ForeignKey("detections.id"), nullable=False),
            sa.Column("action", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("meta_info", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_trace_records_detection_id", "trace_records", ["detection_id"])

    if "audit_logs" not in tables:
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("action", sa.String(), nullable=False),
            sa.Column("resource", sa.String(), nullable=True),
            sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("ip_address", sa.String(), nullable=True),
            sa.Column("user_agent", sa.String(), nullable=True),
            sa.Column("detail", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    if "llm_configs" not in tables:
        op.create_table(
            "llm_configs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("provider", sa.String(), nullable=False, server_default="openai"),
            sa.Column("api_base_url", sa.String(), nullable=False, server_default="https://api.openai.com/v1"),
            sa.Column("api_key", sa.String(), nullable=False, server_default=""),
            sa.Column("model", sa.String(), nullable=False, server_default="gpt-4o-mini"),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("max_tokens", sa.Integer(), nullable=False, server_default="512"),
            sa.Column("temperature", sa.Float(), nullable=False, server_default="0.3"),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    raise RuntimeError(
        "The baseline migration adopts existing application tables and cannot "
        "distinguish them from tables it created. Restore a database backup "
        "instead of downgrading this revision."
    )
