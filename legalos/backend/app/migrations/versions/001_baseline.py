"""baseline

Revision ID: 001_baseline
Revises: 
Create Date: 2026-06-30 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create core.users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), server_default='business_owner', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='core'
    )
    
    # 2. Create core.documents
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('workspace', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['uploaded_by'], ['core.users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='core'
    )

    # 3. Create contract_intelligence.contracts
    op.create_table(
        'contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('counterparty_name', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='processing', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['core.documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id'),
        schema='contract_intelligence'
    )

    # 4. Create contract_intelligence.clauses
    op.create_table(
        'clauses',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('contract_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clause_index', sa.Integer(), nullable=False),
        sa.Column('raw_text', sa.String(), nullable=False),
        sa.Column('summary', sa.String(), nullable=True),
        sa.Column('risk_type', sa.String(), server_default='none', nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('qdrant_point_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['contract_id'], ['contract_intelligence.contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='contract_intelligence'
    )

    # 5. Create contract_intelligence.negotiation_suggestions
    op.create_table(
        'negotiation_suggestions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('clause_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('suggestion_text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['clause_id'], ['contract_intelligence.clauses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='contract_intelligence'
    )


def downgrade() -> None:
    op.drop_table('negotiation_suggestions', schema='contract_intelligence')
    op.drop_table('clauses', schema='contract_intelligence')
    op.drop_table('contracts', schema='contract_intelligence')
    op.drop_table('documents', schema='core')
    op.drop_table('users', schema='core')
