import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.routes import analysis, auth, chat, dashboard, experiments, figures, papers
from app.config import get_settings
from app.core.errors import APIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("researchpilot")

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="ResearchPilot API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
    )


app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(analysis.router)
app.include_router(figures.router)
app.include_router(experiments.router)
app.include_router(dashboard.router)

os.makedirs(f"{settings.storage_dir}/figures", exist_ok=True)
os.makedirs(f"{settings.storage_dir}/papers", exist_ok=True)
app.mount("/static/figures", StaticFiles(directory=f"{settings.storage_dir}/figures"), name="figures")


@app.get("/health")
def health():
    return {"status": "ok"}
