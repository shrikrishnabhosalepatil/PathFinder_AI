"""
Comprehensive Unit and Integration Test Suite for PathFinder AI.
Tests web routes, prediction API, validation rules, SQLite database operations,
and model handling.
"""

import sys
import os
import unittest
import json
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import config
from app import app
from database import (
    init_db,
    insert_prediction,
    get_all_predictions,
    get_prediction_by_id,
    delete_prediction,
    get_dashboard_stats,
    get_analytics_data
)
from predictor import validate_student_input, predict_student_placement

class TestPathFinderAI(unittest.TestCase):

    def setUp(self):
        """Set up Flask test client and ensure clean test database."""
        app.config["TESTING"] = True
        self.client = app.test_client()
        init_db()

    # ---------------------------------------------------------
    # Route Availability Tests
    # ---------------------------------------------------------

    def test_homepage_loads(self):
        """Verify homepage / dashboard returns 200 OK."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PathFinder AI", response.data)
        self.assertIn(b"Placement Intelligence Overview", response.data)

    def test_predict_page_loads(self):
        """Verify prediction form page returns 200 OK."""
        response = self.client.get("/predict")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Placement Prediction Form", response.data)

    def test_history_page_loads(self):
        """Verify history page returns 200 OK."""
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Historical Evaluations", response.data)

    def test_analytics_page_loads(self):
        """Verify analytics page returns 200 OK."""
        response = self.client.get("/analytics")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Cohort Placement", response.data)

    def test_career_guidance_page_loads(self):
        """Verify career guidance page loads successfully."""
        response = self.client.get("/career-guidance")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Career Domain Guidance", response.data)

    def test_model_info_page_loads(self):
        """Verify model transparency page returns 200 OK."""
        response = self.client.get("/model-info")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Random Forest Feature Importance", response.data)

    # ---------------------------------------------------------
    # Server-Side Input Validation Tests
    # ---------------------------------------------------------

    def test_validation_valid_input(self):
        """Verify valid student payload passes validation."""
        valid_payload = {
            "student_name": "Test Candidate",
            "cgpa": 8.5,
            "aptitude_score": 85.0,
            "technical_score": 8.0,
            "communication_score": 7.5,
            "internships": 1,
            "projects": 3,
            "backlogs": 0,
            "programming_skills": "Python, SQL",
            "preferred_domain": "Software Developer"
        }
        is_valid, err, sanitized = validate_student_input(valid_payload)
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertEqual(sanitized["student_name"], "Test Candidate")

    def test_validation_invalid_cgpa(self):
        """Verify out-of-range CGPA is rejected."""
        payload = {
            "student_name": "Invalid CGPA Student",
            "cgpa": 11.5,  # Invalid
            "aptitude_score": 70.0,
            "technical_score": 7.0,
            "communication_score": 7.0,
            "internships": 1,
            "projects": 2,
            "backlogs": 0
        }
        is_valid, err, _ = validate_student_input(payload)
        self.assertFalse(is_valid)
        self.assertIn("CGPA must be between 0.0 and 10.0", err)

    def test_validation_negative_backlogs(self):
        """Verify negative backlogs are rejected."""
        payload = {
            "student_name": "Negative Backlog Student",
            "cgpa": 7.5,
            "aptitude_score": 70.0,
            "technical_score": 7.0,
            "communication_score": 7.0,
            "internships": 0,
            "projects": 1,
            "backlogs": -2  # Invalid
        }
        is_valid, err, _ = validate_student_input(payload)
        self.assertFalse(is_valid)
        self.assertIn("Active backlogs must be a non-negative integer", err)

    def test_validation_missing_name(self):
        """Verify missing student name is rejected."""
        payload = {
            "student_name": "",  # Missing
            "cgpa": 7.5,
            "aptitude_score": 70.0,
            "technical_score": 7.0,
            "communication_score": 7.0,
            "internships": 0,
            "projects": 1,
            "backlogs": 0
        }
        is_valid, err, _ = validate_student_input(payload)
        self.assertFalse(is_valid)

    # ---------------------------------------------------------
    # API Prediction Tests
    # ---------------------------------------------------------

    def test_api_predict_success(self):
        """Verify POST /api/predict returns placement likelihood, readiness, and record_id."""
        payload = {
            "student_name": "Integration Test Student",
            "cgpa": 8.75,
            "aptitude_score": 85.0,
            "technical_score": 8.5,
            "communication_score": 8.0,
            "internships": 2,
            "projects": 4,
            "backlogs": 0,
            "programming_skills": "Python, SQL, React",
            "preferred_domain": "Software Developer"
        }
        response = self.client.post(
            "/api/predict",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertTrue(data["success"])
        self.assertIn("placement_probability", data)
        self.assertIn("readiness_score", data)
        self.assertIn("predicted_category", data)
        self.assertIn("assessments", data)
        self.assertIn("record_id", data)
        self.assertGreater(data["placement_probability"], 60.0)

    def test_api_predict_invalid(self):
        """Verify POST /api/predict handles invalid payload with 400 Bad Request."""
        payload = {
            "student_name": "Bad Input",
            "cgpa": -1.0,  # Invalid
            "aptitude_score": 80.0,
            "technical_score": 5.0,
            "communication_score": 5.0,
            "internships": 0,
            "projects": 0,
            "backlogs": 0
        }
        response = self.client.post(
            "/api/predict",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    # ---------------------------------------------------------
    # Database CRUD & API Record Operations
    # ---------------------------------------------------------

    def test_database_crud_workflow(self):
        """Verify insert, retrieve, search, and delete database operations."""
        sample_record = {
            "student_name": "Unique Database Test Student",
            "cgpa": 8.4,
            "aptitude_score": 80.0,
            "technical_score": 8.0,
            "communication_score": 8.0,
            "internships": 1,
            "projects": 2,
            "backlogs": 0,
            "programming_skills": "Python",
            "preferred_domain": "Data Analyst",
            "predicted_category": "High Placement Likelihood",
            "placement_probability": 88.0,
            "readiness_score": 85.0
        }

        # 1. Insert
        record_id = insert_prediction(sample_record)
        self.assertIsNotNone(record_id)
        self.assertGreater(record_id, 0)

        # 2. Retrieve by ID
        fetched = get_prediction_by_id(record_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["student_name"], "Unique Database Test Student")

        # 3. Search
        search_res = get_all_predictions(search_query="Unique Database")
        self.assertTrue(len(search_res) >= 1)

        # 4. API GET details
        api_get_resp = self.client.get(f"/api/prediction/{record_id}")
        self.assertEqual(api_get_resp.status_code, 200)

        # 5. Delete
        delete_resp = self.client.delete(f"/api/prediction/{record_id}")
        self.assertEqual(delete_resp.status_code, 200)

        # 6. Verify deleted
        post_delete = get_prediction_by_id(record_id)
        self.assertIsNone(post_delete)

    # ---------------------------------------------------------
    # Stats & Analytics Endpoints
    # ---------------------------------------------------------

    def test_api_stats_endpoint(self):
        """Verify /api/stats returns valid aggregate KPI metrics."""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("total_students", data["data"])
        self.assertIn("avg_readiness", data["data"])

    def test_api_analytics_endpoint(self):
        """Verify /api/analytics-data returns structured Chart.js payload."""
        response = self.client.get("/api/analytics-data")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("category_distribution", data["data"])
        self.assertIn("cgpa_distribution", data["data"])

if __name__ == "__main__":
    unittest.main()
