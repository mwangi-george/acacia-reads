from fastapi import FastAPI

from app.core.graphql import mount_graphql
from app.core.health import register_health_check
from app.core.lifespan import app_lifespan
from app.settings.config import (
    PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION, PROJECT_LICENSE
)



def create_app_instance() -> FastAPI:
    """
    Creates and configures the FastAPI application instance.

    Returns:
        FastAPI: The configured FastAPI app instance with health endpoint.
    """
    app_instance = FastAPI(
        title=PROJECT_NAME,
        description=PROJECT_DESCRIPTION,
        version=PROJECT_VERSION,
        license=PROJECT_LICENSE,
        lifespan=app_lifespan,
    )

    # register health check endpoint
    register_health_check(app_instance)

    # mount GraphQl app
    mount_graphql(app_instance)

    return app_instance