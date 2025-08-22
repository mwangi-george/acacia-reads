import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from loguru import logger
from fastapi import FastAPI, status, Depends
from graphene import Schema
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_graphene3 import GraphQLApp, make_playground_handler

from app.db.database import get_db
from app.settings.config import (
    PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION, PROJECT_LICENSE
)


class APIBuilder:
    """
    A builder class for initializing and configuring the FastAPI application,
    including health checks, GraphQL endpoints, and application lifecycle logging.
    """

    START_TIME = time.time()

    def create_app_instance(self) -> FastAPI:
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
            lifespan=self.app_lifespan,
        )

        # Health check endpoint
        @app_instance.get("/health", status_code=status.HTTP_200_OK)
        async def health(db: AsyncSession = Depends(get_db)) -> dict:
            """
            Health check endpoint that validates system components.

            Checks performed:
            - Database connectivity
            - Application uptime
            - Build version
            - Current UTC timestamp

            Returns:
                dict: Health report containing status and check results.
            """
            health_status = {"status": "ok", "checks": {}}

            # Database check
            try:
                await db.execute(text("SELECT 1"))
                health_status["checks"]["database"] = "ok"
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                health_status["checks"]["database"] = "error"
                health_status["status"] = "error"

            # Add uptime, timestamp, version
            health_status["uptime_seconds"] = int(time.time() - self.START_TIME)
            health_status["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            health_status["version"] = PROJECT_VERSION

            return health_status

        return app_instance

    @staticmethod
    def mount_graphql_endpoint(app_instance: FastAPI, endpoint: str = "/graphql") -> FastAPI:
        """
        Mounts a GraphQL endpoint to the FastAPI instance.

        Args:
            app_instance (FastAPI): The FastAPI application instance.
            endpoint (str): Path for the GraphQL API.

        Returns:
            FastAPI: The updated app instance with GraphQL mounted.
        """
        gql_schema = Schema()  # TODO: Replace with actual schema
        app_instance.mount(
            path=endpoint,
            app=GraphQLApp(
                schema=gql_schema,
                on_get=make_playground_handler(),  # Enables GraphQL playground in browser
            )
        )
        return app_instance

    @staticmethod
    @asynccontextmanager
    async def app_lifespan(app_instance: FastAPI) -> AsyncGenerator[None, Any]:
        """
        Application lifespan context manager. Runs on startup and shutdown.

        Args:
            app_instance (FastAPI): The FastAPI application instance.
        """
        logger.info(f"--- Starting {PROJECT_NAME} ---")
        yield
        logger.info(f"--- Stopping {PROJECT_NAME} ---")


# Instantiate and build app
build_app = APIBuilder()
app = build_app.create_app_instance()
build_app.mount_graphql_endpoint(app)
