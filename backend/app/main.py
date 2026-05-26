"""
GovernAI Studio — FastAPI Application Entry Point

Production-grade application factory with:
- Multi-provider LLM Gateway initialization
- GraphRAG knowledge graph (lazy-loaded)
- Privacy middleware (PII stripping, security headers)
- Rate limiting (in-process, pilot-scale)
- Structured logging with request tracing
- Graceful error handling with typed error responses
"""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import structlog

from app.config import get_settings
from app.db.database import init_db, close_db
from app.ai.gateway import LLMGateway, LLMBusyError
from app.corpus.graph_builder import GovernAIGraphBuilder
from app.privacy.middleware import PrivacyMiddleware, RateLimitMiddleware


# === Structured Logging Setup ===

def configure_logging(debug: bool = False):
    """Configure structlog for JSON output in production, pretty in development."""
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    if debug:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(20),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Initialize logging before anything else
settings = get_settings()
configure_logging(debug=settings.DEBUG)
logger = structlog.get_logger()


# === Lifespan (startup/shutdown) ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown."""
    settings = get_settings()
    logger.info(
        "starting_governai_studio",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        python_version=sys.version.split()[0],
    )

    # Initialize database connection
    await init_db()
    logger.info("database_connected", provider="Neon PostgreSQL")

    # Initialize LLM Gateway (multi-provider)
    app.state.llm_gateway = LLMGateway(settings)
    providers = app.state.llm_gateway.get_active_providers()
    logger.info("llm_gateway_ready", providers=providers, count=len(providers))

    # Initialize GraphRAG (lazy load — don't block startup)
    app.state.graph_rag = GovernAIGraphBuilder(settings.GRAPH_DATA_DIR)
    graph_stats = app.state.graph_rag.get_stats()
    logger.info("graphrag_initialized", **graph_stats)

    logger.info("startup_complete", status="ready")

    yield

    # Graceful shutdown
    await close_db()
    logger.info("governai_studio_shutdown", status="clean")


# === App Factory ===

def create_app() -> FastAPI:
    """
    Application factory pattern.
    Creates and configures the FastAPI application with all middleware,
    routes, error handlers, and observability endpoints.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "GovernAI Studio API — Scenario-based AI governance simulator "
            "for Indian civil servants. Built as public-interest infrastructure."
        ),
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # === Middleware Stack (order matters: first added = outermost) ===

    # 1. CORS (outermost — must handle preflight before other middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    # 2. Privacy middleware (PII stripping, security headers, audit logging)
    app.add_middleware(PrivacyMiddleware)

    # 3. Rate limiting (in-process, sufficient for 50-200 pilot users)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

    # === Route Registration ===

    from app.api.routes import auth, onboarding, scenarios, simulation, whisperer

    app.include_router(auth.router, prefix="/v1")
    app.include_router(onboarding.onboarding_router, prefix="/v1")
    app.include_router(scenarios.router, prefix="/v1")
    app.include_router(simulation.router, prefix="/v1")
    app.include_router(whisperer.router, prefix="/v1")

    # === Infrastructure Endpoints ===

    @app.get("/health", tags=["infrastructure"])
    async def health():
        """
        Health check endpoint.
        Pinged every 5 minutes by external cron to prevent Render cold starts.
        """
        return {
            "status": "ok",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/admin/diagnostics", tags=["infrastructure"])
    async def diagnostics(request: Request):
        """
        Diagnostics endpoint for observability.
        Returns LLM provider usage, graph stats, and system status.
        Protected: only accessible in development or with admin header.
        """
        if not settings.DEBUG:
            admin_key = request.headers.get("X-Admin-Key", "")
            if admin_key != settings.JWT_SECRET[:16]:
                return JSONResponse(status_code=403, content={"error": "FORBIDDEN"})

        gateway: LLMGateway = request.app.state.llm_gateway
        graph: GovernAIGraphBuilder = request.app.state.graph_rag

        return {
            "llm_providers": gateway.get_usage_stats(),
            "graph_status": graph.get_stats(),
            "active_providers": gateway.get_active_providers(),
        }

    # === Error Handlers ===

    @app.exception_handler(LLMBusyError)
    async def llm_busy_handler(request: Request, exc: LLMBusyError):
        """Handle LLM provider capacity exhaustion gracefully."""
        logger.warning("llm_capacity_exhausted", path=request.url.path)
        return JSONResponse(
            status_code=503,
            content={
                "error": "LLM_CAPACITY_EXHAUSTED",
                "message": str(exc),
                "retry_after": 60,
            },
            headers={"Retry-After": "60"},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Catch-all error handler. Never leaks internal details."""
        import traceback
        tb = traceback.format_exc()
        logger.error(
            "unhandled_error",
            error_type=type(exc).__name__,
            error=str(exc),
            path=request.url.path,
            method=request.method,
            traceback=tb if settings.DEBUG else "hidden",
        )
        detail = {
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again.",
        }
        if settings.DEBUG:
            detail["debug_error"] = str(exc)
            detail["debug_type"] = type(exc).__name__
        return JSONResponse(status_code=500, content=detail)

    return app


app = create_app()
