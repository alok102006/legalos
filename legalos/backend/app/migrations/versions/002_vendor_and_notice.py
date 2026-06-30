"""vendor and notice schemas

Revision ID: 002_vendor_and_notice
Revises: 001_baseline
Create Date: 2026-06-30 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_vendor_and_notice'
down_revision: Union[str, None] = '001_baseline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create vendor_checks table
    op.create_table(
        'vendor_checks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('gstin', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('registration_date', sa.Date(), nullable=True),
        sa.Column('trust_score', sa.Integer(), nullable=True),
        sa.Column('fraud_flagged', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('raw_mock_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('checked_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['checked_by'], ['core.users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('trust_score >= 0 AND trust_score <= 100', name='check_trust_score_range'),
        schema='vendor_intelligence'
    )

    # Create notices table
    op.create_table(
        'notices',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('raw_text', sa.String(), nullable=False),
        sa.Column('notice_type', sa.String(), nullable=True),
        sa.Column('urgency', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['core.documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("notice_type IN ('demand', 'show_cause', 'summons', 'other')", name='check_notice_type_values'),
        sa.CheckConstraint("urgency IN ('low', 'medium', 'high', 'critical')", name='check_urgency_values'),
        schema='legal_notice_center'
    )

    # Create draft_replies table
    op.create_table(
        'draft_replies',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('notice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reply_text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['notice_id'], ['legal_notice_center.notices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='legal_notice_center'
    )


def downgrade() -> None:
    op.drop_table('draft_replies', schema='legal_notice_center')
    op.drop_table('notices', schema='legal_notice_center')
    op.drop_table('vendor_checks', schema='vendor_intelligence')
