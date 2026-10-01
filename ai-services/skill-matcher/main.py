from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service import calculate_skill_match, generate_grounded_explanation

app = FastAPI(
    title="Sahakar-Link Skill Matcher Service",
    description="Employer Candidate Ranking & Grounded Skill Verification Matcher",
    version="1.0.0"
)

class MatchRequest(BaseModel):
    student_id: str
    student_name: str
    student_skills: list[str]
    job_id: str
    job_title: str
    required_skills: list[str]

@app.post("/api/v1/matcher/match")
def match_candidate(req: MatchRequest):
    score, matched, missing = calculate_skill_match(req.student_skills, req.required_skills)
    explanation = generate_grounded_explanation(
        req.student_name,
        req.job_title,
        matched,
        missing,
        score
    )

    return {
        "status": "success",
        "student_id": req.student_id,
        "job_id": req.job_id,
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_explanation": explanation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8007, reload=True)
