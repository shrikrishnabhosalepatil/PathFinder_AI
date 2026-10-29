"""
Career Guidance and Placement Assessment Engine for PathFinder AI.
Evaluates student competencies across academic, technical, communication, and
practical experience pillars, identifies skill gaps for chosen career domains,
and generates actionable improvement roadmaps.
"""

from typing import Dict, List, Any
import config

def calculate_readiness_score(cgpa: float, aptitude: float, tech: float, comm: float, internships: int, projects: int, backlogs: int) -> float:
    """
    Computes an interpretable 0-100 Placement Readiness Index.
    Separate from the Random Forest probabilistic output to provide a holistic,
    actionable assessment of career preparation.

    Weights:
    - CGPA: 25% (normalized from 10)
    - Aptitude: 20% (0-100)
    - Technical Score: 25% (normalized from 10)
    - Communication Score: 15% (normalized from 10)
    - Practical Experience: 15% (Internships + Projects)
    - Penalty: Active backlogs deduct 10 points each.
    """
    norm_cgpa = min(max(cgpa * 10.0, 0.0), 100.0)
    norm_aptitude = min(max(aptitude, 0.0), 100.0)
    norm_tech = min(max(tech * 10.0, 0.0), 100.0)
    norm_comm = min(max(comm * 10.0, 0.0), 100.0)

    # Experience index: internships (up to 2 * 25 pts) + projects (up to 4 * 12.5 pts) -> max 100
    exp_pts = (min(internships, 2) * 25.0) + (min(projects, 4) * 12.5)
    norm_exp = min(exp_pts, 100.0)

    raw_score = (
        (norm_cgpa * config.READINESS_WEIGHTS["cgpa"]) +
        (norm_aptitude * config.READINESS_WEIGHTS["aptitude_score"]) +
        (norm_tech * config.READINESS_WEIGHTS["technical_score"]) +
        (norm_comm * config.READINESS_WEIGHTS["communication_score"]) +
        (norm_exp * config.READINESS_WEIGHTS["experience"])
    )

    # Apply penalty for active backlogs
    backlog_penalty = backlogs * 10.0
    final_score = max(0.0, min(100.0, raw_score - backlog_penalty))
    return round(final_score, 1)

def generate_pillar_assessments(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates detailed qualitative assessments and actionable feedback for each pillar.
    """
    cgpa = float(data["cgpa"])
    aptitude = float(data["aptitude_score"])
    tech = float(data["technical_score"])
    comm = float(data["communication_score"])
    internships = int(data["internships"])
    projects = int(data["projects"])
    backlogs = int(data["backlogs"])

    # 1. Academic Assessment
    if backlogs > 0:
        acad_status = "At Risk"
        acad_badge = "badge-danger"
        acad_summary = f"Student has {backlogs} active backlog(s). Campus recruitment eligibility commonly requires 0 standing backlogs."
    elif cgpa >= 8.5:
        acad_status = "Distinction / Excellent"
        acad_badge = "badge-success"
        acad_summary = f"CGPA of {cgpa:.2f} qualifies student for Tier-1 product companies and premier recruitment rounds."
    elif cgpa >= 7.0:
        acad_status = "Solid Academic Standing"
        acad_badge = "badge-primary"
        acad_summary = f"CGPA of {cgpa:.2f} clears majority IT service and product company cutoffs (typically 6.5-7.0)."
    else:
        acad_status = "Borderline Cutoff"
        acad_badge = "badge-warning"
        acad_summary = f"CGPA of {cgpa:.2f} is close to minimum cutoff thresholds; focus on scoring high in semester exams."

    # 2. Technical Skills Assessment
    if tech >= 8.0:
        tech_status = "Advanced Developer"
        tech_badge = "badge-success"
        tech_summary = "Strong problem-solving, architectural awareness, and coding fluency suitable for technical rounds."
    elif tech >= 6.0:
        tech_status = "Competent / Industry-Ready"
        tech_badge = "badge-primary"
        tech_summary = "Solid core programming fundamentals. Target DSA optimization and clean code practices."
    else:
        tech_status = "Foundational Need"
        tech_badge = "badge-warning"
        tech_summary = "Technical rating indicates need for intensive practice in Data Structures, Algorithms, and debugging."

    # 3. Communication Assessment
    if comm >= 8.0:
        comm_status = "Exceptional Articulation"
        comm_badge = "badge-success"
        comm_summary = "High clarity in technical explanations and managerial/HR interview rounds."
    elif comm >= 6.0:
        comm_status = "Effective Communicator"
        comm_badge = "badge-primary"
        comm_summary = "Able to express project contributions clearly; fine-tune behavioral STAR-method responses."
    else:
        comm_status = "Needs Practice"
        comm_badge = "badge-warning"
        comm_summary = "Practice mock interviews and technical presentation delivery to boost confidence."

    # 4. Practical Experience Assessment
    exp_status = "Strong Portfolio" if (internships >= 1 and projects >= 2) else ("Moderate Experience" if projects >= 2 else "Limited Practical Exposure")
    exp_badge = "badge-success" if exp_status == "Strong Portfolio" else ("badge-primary" if exp_status == "Moderate Experience" else "badge-warning")
    exp_summary = f"{internships} internship(s) and {projects} project(s) completed. "
    if internships == 0:
        exp_summary += "Securing at least one summer internship or open-source contribution will substantially boost profile visibility."
    else:
        exp_summary += "Practical internship experience gives a strong competitive advantage in resume screening."

    # 5. Targeted Recommendations
    recommendations = []
    if backlogs > 0:
        recommendations.append("Priority 1: Clear all active backlogs before placement season begins, as most recruiters impose strict zero-backlog criteria.")
    if cgpa < 7.0:
        recommendations.append("Strive to bring aggregate CGPA above 7.0 to unlock eligibility for product company hiring drives.")
    if aptitude < 70.0:
        recommendations.append("Practice quantitative aptitude, logical reasoning, and data interpretation (e.g., Indiabix, PrepInsta) for 30 mins daily.")
    if tech < 7.0:
        recommendations.append("Strengthen Data Structures & Algorithms on LeetCode/GeeksforGeeks; aim to solve at least 100 Medium problems.")
    if projects < 2:
        recommendations.append("Build at least two end-to-end deployed capstone projects on GitHub with comprehensive README documentation.")
    if comm < 7.0:
        recommendations.append("Participate in group discussions and record mock technical presentations using the STAR technique (Situation, Task, Action, Result).")

    if not recommendations:
        recommendations.append("Excellent overall profile! Focus on domain-specific system design interview questions and competitive coding speed.")

    return {
        "academic": {"status": acad_status, "badge": acad_badge, "summary": acad_summary},
        "technical": {"status": tech_status, "badge": tech_badge, "summary": tech_summary},
        "communication": {"status": comm_status, "badge": comm_badge, "summary": comm_summary},
        "experience": {"status": exp_status, "badge": exp_badge, "summary": exp_summary},
        "recommendations": recommendations
    }

def get_career_guidance_for_student(domain_name: str, programming_skills_str: str) -> Dict[str, Any]:
    """
    Performs gap analysis between the student's declared skills and the selected career domain.
    """
    domain = config.CAREER_DOMAINS.get(domain_name, config.CAREER_DOMAINS["Software Developer"])

    # Parse student skills into a normalized set
    raw_skills = [s.strip().lower() for s in programming_skills_str.split(",") if s.strip()]
    
    # Check match against recommended languages and core skills
    matched_skills = []
    missing_skills = []

    # Map aliases for checking
    for skill in domain["core_skills"]:
        skill_lower = skill.lower()
        if any(term in skill_lower or skill_lower in term for term in raw_skills):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    for lang in domain["recommended_languages"]:
        lang_lower = lang.lower()
        if any(term in lang_lower or lang_lower in term for term in raw_skills):
            if lang not in matched_skills:
                matched_skills.append(lang)
        else:
            if lang not in missing_skills:
                missing_skills.append(lang)

    return {
        "domain_key": domain_name,
        "title": domain["title"],
        "badge": domain["badge"],
        "icon": domain["icon"],
        "description": domain["description"],
        "core_skills": domain["core_skills"],
        "recommended_languages": domain["recommended_languages"],
        "matched_skills": matched_skills,
        "missing_skills": missing_skills[:4],  # Highlight top missing skills
        "learning_roadmap": domain["learning_roadmap"],
        "project_ideas": domain["project_ideas"],
        "interview_tips": domain["interview_tips"]
    }
