"""
Rhino AI - Backend FastAPI
MVP1: Pre-check de entregables con evaluación por rúbrica
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pythonjsonlogger import jsonlogger

from api.routes import router
from storage.database import init_db
from utils.config import settings

# Configurar logging JSON
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    logger.info("Starting Rhino AI backend")
    await init_db()
    
    # Crear directorios necesarios
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("db", exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Rhino AI backend")


app = FastAPI(
    title="Rhino AI API",
    description="Pre-check de entregables con evaluación por rúbrica gubernamental",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "Rhino AI",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
