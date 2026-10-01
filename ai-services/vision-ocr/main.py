from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from service import extract_text_from_image, verify_certificate_metadata

app = FastAPI(
    title="Sahakar-Link Vision OCR Service",
    description="PaddleOCR Document Text Extraction and Certificate Validation Engine",
    version="1.0.0"
)

@app.post("/api/v1/ocr/verify-certificate")
async def verify_certificate(
    expected_name: str = Form(...),
    expected_skill: str = Form(...),
    document: UploadFile = File(...)
):
    try:
        image_bytes = await document.read()
        
        # 1. Extract text using OCR pipeline
        extracted_text = extract_text_from_image(image_bytes)
        
        # 2. Verify metadata against extracted text
        verification_results = verify_certificate_metadata(
            extracted_text, 
            expected_name, 
            expected_skill
        )
        
        return {
            "status": "success",
            "extracted_text_preview": extracted_text[:120] + "...",
            "verification": verification_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)
