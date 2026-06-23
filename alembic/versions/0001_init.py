"""initial schema

Revision ID: 0001_init
Revises:
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("service", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("logs", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doc_id", sa.String(length=100), nullable=False, unique=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("doc_type", sa.String(length=50), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "investigation_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id"), nullable=False, unique=True),
        sa.Column("root_cause", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("remediation_steps", sa.JSON(), nullable=False),
        sa.Column("supporting_evidence", sa.JSON(), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=False),
        sa.Column("escalation_required", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "agent_traces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("agent_traces")
    op.drop_table("investigation_reports")
    op.drop_table("knowledge_documents")
    op.drop_table("incidents")
