"""
PathFinder AI — Intelligent Student Placement Prediction and Career Readiness System.
Flask Application Web Server & API Layer.
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import config
from database import (
    init_db,
    insert_prediction,
    get_all_predictions,
    get_prediction_by_id,
    delete_prediction,
    get_dashboard_stats,
    get_analytics_data
)
from predictor import (
    validate_student_input,
    predict_student_placement,
    get_metrics,
    get_model
)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Ensure database and model are initialized on startup
with app.app_context():
    init_db()
    # Preload ML model
    try:
        get_model()
    except Exception as e:
        print(f"Warning: Could not preload model on startup: {e}")

# ==========================================
# Page Routes (Frontend Views)
# ==========================================

@app.route("/")
def index():
    """Dashboard homepage with KPI cards, charts, and recent records."""
    stats = get_dashboard_stats()
    recent_predictions = get_all_predictions(limit=6)
    metrics = get_metrics()
    return render_template(
        "index.html",
        active_page="dashboard",
        stats=stats,
        recent_predictions=recent_predictions,
        metrics=metrics
    )

@app.route("/predict", methods=["GET"])
def predict_page():
    """Student placement prediction and readiness evaluation form."""
    domains = config.CAREER_DOMAINS
    return render_template(
        "predict.html",
        active_page="predict",
        domains=domains
    )

@app.route("/history")
def history_page():
    """Prediction records history table with search and delete actions."""
    search_query = request.args.get("q", "").strip()
    predictions = get_all_predictions(search_query=search_query)
    return render_template(
        "history.html",
        active_page="history",
        predictions=predictions,
        search_query=search_query
    )

@app.route("/analytics")
def analytics_page():
    """In-depth interactive Chart.js analytics dashboard."""
    stats = get_dashboard_stats()
    return render_template(
        "analytics.html",
        active_page="analytics",
        stats=stats
    )

@app.route("/career-guidance")
def career_guidance_page():
    """Career guidance exploration with roadmaps and project ideas."""
    domains = config.CAREER_DOMAINS
    selected_domain = request.args.get("domain", "Software Developer")
    if selected_domain not in domains:
        selected_domain = "Software Developer"
    return render_template(
        "career_guidance.html",
        active_page="career_guidance",
        domains=domains,
        selected_domain=selected_domain
    )

@app.route("/model-info")
def model_info_page():
    """Transparency page detailing ML model architecture, evaluation metrics, and dataset."""
    metrics = get_metrics()
    return render_template(
        "model_info.html",
        active_page="model_info",
        metrics=metrics
    )

# ==========================================
# REST API Endpoints
# ==========================================

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Handles student placement prediction requests.
    Accepts JSON or Form data, performs validation, runs inference,
    stores in SQLite, and returns comprehensive readiness assessment.
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    # 1. Server-side Input Validation
    is_valid, error_msg, sanitized_data = validate_student_input(data)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": error_msg
        }), 400

    try:
        # 2. Run Machine Learning Inference and Pillar Assessment
        result = predict_student_placement(sanitized_data)

        # 3. Save Record to SQLite Database
        record_id = insert_prediction({
            "student_name": sanitized_data["student_name"],
            "cgpa": sanitized_data["cgpa"],
            "aptitude_score": sanitized_data["aptitude_score"],
            "technical_score": sanitized_data["technical_score"],
            "communication_score": sanitized_data["communication_score"],
            "internships": sanitized_data["internships"],
            "projects": sanitized_data["projects"],
            "backlogs": sanitized_data["backlogs"],
            "programming_skills": sanitized_data.get("programming_skills", ""),
            "preferred_domain": sanitized_data.get("preferred_domain", "Software Developer"),
            "predicted_category": result["predicted_category"],
            "placement_probability": result["placement_probability"],
            "readiness_score": result["readiness_score"]
        })

        result["record_id"] = record_id
        result["success"] = True

        return jsonify(result), 200

    except Exception as e:
        app.logger.error(f"Prediction execution failed: {e}")
        return jsonify({
            "success": False,
            "error": f"An error occurred during prediction processing: {str(e)}"
        }), 500

@app.route("/api/prediction/<int:record_id>", methods=["GET"])
def api_get_prediction(record_id):
    """Fetches full details of a specific prediction record."""
    record = get_prediction_by_id(record_id)
    if not record:
        return jsonify({"success": False, "error": "Record not found"}), 404

    # Reconstruct assessment for detailed view
    result = predict_student_placement(record)
    result["id"] = record["id"]
    result["created_at"] = record["created_at"]
    return jsonify({"success": True, "data": result})

@app.route("/api/prediction/<int:record_id>", methods=["DELETE"])
def api_delete_prediction(record_id):
    """Deletes a prediction record by ID."""
    success = delete_prediction(record_id)
    if success:
        return jsonify({"success": True, "message": "Record deleted successfully."}), 200
    else:
        return jsonify({"success": False, "error": "Record could not be found or deleted."}), 404

@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Returns dynamic KPI counts for dashboard updates."""
    stats = get_dashboard_stats()
    return jsonify({"success": True, "data": stats})

@app.route("/api/analytics-data", methods=["GET"])
def api_analytics_data():
    """Returns aggregated distribution data for all Chart.js visualizations."""
    data = get_analytics_data()
    return jsonify({"success": True, "data": data})

# ==========================================
# Error Handlers
# ==========================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html", active_page="", error_content="404 - Page Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("base.html", active_page="", error_content="500 - Internal Server Error"), 500

if __name__ == "__main__":
    print(f"[*] Starting PathFinder AI on http://{config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=False, use_reloader=False)
