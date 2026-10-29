"""
Database access layer for PathFinder AI using SQLite3.
Implements parameterized queries, connection management, table creation,
CRUD operations, and aggregate queries for analytics dashboards.
"""

import sqlite3
from typing import Dict, List, Optional, Any
from pathlib import Path
import config

def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dict-like row access."""
    conn = sqlite3.connect(str(config.DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite database and tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            cgpa REAL NOT NULL,
            aptitude_score REAL NOT NULL,
            technical_score REAL NOT NULL,
            communication_score REAL NOT NULL,
            internships INTEGER NOT NULL,
            projects INTEGER NOT NULL,
            backlogs INTEGER NOT NULL,
            programming_skills TEXT NOT NULL,
            preferred_domain TEXT NOT NULL,
            predicted_category TEXT NOT NULL,
            placement_probability REAL NOT NULL,
            readiness_score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_student_name ON predictions(student_name);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created_at ON predictions(created_at);
    """)

    conn.commit()

    # Check if we should populate realistic seed data
    cursor.execute("SELECT COUNT(*) as count FROM predictions")
    count = cursor.fetchone()["count"]
    if count == 0:
        seed_sample_records(conn)

    conn.close()

def seed_sample_records(conn: sqlite3.Connection):
    """Inserts initial realistic records so the dashboard has immediate analytics."""
    sample_students = [
        {
            "student_name": "Aarav Sharma",
            "cgpa": 8.75,
            "aptitude_score": 88.0,
            "technical_score": 9.0,
            "communication_score": 8.5,
            "internships": 2,
            "projects": 4,
            "backlogs": 0,
            "programming_skills": "Python, SQL, React, Git",
            "preferred_domain": "Software Developer",
            "predicted_category": "High Placement Likelihood",
            "placement_probability": 94.2,
            "readiness_score": 91.5
        },
        {
            "student_name": "Priya Nair",
            "cgpa": 9.20,
            "aptitude_score": 92.5,
            "technical_score": 9.5,
            "communication_score": 9.0,
            "internships": 2,
            "projects": 5,
            "backlogs": 0,
            "programming_skills": "Python, PyTorch, SQL, Scikit-Learn",
            "preferred_domain": "Machine Learning Engineer",
            "predicted_category": "High Placement Likelihood",
            "placement_probability": 97.6,
            "readiness_score": 95.8
        },
        {
            "student_name": "Rohan Verma",
            "cgpa": 7.30,
            "aptitude_score": 68.0,
            "technical_score": 6.5,
            "communication_score": 7.0,
            "internships": 1,
            "projects": 2,
            "backlogs": 0,
            "programming_skills": "Java, Spring Boot, MySQL",
            "preferred_domain": "Software Developer",
            "predicted_category": "Moderate Placement Likelihood",
            "placement_probability": 68.4,
            "readiness_score": 71.0
        },
        {
            "student_name": "Ananya Iyer",
            "cgpa": 8.10,
            "aptitude_score": 82.0,
            "technical_score": 8.0,
            "communication_score": 8.5,
            "internships": 1,
            "projects": 3,
            "backlogs": 0,
            "programming_skills": "Python, SQL, Tableau, Excel",
            "preferred_domain": "Data Analyst",
            "predicted_category": "High Placement Likelihood",
            "placement_probability": 89.1,
            "readiness_score": 86.4
        },
        {
            "student_name": "Kabir Patel",
            "cgpa": 6.40,
            "aptitude_score": 52.0,
            "technical_score": 5.0,
            "communication_score": 5.5,
            "internships": 0,
            "projects": 1,
            "backlogs": 1,
            "programming_skills": "C++, HTML, CSS",
            "preferred_domain": "Cloud/DevOps Engineer",
            "predicted_category": "Needs Improvement / At Risk",
            "placement_probability": 34.0,
            "readiness_score": 52.5
        },
        {
            "student_name": "Sneha Kulkarni",
            "cgpa": 7.85,
            "aptitude_score": 75.0,
            "technical_score": 7.5,
            "communication_score": 8.0,
            "internships": 1,
            "projects": 3,
            "backlogs": 0,
            "programming_skills": "Linux, Bash, Docker, Python",
            "preferred_domain": "Cloud/DevOps Engineer",
            "predicted_category": "High Placement Likelihood",
            "placement_probability": 82.7,
            "readiness_score": 81.2
        },
        {
            "student_name": "Devansh Singh",
            "cgpa": 6.95,
            "aptitude_score": 64.0,
            "technical_score": 6.0,
            "communication_score": 6.5,
            "internships": 0,
            "projects": 2,
            "backlogs": 0,
            "programming_skills": "Python, Wireshark, Linux",
            "preferred_domain": "Cybersecurity Analyst",
            "predicted_category": "Moderate Placement Likelihood",
            "placement_probability": 61.5,
            "readiness_score": 67.8
        },
        {
            "student_name": "Meera Joshi",
            "cgpa": 5.80,
            "aptitude_score": 45.0,
            "technical_score": 4.5,
            "communication_score": 5.0,
            "internships": 0,
            "projects": 1,
            "backlogs": 2,
            "programming_skills": "C, Java",
            "preferred_domain": "Software Developer",
            "predicted_category": "Needs Improvement / At Risk",
            "placement_probability": 18.2,
            "readiness_score": 44.0
        }
    ]

    cursor = conn.cursor()
    for s in sample_students:
        cursor.execute("""
            INSERT INTO predictions (
                student_name, cgpa, aptitude_score, technical_score,
                communication_score, internships, projects, backlogs,
                programming_skills, preferred_domain, predicted_category,
                placement_probability, readiness_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["student_name"], s["cgpa"], s["aptitude_score"], s["technical_score"],
            s["communication_score"], s["internships"], s["projects"], s["backlogs"],
            s["programming_skills"], s["preferred_domain"], s["predicted_category"],
            s["placement_probability"], s["readiness_score"]
        ))
    conn.commit()

def insert_prediction(data: Dict[str, Any]) -> int:
    """Inserts a new prediction record and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions (
            student_name, cgpa, aptitude_score, technical_score,
            communication_score, internships, projects, backlogs,
            programming_skills, preferred_domain, predicted_category,
            placement_probability, readiness_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["student_name"].strip(),
        float(data["cgpa"]),
        float(data["aptitude_score"]),
        float(data["technical_score"]),
        float(data["communication_score"]),
        int(data["internships"]),
        int(data["projects"]),
        int(data["backlogs"]),
        data.get("programming_skills", "").strip(),
        data.get("preferred_domain", "Software Developer").strip(),
        data["predicted_category"],
        float(data["placement_probability"]),
        float(data["readiness_score"])
    ))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_all_predictions(limit: Optional[int] = None, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves prediction records with optional search filter and limit."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM predictions"
    params = []

    if search_query and search_query.strip():
        query += " WHERE student_name LIKE ? OR preferred_domain LIKE ?"
        term = f"%{search_query.strip()}%"
        params.extend([term, term])

    query += " ORDER BY id DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def get_prediction_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single prediction record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None

def delete_prediction(record_id: int) -> bool:
    """Deletes a prediction record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    return rows_affected > 0

def get_dashboard_stats() -> Dict[str, Any]:
    """Computes aggregate summary statistics for dashboard KPI cards."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*) as total_students,
            AVG(readiness_score) as avg_readiness,
            AVG(placement_probability) as avg_probability,
            AVG(cgpa) as avg_cgpa,
            AVG(aptitude_score) as avg_aptitude,
            AVG(technical_score) as avg_tech,
            AVG(communication_score) as avg_comm
        FROM predictions
    """)
    summary = cursor.fetchone()

    # Category counts
    cursor.execute("""
        SELECT predicted_category, COUNT(*) as count 
        FROM predictions 
        GROUP BY predicted_category
    """)
    category_rows = cursor.fetchall()

    categories = {
        "High Placement Likelihood": 0,
        "Moderate Placement Likelihood": 0,
        "Needs Improvement / At Risk": 0
    }
    for row in category_rows:
        cat = row["predicted_category"]
        if cat in categories:
            categories[cat] = row["count"]
        else:
            categories[cat] = row["count"]

    conn.close()

    total = summary["total_students"] or 0
    return {
        "total_students": total,
        "avg_readiness": round(summary["avg_readiness"] or 0.0, 1),
        "avg_probability": round(summary["avg_probability"] or 0.0, 1),
        "avg_cgpa": round(summary["avg_cgpa"] or 0.0, 2),
        "avg_aptitude": round(summary["avg_aptitude"] or 0.0, 1),
        "avg_tech": round(summary["avg_tech"] or 0.0, 1),
        "avg_comm": round(summary["avg_comm"] or 0.0, 1),
        "category_counts": categories
    }

def get_analytics_data() -> Dict[str, Any]:
    """Returns structured data suitable for all Chart.js visualizations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, student_name, cgpa, aptitude_score, technical_score, 
               communication_score, internships, projects, backlogs,
               preferred_domain, predicted_category, placement_probability,
               readiness_score, created_at
        FROM predictions
        ORDER BY id ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not rows:
        return {
            "has_data": False,
            "category_distribution": {},
            "cgpa_distribution": {},
            "tech_vs_comm": [],
            "cgpa_vs_probability": [],
            "domain_distribution": {},
            "backlog_impact": {}
        }

    # 1. Category Distribution
    category_counts = {}
    for r in rows:
        cat = r["predicted_category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # 2. CGPA Distribution Bins: <6.0, 6.0-7.0, 7.0-8.0, 8.0-9.0, >=9.0
    cgpa_bins = {
        "< 6.0": 0,
        "6.0 - 6.99": 0,
        "7.0 - 7.99": 0,
        "8.0 - 8.99": 0,
        "9.0 - 10.0": 0
    }
    for r in rows:
        g = r["cgpa"]
        if g < 6.0:
            cgpa_bins["< 6.0"] += 1
        elif g < 7.0:
            cgpa_bins["6.0 - 6.99"] += 1
        elif g < 8.0:
            cgpa_bins["7.0 - 7.99"] += 1
        elif g < 9.0:
            cgpa_bins["8.0 - 8.99"] += 1
        else:
            cgpa_bins["9.0 - 10.0"] += 1

    # 3. Tech vs Comm correlation scatter points
    tech_vs_comm = [
        {"x": r["technical_score"], "y": r["communication_score"], "name": r["student_name"], "prob": r["placement_probability"]}
        for r in rows
    ]

    # 4. CGPA vs Probability scatter points
    cgpa_vs_probability = [
        {"x": r["cgpa"], "y": r["placement_probability"], "name": r["student_name"], "readiness": r["readiness_score"]}
        for r in rows
    ]

    # 5. Domain Distribution
    domain_counts = {}
    for r in rows:
        d = r["preferred_domain"] or "General Software"
        domain_counts[d] = domain_counts.get(d, 0) + 1

    # 6. Backlog impact on average placement probability
    backlog_groups: Dict[int, List[float]] = {}
    for r in rows:
        b = min(r["backlogs"], 3)  # Group 3+ together
        if b not in backlog_groups:
            backlog_groups[b] = []
        backlog_groups[b].append(r["placement_probability"])

    backlog_impact = {}
    for b in sorted(backlog_groups.keys()):
        label = f"{b} Backlogs" if b < 3 else "3+ Backlogs"
        if b == 0:
            label = "0 (Clean)"
        avg_prob = sum(backlog_groups[b]) / len(backlog_groups[b])
        backlog_impact[label] = round(avg_prob, 1)

    return {
        "has_data": True,
        "total_records": len(rows),
        "category_distribution": category_counts,
        "cgpa_distribution": cgpa_bins,
        "tech_vs_comm": tech_vs_comm,
        "cgpa_vs_probability": cgpa_vs_probability,
        "domain_distribution": domain_counts,
        "backlog_impact": backlog_impact
    }
