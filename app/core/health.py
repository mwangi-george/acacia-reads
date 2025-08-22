import time
from loguru import logger
from fastapi import status, Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.settings.config import PROJECT_VERSION

START_TIME = time.time()

def register_health_check(app: FastAPI) -> None:
    """
    Creates a Health check endpoint that validates system components.

    Checks performed:
        - Database connectivity
        - Application uptime
        - Build version
        - Current UTC timestamp

    Returns:
        dict: Health report containing status and check results.
    """

    @app.get("/health", status_code=status.HTTP_200_OK)
    async def health(db: AsyncSession = Depends(get_db)) -> dict:
        health_status = {"status": "ok", "checks": {}}

        # Database check
        try:
            await db.execute(text("SELECT 1"))
            health_status["checks"]["database"] = "ok"
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            health_status["checks"]["database"] = "error"
            health_status["status"] = "error"

        # Uptime, timestamp, version
        health_status["uptime_seconds"] = int(time.time() - START_TIME)
        health_status["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        health_status["version"] = PROJECT_VERSION
        return health_status
