from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

# Import all models here so that Alembic's target_metadata can discover them
from app.shared.db.models import User, Document
from app.workspaces.contract_intelligence.models import Contract, Clause, NegotiationSuggestion
