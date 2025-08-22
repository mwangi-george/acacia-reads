from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from fastapi import FastAPI
from loguru import logger

from app.settings.config import PROJECT_NAME

@asynccontextmanager
async def app_lifespan(app_instance: FastAPI) -> AsyncGenerator[None, Any]:
    logger.info(f"--- Starting {PROJECT_NAME} ---")

    yield

    logger.info(f"--- Stopping {PROJECT_NAME} ---")
