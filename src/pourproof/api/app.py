"""FastAPI application factory for PourProof backend."""

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pourproof.vision.runtime import get_opencv_runtime_info
from pourproof.api.routes import router

logger = logging.getLogger("pourproof.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler verifying runtime environment on startup."""
    runtime = get_opencv_runtime_info()
    if runtime["is_opencv5"]:
        logger.info("PourProof API started with verified OpenCV %s (%s)", runtime["version"], runtime["module_path"])
    else:
        logger.warning(
            "PourProof API started but OpenCV 5 requirement NOT met! Detected version: %s at %s",
            runtime["version"],
            runtime["module_path"],
        )
    yield


app = FastAPI(
    title="PourProof Inspection API",
    description="Evidence-driven computer vision inspection backend for rebar spacing verification using OpenCV 5.",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS middleware for local frontend development (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pourproof.api.app:app", host="127.0.0.1", port=8000, reload=True, app_dir="src")
