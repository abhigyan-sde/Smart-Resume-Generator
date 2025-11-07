from dotenv import load_dotenv

# Load environment variables from .env at project root
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import resume, job


def create_app() -> FastAPI:
    app = FastAPI(
        title="Resume Optimizer API",
        description="LLM-powered resume tailoring service",
        version="0.1.0",
    )

    # --- CORS Middleware ---
    origins = [
        "http://localhost:4200",  # Angular dev server
        "http://127.0.0.1:4200",
        # Add more origins if needed
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(resume.router, prefix="/resume", tags=["Resume"])
    app.include_router(job.router, prefix="/job", tags=["Job"])

    return app


# Instantiate app
app = create_app()
