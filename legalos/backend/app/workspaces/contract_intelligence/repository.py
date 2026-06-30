import uuid
from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.shared.db.models import Document
from app.workspaces.contract_intelligence.models import Contract, Clause, NegotiationSuggestion


async def get_contract_by_id(session: AsyncSession, contract_id: uuid.UUID) -> Optional[Contract]:
    """Retrieves a contract with all clauses and nested negotiation suggestions loaded."""
    stmt = (
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.clauses)
            .selectinload(Clause.suggestions)
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_contracts_with_counts(session: AsyncSession) -> List[dict]:
    """
    Lists all contracts and calculates risk counts:
    - risk_clause_count: clauses where risk_type != 'none'
    - high_risk_count: clauses where risk_score >= 70
    """
    # Simple strategy: Select contracts, then subquery count clauses or do aggregation.
    # To keep it clean and robust, we select contracts and count using aggregates
    # with a group_by.
    stmt = (
        select(
            Contract,
            func.count(Clause.id).filter(Clause.risk_type != 'none').label("risk_clause_count"),
            func.count(Clause.id).filter(Clause.risk_score >= 70).label("high_risk_count")
        )
        .outerjoin(Clause, Contract.id == Clause.contract_id)
        .group_by(Contract.id)
        .order_by(Contract.created_at.desc())
    )
    
    result = await session.execute(stmt)
    rows = result.all()
    
    contracts_list = []
    for contract, risk_count, high_risk in rows:
        contracts_list.append({
            "id": contract.id,
            "document_id": contract.document_id,
            "title": contract.title,
            "counterparty_name": contract.counterparty_name,
            "status": contract.status,
            "created_at": contract.created_at,
            "risk_clause_count": risk_count or 0,
            "high_risk_count": high_risk or 0
        })
        
    return contracts_list


async def create_document(
    session: AsyncSession,
    workspace: str,
    original_filename: str,
    storage_path: str,
    uploaded_by: Optional[uuid.UUID] = None
) -> Document:
    """Inserts an uploaded document record in the core schema."""
    doc = Document(
        workspace=workspace,
        original_filename=original_filename,
        storage_path=storage_path,
        uploaded_by=uploaded_by
    )
    session.add(doc)
    await session.flush()
    return doc


async def create_contract(
    session: AsyncSession,
    document_id: uuid.UUID,
    title: str = "Analyzing...",
    counterparty_name: str = "Analyzing..."
) -> Contract:
    """Inserts a contract record."""
    contract = Contract(
        document_id=document_id,
        title=title,
        counterparty_name=counterparty_name,
        status="processing"
    )
    session.add(contract)
    await session.flush()
    return contract


async def update_contract_metadata(
    session: AsyncSession,
    contract_id: uuid.UUID,
    title: str,
    counterparty_name: str,
    status: str = "analyzed"
) -> None:
    """Updates contract metadata after AI extraction."""
    contract = await session.get(Contract, contract_id)
    if contract:
        contract.title = title
        contract.counterparty_name = counterparty_name
        contract.status = status
        await session.flush()


async def add_clause(
    session: AsyncSession,
    contract_id: uuid.UUID,
    clause_index: int,
    raw_text: str,
    summary: Optional[str] = None,
    risk_type: Optional[str] = "none",
    risk_score: Optional[int] = 0,
    qdrant_point_id: Optional[uuid.UUID] = None
) -> Clause:
    """Saves an analyzed clause to the database."""
    clause = Clause(
        contract_id=contract_id,
        clause_index=clause_index,
        raw_text=raw_text,
        summary=summary,
        risk_type=risk_type,
        risk_score=risk_score,
        qdrant_point_id=qdrant_point_id
    )
    session.add(clause)
    await session.flush()
    return clause


async def get_clause_by_id(session: AsyncSession, clause_id: uuid.UUID) -> Optional[Clause]:
    """Fetch a single clause by ID."""
    return await session.get(Clause, clause_id)


async def add_suggestion(
    session: AsyncSession,
    clause_id: uuid.UUID,
    suggestion_text: str
) -> NegotiationSuggestion:
    """Saves a negotiation suggestion to a clause."""
    suggestion = NegotiationSuggestion(
        clause_id=clause_id,
        suggestion_text=suggestion_text
    )
    session.add(suggestion)
    await session.flush()
    return suggestion
