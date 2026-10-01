import os
import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://sahakar:sahakar_dev_password@localhost:5432/sahakar_link")

def calculate_skill_match(student_skills: list[str], required_skills: list[str]) -> tuple[float, list[str], list[str]]:
    """Calculates match score based on verified skill overlaps."""
    if not required_skills:
        return 100.0, student_skills, []

    student_set = set(s.lower() for s in student_skills)
    required_set = set(s.lower() for s in required_skills)

    matched = list(student_set.intersection(required_set))
    missing = list(required_set.difference(student_set))

    score = round((len(matched) / len(required_set)) * 100, 2)
    return score, matched, missing

def generate_grounded_explanation(candidate_name: str, job_title: str, matched_skills: list[str], missing_skills: list[str], score: float) -> str:
    """Generates an evidence-backed match explanation for employers."""
    matched_str = ", ".join(matched_skills) if matched_skills else "None"
    missing_str = ", ".join(missing_skills) if missing_skills else "None"

    return (
        f"Candidate {candidate_name} achieves a {score}% skill match for the {job_title} role. "
        f"Verified evidence confirmed for: [{matched_str}]. "
        f"Gaps identified in required skills: [{missing_str}]."
    )
