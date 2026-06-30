import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.embeddings.embedder import get_embedder
from app.core.vectorstore.collections import init_collections
from app.shared.exceptions import LegalOSException
from app.workspaces.contract_intelligence.router import router as contract_router
from app.workspaces.vendor_intelligence.router import router as vendor_router
from app.workspaces.legal_notice_center.router import router as notice_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and teardown routines:
    1. Warms up local embedding singleton (SentenceTransformer)
    2. Warm up / create Qdrant database collections
    """
    print("[LIFESPAN] Executing startup sequence...")
    
    # 1. Warm up embedder (singleton loading)
    try:
        get_embedder()
    except Exception as e:
        print(f"[LIFESPAN] Critical Error warming up embedder: {e}")
        # We don't crash startup for dev environment, but raise for prod
        if settings.env == "prod":
            raise e
            
    # 2. Warm up Qdrant database collections
    try:
        init_collections()
    except Exception as e:
        print(f"[LIFESPAN] Critical Error warming up Qdrant collections: {e}")
        if settings.env == "prod":
            raise e
            
    print("[LIFESPAN] Startup sequence successfully finished.")
    yield
    print("[LIFESPAN] Shutting down application...")


app = FastAPI(
    title="LegalOS Central Server",
    description="Production-grade AI/RAG Legal OS Core and Contract Intelligence platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure dynamic CORS origins
allowed_origins = []
if settings.frontend_url:
    # Handle multiple comma-separated URLs if present
    allowed_origins = [o.strip() for o in settings.frontend_url.split(",")]
    
print(f"[MAIN] CORS Allowed Origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for custom LegalOS exception class
@app.exception_handler(LegalOSException)
async def legalos_exception_handler(request: Request, exc: LegalOSException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": time.time(),
            "path": request.url.path
        }
    )


# Basic health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "provider": settings.llm_provider
    }


# Register workspace routers
app.include_router(
    contract_router,
    prefix="/api/v1/contracts",
    tags=["Contract Intelligence"]
)

app.include_router(
    vendor_router,
    prefix="/api/v1/vendors",
    tags=["Vendor Intelligence"]
)

app.include_router(
    notice_router,
    prefix="/api/v1/notices",
    tags=["Legal Notice Center"]
)
