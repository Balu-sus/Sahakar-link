from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from service import detect_liveness, verify_face_embedding
import json

app = FastAPI(
    title="Sahakar-Link Biometrics Service",
    description="AdaFace Identity Verification & Liveness Detection Engine",
    version="1.0.0"
)

class VerificationResponse(BaseModel):
    verified: bool
    liveness_passed: bool
    liveness_score: float
    face_matched: bool
    similarity_score: float
    message: str

@app.post("/api/v1/biometrics/verify", response_model=VerificationResponse)
async def verify_attendance(
    student_id: str = Form(...),
    reference_embedding: str = Form(...), # JSON array of 512 floats
    face_image: UploadFile = File(...)
):
    try:
        ref_vec = json.loads(reference_embedding)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid reference embedding JSON format")

    image_bytes = await face_image.read()

    # 1. Anti-spoofing Liveness Check
    is_live, liveness_score = detect_liveness(image_bytes)
    if not is_live:
        return VerificationResponse(
            verified=False,
            liveness_passed=False,
            liveness_score=liveness_score,
            face_matched=False,
            similarity_score=0.0,
            message="Liveness check failed (Spoofing detected). Route to Manual Exception Workflow."
        )

    # 2. Extract AdaFace Embedding & Match
    # Simulated dummy target embedding for current service shell testing
    dummy_target_embedding = ref_vec if len(ref_vec) == 512 else [0.1] * 512
    is_match, similarity_score = verify_face_embedding(dummy_target_embedding, ref_vec)

    is_verified = is_live and is_match

    return VerificationResponse(
        verified=is_verified,
        liveness_passed=is_live,
        liveness_score=liveness_score,
        face_matched=is_match,
        similarity_score=similarity_score,
        message="Biometric verification successful" if is_verified else "Face mismatch. Route to Manual Exception Workflow."
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
