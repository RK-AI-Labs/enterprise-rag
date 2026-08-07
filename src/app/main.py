"""FastAPI application factory."""

from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.middleware import correlation_id_middleware
from app.api.router import api_router
from app.config.settings import get_settings
from app.logging.setup import configure_logging


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.middleware("http")(correlation_id_middleware)
    register_exception_handlers(app)
    app.include_router(api_router)

    return app


app = create_app()
