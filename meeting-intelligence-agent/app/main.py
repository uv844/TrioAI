import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

from app.database.session import Base, engine
from app.models.meeting_db import MeetingModel  # ensures model is registered with Base
from app.routes.meeting_routes import router
from app.routes.rag_routes import router as rag_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that handles startup and shutdown events.
    Attempts to create database tables on startup. If SQL Server is not reachable,
    logs a warning without crashing so configuration can be adjusted.
    """
    try:
        logger.info("Connecting to SQL Server and creating tables if not present...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(
            f"Could not connect to SQL Server during startup. "
            f"Please ensure SQL Server is running and .env is configured correctly. Error: {e}"
        )
    yield


app = FastAPI(
    title="Meeting Intelligence Agent",
    lifespan=lifespan
)

app.include_router(router)
app.include_router(rag_router)


@app.get("/")
def home():
    return {
        "message": "Meeting Intelligence Agent Running",
        "database": "Microsoft SQL Server (SSMS)"
    }

@app.get("/chat")
def chatbot():
    html_path = Path(__file__).resolve().parents[1] / "chatbot.html"
    return FileResponse(html_path)
