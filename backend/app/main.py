from fastapi import FastAPI, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# CORS Middleware
from fastapi.middleware.cors import CORSMiddleware

# DB
from app.db.database import get_db

# CORE
from app.core.config import settings

# Exceptions
from app.core.exceptions import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unexpected_exception_handler,
)

# Routers
from app.routers import auth, category, transaction, budget, dashboard, report, export

# Logging
from app.core.logging_config import setup_logging
import logging
import time

setup_logging()

# Create FastAPI application
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


# Request logging middleware
logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request, call_next):

    start_time = time.perf_counter()

    method = request.method
    path = request.url.path

    try:
        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        logger.info(
            "%s %s | Status: %s | Duration: %.4f seconds",
            method,
            path,
            response.status_code,
            process_time,
        )

        return response

    except Exception:
        process_time = time.perf_counter() - start_time

        logger.exception(
            "%s %s | Request failed | Duration: %.4f seconds",
            method,
            path,
            process_time,
        )

        raise


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)

# Register routers
API_V1_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(category.router, prefix=API_V1_PREFIX)
app.include_router(transaction.router, prefix=API_V1_PREFIX)
app.include_router(budget.router, prefix=API_V1_PREFIX)
app.include_router(dashboard.router, prefix=API_V1_PREFIX)
app.include_router(report.router, prefix=API_V1_PREFIX)
app.include_router(export.router, prefix=API_V1_PREFIX)


# Default Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Expense Tracker API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/db-check")
async def database_check(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        value = result.scalar_one()

        return {"database": "connected", "result": value}

    except Exception as e:
        return {"database": "connection failed", "error": str(e)}
