"""
ExecutiveAI Backend — FastAPI Application Entry Point
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import create_tables
from middleware.logging import RequestLoggingMiddleware
from middleware.tenant import TenantMiddleware
from api.routes import auth, sales, inventory, analytics, ai, forecasting, reports, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    await create_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "ExecutiveAI — Production-grade analytics platform for C-suite executives. "
        "Provides real-time sales analytics, inventory management, AI-powered insights, "
        "and revenue forecasting."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TenantMiddleware)

API = settings.API_V1_STR

app.include_router(auth.router,        prefix=f"{API}/auth",        tags=["Authentication"])
app.include_router(sales.router,       prefix=f"{API}/sales",       tags=["Sales Analytics"])
app.include_router(inventory.router,   prefix=f"{API}/inventory",   tags=["Inventory"])
app.include_router(analytics.router,   prefix=f"{API}/analytics",   tags=["Analytics & KPIs"])
app.include_router(ai.router,          prefix=f"{API}/ai",          tags=["AI Agent"])
app.include_router(forecasting.router, prefix=f"{API}/forecasting", tags=["Forecasting"])
app.include_router(reports.router,     prefix=f"{API}/reports",     tags=["Reports"])
app.include_router(alerts.router,      prefix=f"{API}/alerts",      tags=["Alerts"])


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
