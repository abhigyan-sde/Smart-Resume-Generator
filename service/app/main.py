from dotenv import load_dotenv

# Load environment variables from .env at project root
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import resume_evaluation_route, resume_generation_route


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
    app.include_router(resume_evaluation_route.router, prefix="/resume", tags=["Resume"])
    app.include_router(resume_generation_route.router, prefix="/resume", tags=["Resume"])
    return app


# Instantiate app
app = create_app()
