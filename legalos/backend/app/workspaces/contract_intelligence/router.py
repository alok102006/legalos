import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks

from app.dependencies import get_db_session, get_current_user
from app.shared.db.session import AsyncSession
from app.shared.auth.auth_service import UserStub
from app.shared.exceptions import BadRequestException
from app.workspaces.contract_intelligence import service, schemas

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md"}


@router.post("/upload", response_model=schemas.ContractSummarySchema)
async def upload_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserStub = Depends(get_current_user)
):
    """
    Upload and parse contract file.
    Performs file size validation (max 10MB) and file format checking.
    Launches analysis worker asynchronously.
    """
    # 1. Read file bytes to validate size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise BadRequestException(
            f"File size too large ({len(file_bytes)} bytes). Maximum allowed size is 10MB."
        )
        
    # 2. Extract and validate file extension
    filename = file.filename or "contract.txt"
    if "." not in filename:
        raise BadRequestException("Missing file extension. Supported: PDF, DOCX, TXT.")
        
    ext = filename.lower().split(".")[-1]
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequestException(
            f"Unsupported file format '{ext}'. Only PDF, DOCX, and TXT/MD are allowed."
        )
        
    # 3. Create document stub and contract record in DB
    contract = await service.create_and_start_analysis(
        session=db,
        file_bytes=file_bytes,
        filename=filename,
        user_id=current_user.id
    )
    
    # 4. Trigger asynchronous analysis task
    background_tasks.add_task(
        service.run_async_contract_analysis,
        contract_id=contract.id,
        file_bytes=file_bytes,
        filename=filename,
        document_id=contract.document_id
    )
    
    # Return contract summary object with processing status
    return {
        "id": contract.id,
        "document_id": contract.document_id,
        "title": contract.title,
        "counterparty_name": contract.counterparty_name,
        "status": contract.status,
        "created_at": contract.created_at,
        "risk_clause_count": 0,
        "high_risk_count": 0
    }


@router.get("/", response_model=List[schemas.ContractSummarySchema])
async def get_contracts(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserStub = Depends(get_current_user)
):
    """Lists all contracts under processing, analyzed, or failed status."""
    return await service.list_contracts(db)


@router.get("/{id}", response_model=schemas.ContractDetailSchema)
async def get_contract(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserStub = Depends(get_current_user)
):
    """Retrieves full contract breakdown with all clause scores and annotations."""
    return await service.get_contract_details(db, id)


@router.post("/{id}/clauses/{clause_id}/suggest", response_model=schemas.NegotiationSuggestionSchema)
async def generate_clause_suggestion(
    id: uuid.UUID,
    clause_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserStub = Depends(get_current_user)
):
    """Generates a negotiation recommendation using context-enhanced RAG generation."""
    return await service.generate_clause_suggestion(db, id, clause_id)


@router.delete("/{id}")
async def delete_contract(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserStub = Depends(get_current_user)
):
    """Deletes a contract and its associated database and vector store records."""
    await service.delete_contract_and_document(db, id)
    return {"status": "success", "message": "Contract deleted successfully"}

