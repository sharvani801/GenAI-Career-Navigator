
from typing import List, Optional
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.core.career_engine import create_career_plan
from backend.ai.genai import generate_career_response


# ==========================================
# LOGGING CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("career_navigator")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="GenAI Career Navigator API",
    description=(
        "AI-powered skill gap analysis and "
        "personalized career roadmap system."
    ),
    version="1.0.0",
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# REQUEST MODELS
# ==========================================

class AnalyzeRequest(BaseModel):
    target_job: str = Field(..., min_length=1)
    current_skills: List[str] = Field(default_factory=list)
    study_time: int = Field(default=10, ge=1, le=60)
    experience_level: str = "Beginner"
    learning_style: str = "Project-Based"


class AIRequest(BaseModel):
    target_job: str = Field(..., min_length=1)
    current_skills: List[str] = Field(default_factory=list)
    missing_skills: Optional[List[str]] = None
    study_time: int = Field(default=10, ge=1, le=60)
    experience_level: str = "Beginner"
    learning_style: str = "Project-Based"


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def root():
    logger.info("Health check endpoint accessed")

    return {
        "message": "GenAI Career Navigator API is running",
        "status": "healthy",
        "version": "1.0.0",
    }


# ==========================================
# GET ALL JOB ROLES
# ==========================================

@app.get("/roles")
def get_roles():
    logger.info("Job roles requested")
    roles_file = BASE_DIR / "data" / "career_roles.json"

    try:
        with open(roles_file, "r", encoding="utf-8") as file:
            roles = json.load(file)

        logger.info("Job roles loaded successfully")
        return {"roles": roles}

    except FileNotFoundError:
        logger.exception("career_roles.json was not found")
        raise HTTPException(
            status_code=500,
            detail="career_roles.json file was not found.",
        )

    except json.JSONDecodeError:
        logger.exception("career_roles.json contains invalid JSON")
        raise HTTPException(
            status_code=500,
            detail="career_roles.json contains invalid JSON.",
        )


# ==========================================
# ANALYZE CAREER
# ==========================================

@app.post("/analyze")
def analyze_career(request: AnalyzeRequest):
    logger.info(
        "Career analysis requested for job: %s",
        request.target_job,
    )

    try:
        result = create_career_plan(
            target_job=request.target_job,
            current_skills=request.current_skills,
            study_time=request.study_time,
            experience_level=request.experience_level,
            learning_style=request.learning_style,
        )

        if result is None:
            logger.warning(
                "Target job not found: %s",
                request.target_job,
            )
            raise HTTPException(
                status_code=404,
                detail=f"Target job '{request.target_job}' was not found.",
            )

        logger.info(
            "Career analysis completed successfully for job: %s",
            request.target_job,
        )

        return {
            "success": True,
            "data": result,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Career analysis failed for job: %s",
            request.target_job,
        )
        raise HTTPException(
            status_code=500,
            detail="Career analysis failed. Check the application logs.",
        )


# ==========================================
# GENERATE AI CAREER PLAN
# ==========================================

@app.post("/generate-ai")
def generate_ai_plan(request: AIRequest):
    logger.info(
        "AI career plan requested for job: %s",
        request.target_job,
    )

    try:
        missing_skills = request.missing_skills

        if missing_skills is None:
            career_result = create_career_plan(
                target_job=request.target_job,
                current_skills=request.current_skills,
                study_time=request.study_time,
                experience_level=request.experience_level,
                learning_style=request.learning_style,
            )

            if career_result is None:
                logger.warning(
                    "Target job not found for AI plan: %s",
                    request.target_job,
                )
                raise HTTPException(
                    status_code=404,
                    detail=f"Target job '{request.target_job}' was not found.",
                )

            missing_skills = career_result["missing_skills"]

        ai_response = generate_career_response(
            target_job=request.target_job,
            current_skills=request.current_skills,
            missing_skills=missing_skills,
            study_time=request.study_time,
            experience_level=request.experience_level,
            learning_style=request.learning_style,
        )

        logger.info(
            "AI career plan generated successfully for job: %s",
            request.target_job,
        )

        return {
            "success": True,
            "target_job": request.target_job,
            "response": ai_response,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "AI career plan generation failed for job: %s",
            request.target_job,
        )
        raise HTTPException(
            status_code=500,
            detail="AI generation failed. Check the application logs.",
        )


# ==========================================
# SERVER TEST
# ==========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
