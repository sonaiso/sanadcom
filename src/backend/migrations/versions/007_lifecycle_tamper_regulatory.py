"""Control lifecycle management, evidence tamper protection, and regulatory version register

Adds:
- Control lifecycle fields: lifecycle_status, owner, reviewer, approved_at, testability metadata
- Evidence tamper protection: file_hash (SHA-256), hash_algorithm, immutable audit chain flag
- Regulatory version register table

Revision ID: 007
Revises: 006_enhanced_controls
Create Date: 2026-02-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '007_lifecycle_tamper_regulatory'
down_revision = '006_enhanced_controls'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    # -----------------------------------------------------------------------
    # 1. Control lifecycle management fields
    # -----------------------------------------------------------------------
    existing_control_cols = [c['name'] for c in inspector.get_columns('controls')]

    lifecycle_columns = [
        ('lifecycle_status', sa.String(20), 'published'),
        ('owner', sa.String(200), None),
        ('reviewer', sa.String(200), None),
        ('approved_at', sa.DateTime, None),
        ('approved_by', sa.String(200), None),
        ('deprecated_at', sa.DateTime, None),
        ('test_what_en', sa.Text, None),
        ('test_what_ar', sa.Text, None),
        ('test_evidence_accepted', sa.JSON, None),
        ('test_frequency', sa.String(50), None),
        ('test_pass_criteria_en', sa.Text, None),
        ('test_pass_criteria_ar', sa.Text, None),
        ('regulatory_source', sa.String(100), None),
        ('regulatory_version', sa.String(50), None),
        ('regulatory_article', sa.String(100), None),
        ('regulatory_page', sa.Integer, None),
        ('regulatory_effective_date', sa.Date, None),
    ]

    for col_name, col_type, col_default in lifecycle_columns:
        if col_name not in existing_control_cols:
            if col_default is not None:
                op.add_column(
                    'controls',
                    sa.Column(col_name, col_type, nullable=True, server_default=col_default)
                )
            else:
                op.add_column('controls', sa.Column(col_name, col_type, nullable=True))

    # Index on lifecycle_status for filtering
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('controls')]
    if 'ix_controls_lifecycle_status' not in existing_indexes:
        op.create_index('ix_controls_lifecycle_status', 'controls', ['lifecycle_status'])
    if 'ix_controls_owner' not in existing_indexes:
        op.create_index('ix_controls_owner', 'controls', ['owner'])

    # -----------------------------------------------------------------------
    # 2. Evidence tamper protection fields
    # -----------------------------------------------------------------------
    existing_evidence_cols = [c['name'] for c in inspector.get_columns('evidence')]

    evidence_tamper_columns = [
        ('file_hash', sa.String(64)),        # SHA-256 hex digest
        ('hash_algorithm', sa.String(20)),   # e.g. "SHA-256"
        ('hash_verified_at', sa.DateTime),   # last integrity check timestamp
        ('is_immutable', sa.Boolean),        # flag for immutable/locked evidence
        ('workflow_status', sa.String(30)),  # requested|submitted|under_review|approved|rejected|expired
        ('submitted_at', sa.DateTime),
        ('reviewed_at', sa.DateTime),
        ('reviewed_by', sa.String(200)),
        ('sla_due_date', sa.DateTime),       # deadline per evidence SLA policy
        ('quality_score', sa.Integer),       # 0-100 completeness/quality score
        ('tenant_id', sa.Integer),           # for multi-tenant isolation
    ]

    for col_name, col_type in evidence_tamper_columns:
        if col_name not in existing_evidence_cols:
            op.add_column('evidence', sa.Column(col_name, col_type, nullable=True))

    # Index for workflow filtering
    existing_ev_indexes = [idx['name'] for idx in inspector.get_indexes('evidence')]
    if 'ix_evidence_workflow_status' not in existing_ev_indexes:
        op.create_index('ix_evidence_workflow_status', 'evidence', ['workflow_status'])
    if 'ix_evidence_tenant_id' not in existing_ev_indexes:
        op.create_index('ix_evidence_tenant_id', 'evidence', ['tenant_id'])

    # -----------------------------------------------------------------------
    # 3. Regulatory version register table
    # -----------------------------------------------------------------------
    if 'regulatory_versions' not in existing_tables:
        op.create_table(
            'regulatory_versions',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('framework', sa.String(20), nullable=False, index=True),
            sa.Column('version', sa.String(50), nullable=False),
            sa.Column('status', sa.String(20), nullable=False, server_default='active'),
            sa.Column('release_date', sa.Date, nullable=True),
            sa.Column('effective_date', sa.Date, nullable=True),
            sa.Column('superseded_date', sa.Date, nullable=True),
            sa.Column('official_url', sa.String(500), nullable=True),
            sa.Column('source_document', sa.String(200), nullable=True),
            sa.Column('change_summary_en', sa.Text, nullable=True),
            sa.Column('change_summary_ar', sa.Text, nullable=True),
            sa.Column('created_at', sa.DateTime, nullable=True),
            sa.Column('updated_at', sa.DateTime, nullable=True),
        )
        op.create_index(
            'ix_regulatory_versions_framework_status',
            'regulatory_versions',
            ['framework', 'status']
        )

    # -----------------------------------------------------------------------
    # 4. Per-tenant configuration table
    # -----------------------------------------------------------------------
    if 'tenant_configs' not in existing_tables:
        op.create_table(
            'tenant_configs',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('tenant_id', sa.Integer, nullable=False, index=True, unique=True),
            sa.Column('framework_scope', sa.JSON, nullable=True),   # ["ECC", "CCC"]
            sa.Column('language_preference', sa.String(5), server_default='ar'),
            sa.Column('evidence_policy_overrides', sa.JSON, nullable=True),
            sa.Column('report_template', sa.String(100), nullable=True),
            sa.Column('client_dictionary', sa.JSON, nullable=True),
            sa.Column('ai_index_id', sa.String(100), nullable=True),
            sa.Column('ai_adapter_id', sa.String(100), nullable=True),
            sa.Column('sla_config', sa.JSON, nullable=True),
            sa.Column('created_at', sa.DateTime, nullable=True),
            sa.Column('updated_at', sa.DateTime, nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # Drop tenant_configs
    existing_tables = inspector.get_table_names()
    if 'tenant_configs' in existing_tables:
        op.drop_table('tenant_configs')

    # Drop regulatory_versions
    if 'regulatory_versions' in existing_tables:
        op.drop_index('ix_regulatory_versions_framework_status', 'regulatory_versions')
        op.drop_table('regulatory_versions')

    # Drop evidence columns
    existing_evidence_cols = [c['name'] for c in inspector.get_columns('evidence')]
    for col_name in [
        'file_hash', 'hash_algorithm', 'hash_verified_at', 'is_immutable',
        'workflow_status', 'submitted_at', 'reviewed_at', 'reviewed_by',
        'sla_due_date', 'quality_score', 'tenant_id',
    ]:
        if col_name in existing_evidence_cols:
            op.drop_column('evidence', col_name)

    # Drop control lifecycle columns
    existing_control_cols = [c['name'] for c in inspector.get_columns('controls')]
    for col_name in [
        'lifecycle_status', 'owner', 'reviewer', 'approved_at', 'approved_by',
        'deprecated_at', 'test_what_en', 'test_what_ar', 'test_evidence_accepted',
        'test_frequency', 'test_pass_criteria_en', 'test_pass_criteria_ar',
        'regulatory_source', 'regulatory_version', 'regulatory_article',
        'regulatory_page', 'regulatory_effective_date',
    ]:
        if col_name in existing_control_cols:
            op.drop_column('controls', col_name)
