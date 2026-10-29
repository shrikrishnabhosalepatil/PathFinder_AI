"""
Inference and Prediction Pipeline for PathFinder AI.
Loads the trained scikit-learn model, validates input features, computes
probabilities, categorizes readiness, and orchestrates domain career guidance.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import joblib
import pandas as pd
import numpy as np

import config
from train_model import train_and_evaluate_model
from career_guidance import (
    calculate_readiness_score,
    generate_pillar_assessments,
    get_career_guidance_for_student
)

# Global model cache to avoid reloading on every single request
_MODEL_PIPELINE = None
_MODEL_METRICS = None

def get_model():
    """Returns the cached model pipeline, loading or training if necessary."""
    global _MODEL_PIPELINE, _MODEL_METRICS

    if _MODEL_PIPELINE is not None:
        return _MODEL_PIPELINE

    if not config.MODEL_PATH.exists():
        print("[!] Model file not found. Triggering automated model training...")
        _MODEL_PIPELINE, _MODEL_METRICS = train_and_evaluate_model()
        return _MODEL_PIPELINE

    try:
        _MODEL_PIPELINE = joblib.load(config.MODEL_PATH)
    except Exception as e:
        print(f"[!] Error loading model ({e}). Retraining...")
        _MODEL_PIPELINE, _MODEL_METRICS = train_and_evaluate_model()

    return _MODEL_PIPELINE

def get_metrics() -> Dict[str, Any]:
    """Loads model evaluation metrics metadata from JSON."""
    global _MODEL_METRICS
    if _MODEL_METRICS is not None:
        return _MODEL_METRICS

    if config.METRICS_PATH.exists():
        try:
            with open(config.METRICS_PATH, "r", encoding="utf-8") as f:
                _MODEL_METRICS = json.load(f)
                return _MODEL_METRICS
        except Exception:
            pass

    # If missing, train to regenerate
    _, _MODEL_METRICS = train_and_evaluate_model()
    return _MODEL_METRICS

def validate_student_input(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Strict server-side validation of student submission.
    Returns (is_valid, error_message, sanitized_dict).
    """
    required_fields = [
        "student_name", "cgpa", "aptitude_score", "technical_score",
        "communication_score", "internships", "projects", "backlogs"
    ]

    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            return False, f"Missing required field: {field.replace('_', ' ').capitalize()}", {}

    try:
        student_name = str(data["student_name"]).strip()
        if len(student_name) < 2 or len(student_name) > 100:
            return False, "Student name must be between 2 and 100 characters.", {}

        cgpa = float(data["cgpa"])
        if not (0.0 <= cgpa <= 10.0):
            return False, "CGPA must be between 0.0 and 10.0.", {}

        aptitude_score = float(data["aptitude_score"])
        if not (0.0 <= aptitude_score <= 100.0):
            return False, "Aptitude score must be between 0 and 100.", {}

        technical_score = float(data["technical_score"])
        if not (1.0 <= technical_score <= 10.0):
            return False, "Technical skill rating must be between 1 and 10.", {}

        communication_score = float(data["communication_score"])
        if not (1.0 <= communication_score <= 10.0):
            return False, "Communication skill rating must be between 1 and 10.", {}

        internships = int(data["internships"])
        if not (0 <= internships <= 20):
            return False, "Number of internships must be a non-negative integer (0-20).", {}

        projects = int(data["projects"])
        if not (0 <= projects <= 50):
            return False, "Number of projects must be a non-negative integer (0-50).", {}

        backlogs = int(data["backlogs"])
        if not (0 <= backlogs <= 30):
            return False, "Active backlogs must be a non-negative integer (0-30).", {}

        programming_skills = str(data.get("programming_skills", "")).strip()
        preferred_domain = str(data.get("preferred_domain", "Software Developer")).strip()
        if preferred_domain not in config.CAREER_DOMAINS:
            preferred_domain = "Software Developer"

        sanitized = {
            "student_name": student_name,
            "cgpa": round(cgpa, 2),
            "aptitude_score": round(aptitude_score, 1),
            "technical_score": round(technical_score, 1),
            "communication_score": round(communication_score, 1),
            "internships": internships,
            "projects": projects,
            "backlogs": backlogs,
            "programming_skills": programming_skills,
            "preferred_domain": preferred_domain
        }
        return True, None, sanitized

    except (ValueError, TypeError) as e:
        return False, f"Invalid numerical format: {str(e)}", {}

def predict_student_placement(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the full prediction workflow:
    1. Preprocesses numerical features into model DataFrame.
    2. Runs inference using Random Forest pipeline to obtain placement probability.
    3. Categorizes placement likelihood.
    4. Computes independent 0-100 Placement Readiness Score.
    5. Performs pillar-by-pillar qualitative assessment.
    6. Conducts career domain skill gap analysis.
    """
    model = get_model()

    # Create feature DataFrame with exact column ordering
    input_df = pd.DataFrame([{
        "cgpa": float(data["cgpa"]),
        "aptitude_score": float(data["aptitude_score"]),
        "technical_score": float(data["technical_score"]),
        "communication_score": float(data["communication_score"]),
        "internships": int(data["internships"]),
        "projects": int(data["projects"]),
        "backlogs": int(data["backlogs"])
    }])[config.FEATURE_COLUMNS]

    # Predict probability for Class 1 (Placed)
    probabilities = model.predict_proba(input_df)[0]
    prob_placed = float(probabilities[1]) * 100.0  # percentage

    # If student has backlogs >= 3, industry realism override
    if int(data["backlogs"]) >= 3:
        prob_placed = min(prob_placed, 25.0)

    prob_placed = round(prob_placed, 1)

    # Placement Category
    if prob_placed >= 75.0:
        category = "High Placement Likelihood"
        cat_badge = "badge-success"
        cat_color = "#10B981"
        cat_desc = "Strong profile alignment with major recruitment benchmarks. High probability of clearing recruitment rounds."
    elif prob_placed >= 45.0:
        category = "Moderate Placement Likelihood"
        cat_badge = "badge-primary"
        cat_color = "#3B82F6"
        cat_desc = "Promising profile with key upskilling opportunities. Consistent practice in core areas will solidify offers."
    else:
        category = "Needs Improvement / At Risk"
        cat_badge = "badge-danger"
        cat_color = "#EF4444"
        cat_desc = "Active backlogs or foundational gaps require immediate corrective focus before campus placement drives."

    # Readiness Score (0-100 composite index)
    readiness_score = calculate_readiness_score(
        cgpa=data["cgpa"],
        aptitude=data["aptitude_score"],
        tech=data["technical_score"],
        comm=data["communication_score"],
        internships=data["internships"],
        projects=data["projects"],
        backlogs=data["backlogs"]
    )

    # Qualitative Assessments
    assessments = generate_pillar_assessments(data)

    # Career Domain Guidance
    career_guidance = get_career_guidance_for_student(
        domain_name=data["preferred_domain"],
        programming_skills_str=data.get("programming_skills", "")
    )

    # Radar/Spider chart normalized data for frontend visualization
    radar_data = {
        "labels": ["Academics (CGPA)", "Aptitude", "Technical Skills", "Communication", "Projects & Internships"],
        "values": [
            round(min(data["cgpa"] * 10.0, 100.0), 1),
            round(min(data["aptitude_score"], 100.0), 1),
            round(min(data["technical_score"] * 10.0, 100.0), 1),
            round(min(data["communication_score"] * 10.0, 100.0), 1),
            round(min((data["internships"] * 25.0) + (data["projects"] * 12.5), 100.0), 1)
        ]
    }

    return {
        "student_name": data["student_name"],
        "cgpa": data["cgpa"],
        "aptitude_score": data["aptitude_score"],
        "technical_score": data["technical_score"],
        "communication_score": data["communication_score"],
        "internships": data["internships"],
        "projects": data["projects"],
        "backlogs": data["backlogs"],
        "programming_skills": data.get("programming_skills", ""),
        "preferred_domain": data["preferred_domain"],
        "predicted_category": category,
        "category_badge": cat_badge,
        "category_color": cat_color,
        "category_description": cat_desc,
        "placement_probability": prob_placed,
        "readiness_score": readiness_score,
        "assessments": assessments,
        "career_guidance": career_guidance,
        "radar_data": radar_data,
        "disclaimer": "Note: Model prediction represents estimated statistical likelihood based on historical campus recruitment patterns, not a guaranteed employment offer."
    }
