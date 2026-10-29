"""
Configuration module for PathFinder AI.
Centralizes paths, feature definitions, scoring weights, and career domain data.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
DATASET_PATH = DATA_DIR / "placement_dataset.csv"
MODEL_PATH = MODELS_DIR / "placement_model.pkl"
METRICS_PATH = MODELS_DIR / "model_metrics.json"
DATABASE_PATH = DATA_DIR / "pathfinder.db"

# Flask Configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "pathfinder-ai-secret-key-2026-college-demo")
DEBUG = False
HOST = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
PORT = int(os.environ.get("PORT", 5000))

# Machine Learning Feature Schema
FEATURE_COLUMNS = [
    "cgpa",
    "aptitude_score",
    "technical_score",
    "communication_score",
    "internships",
    "projects",
    "backlogs"
]

# Readiness Score Composite Weights
READINESS_WEIGHTS = {
    "cgpa": 0.25,            # Normalized from 0-10 to 0-100
    "aptitude_score": 0.20,  # 0-100
    "technical_score": 0.25, # Normalized from 1-10 to 0-100
    "communication_score": 0.15, # Normalized from 1-10 to 0-100
    "experience": 0.15       # Combined internships (up to 3) and projects (up to 5)
}

# Career Domains Knowledge Base
CAREER_DOMAINS = {
    "Software Developer": {
        "title": "Software Development Engineer (SDE / Full Stack)",
        "badge": "bg-primary",
        "icon": "bi-code-slash",
        "description": "Designs, builds, and maintains robust software systems, enterprise applications, and cloud-native backend services.",
        "core_skills": ["Data Structures & Algorithms", "Object-Oriented Programming", "System Design", "Git & CI/CD", "Databases (SQL/NoSQL)"],
        "recommended_languages": ["Java", "Python", "C++", "JavaScript", "Go"],
        "learning_roadmap": [
            {"phase": "Foundational", "topic": "Master DSA (Arrays, Trees, Graphs, DP) in Java/C++/Python, OOP principles."},
            {"phase": "Intermediate", "topic": "Build RESTful APIs with Flask/Spring Boot/Node, relational database design with PostgreSQL/MySQL."},
            {"phase": "Advanced", "topic": "Microservices architecture, Docker, caching with Redis, system design (HLD & LLD)."}
        ],
        "project_ideas": [
            {"title": "Distributed Task Scheduler", "difficulty": "Intermediate", "tech": "Python / Redis / SQLite"},
            {"title": "Real-time Collaborative Code Editor", "difficulty": "Advanced", "tech": "Node.js / WebSockets / React"},
            {"title": "Campus Placement Portal & Applicant Tracker", "difficulty": "Intermediate", "tech": "Flask / PostgreSQL / Bootstrap"}
        ],
        "interview_tips": [
            "Practice LeetCode Medium problems daily; focus on Two Pointers, BFS/DFS, and Dynamic Programming.",
            "Be ready to explain time and space complexity (Big-O notation) for every code solution.",
            "Review core CS fundamentals: OS processes vs threads, DB indexing, ACID properties, and HTTP/HTTPS protocols."
        ]
    },
    "Data Analyst": {
        "title": "Data Analyst / Business Intelligence Engineer",
        "badge": "bg-success",
        "icon": "bi-graph-up-arrow",
        "description": "Transforms raw transactional data into actionable business intelligence through statistical modeling, dashboards, and KPI reporting.",
        "core_skills": ["SQL (Advanced Queries & Window Functions)", "Python / R", "Data Visualization (Tableau/Power BI)", "Statistical Analysis", "Excel/Spreadsheets"],
        "recommended_languages": ["SQL", "Python", "R"],
        "learning_roadmap": [
            {"phase": "Foundational", "topic": "Master SQL (JOINs, Window Functions, CTEs) and descriptive/inferential statistics."},
            {"phase": "Intermediate", "topic": "Data manipulation in Python (pandas, NumPy) and exploratory data analysis (EDA)."},
            {"phase": "Advanced", "topic": "Interactive business dashboards in Power BI/Tableau and basic forecasting/regression modeling."}
        ],
        "project_ideas": [
            {"title": "E-Commerce Customer Retention & Cohort Analysis", "difficulty": "Intermediate", "tech": "Python / pandas / Tableau"},
            {"title": "Healthcare Clinical Outcomes Dashboard", "difficulty": "Intermediate", "tech": "SQL / Power BI / Seaborn"},
            {"title": "Automated Financial Portfolio Tracker", "difficulty": "Advanced", "tech": "Python / yfinance / Streamlit"}
        ],
        "interview_tips": [
            "Expect live SQL coding challenges covering self-joins, window functions (ROW_NUMBER, DENSE_RANK), and aggregation.",
            "Prepare a portfolio case study explaining how your data insights influenced a business decision.",
            "Review hypothesis testing, p-values, A/B testing methodology, and common statistical biases."
        ]
    },
    "Machine Learning Engineer": {
        "title": "Machine Learning Engineer / AI Developer",
        "badge": "bg-info text-dark",
        "icon": "bi-cpu",
        "description": "Designs and deploys scalable machine learning and deep learning models into production environments.",
        "core_skills": ["Machine Learning Algorithms (Supervised & Unsupervised)", "scikit-learn & PyTorch/TensorFlow", "Feature Engineering", "Model Evaluation & Tuning", "MLOps & API Deployment"],
        "recommended_languages": ["Python", "C++", "SQL"],
        "learning_roadmap": [
            {"phase": "Foundational", "topic": "Linear algebra, multivariate calculus, probability, and foundational scikit-learn models."},
            {"phase": "Intermediate", "topic": "Deep learning architectures (CNNs, RNNs, Transformers), hyperparameter tuning, model serving with FastAPI."},
            {"phase": "Advanced", "topic": "MLOps pipelines (MLflow, DVC, Docker), model monitoring, drift detection, and LLM fine-tuning."}
        ],
        "project_ideas": [
            {"title": "End-to-End Placement Prediction Pipeline", "difficulty": "Intermediate", "tech": "Flask / scikit-learn / SQLite"},
            {"title": "Medical Imaging Diagnostic Classifier", "difficulty": "Advanced", "tech": "PyTorch / ResNet / Grad-CAM"},
            {"title": "Automated Resume Screener & Skill Matcher", "difficulty": "Intermediate", "tech": "NLP / spaCy / TF-IDF"}
        ],
        "interview_tips": [
            "Be prepared to mathematically explain the Bias-Variance tradeoff, regularization (L1/L2), and gradient descent.",
            "Know when to choose specific evaluation metrics: precision vs recall vs AUC-ROC on imbalanced datasets.",
            "Discuss real production challenges: data leakage, feature store latency, and model drift in live traffic."
        ]
    },
    "Cloud/DevOps Engineer": {
        "title": "Cloud Platform & DevOps Engineer",
        "badge": "bg-warning text-dark",
        "icon": "bi-cloud-check",
        "description": "Automates continuous integration, infrastructure orchestration, and ensures high availability of cloud systems.",
        "core_skills": ["Linux System Administration", "Containerization (Docker)", "Kubernetes Orchestration", "CI/CD Pipelines (GitHub Actions/Jenkins)", "Infrastructure as Code (Terraform)"],
        "recommended_languages": ["Bash/Shell", "Python", "Go", "YAML"],
        "learning_roadmap": [
            {"phase": "Foundational", "topic": "Linux shell scripting, networking fundamentals (DNS, TCP/IP, VPC, load balancers), Git workflows."},
            {"phase": "Intermediate", "topic": "Docker containerization, AWS/GCP cloud services (EC2, S3, IAM), automated CI/CD pipelines."},
            {"phase": "Advanced", "topic": "Kubernetes cluster management, Terraform IaC, Prometheus & Grafana telemetry and observability."}
        ],
        "project_ideas": [
            {"title": "Automated Multi-Stage CI/CD Pipeline for Microservices", "difficulty": "Intermediate", "tech": "GitHub Actions / Docker / AWS"},
            {"title": "Self-Healing Kubernetes Cluster with Monitoring", "difficulty": "Advanced", "tech": "K8s / Helm / Prometheus / Grafana"},
            {"title": "Serverless Event-Driven Image Processing Pipeline", "difficulty": "Intermediate", "tech": "AWS Lambda / S3 / Terraform"}
        ],
        "interview_tips": [
            "Master Linux command line, permissions, process management, and networking diagnostics (netstat, curl, tcpdump).",
            "Be ready to white-board a blue-green or canary zero-downtime deployment strategy.",
            "Familiarize yourself with AWS/Azure/GCP foundational architecture certifications (AWS SAA or Azure Fundamentals)."
        ]
    },
    "Cybersecurity Analyst": {
        "title": "Cybersecurity Analyst / Information Security Specialist",
        "badge": "bg-danger",
        "icon": "bi-shield-lock",
        "description": "Protects organizational information systems, monitors threat vectors, performs vulnerability assessments, and ensures compliance.",
        "core_skills": ["Network Security & Protocols", "Vulnerability Assessment & Pen Testing", "SIEM & Log Analysis", "Incident Response", "Cryptography Fundamentals"],
        "recommended_languages": ["Python", "Bash", "PowerShell", "C"],
        "learning_roadmap": [
            {"phase": "Foundational", "topic": "Network OSI model, TCP/IP handshake, firewalls, symmetric/asymmetric encryption, OWASP Top 10."},
            {"phase": "Intermediate", "topic": "Vulnerability scanning with Nmap/Wireshark/Burp Suite, SIEM log monitoring (Splunk, Wazuh)."},
            {"phase": "Advanced", "topic": "Penetration testing methodologies, malware reverse engineering, security compliance frameworks (NIST, ISO 27001)."}
        ],
        "project_ideas": [
            {"title": "Automated Network Intrusion Detection System", "difficulty": "Advanced", "tech": "Python / Scapy / Snort"},
            {"title": "OWASP Vulnerability Scanner & Audit Reporter", "difficulty": "Intermediate", "tech": "Python / Requests / BeautifulSoup"},
            {"title": "Secure Zero-Trust Identity & Access Management Demo", "difficulty": "Intermediate", "tech": "Flask / JWT / OAuth2 / Argon2"}
        ],
        "interview_tips": [
            "Demonstrate a solid understanding of the OWASP Top 10 web vulnerabilities (SQLi, XSS, CSRF, IDOR).",
            "Walk through incident triage scenarios: how would you detect and contain an active ransomware infection?",
            "Highlight practical lab experience on platforms like TryHackMe or Hack The Box."
        ]
    }
}
