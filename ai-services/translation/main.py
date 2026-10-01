from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service import translate_text, SUPPORTED_LANGUAGES

app = FastAPI(
    title="Sahakar-Link IndicTrans2 Service",
    description="Multi-Indian Language Translation Adapter",
    version="1.0.0"
)

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "hi"

@app.get("/api/v1/languages")
def get_supported_languages():
    return {"supported_languages": list(SUPPORTED_LANGUAGES.keys())}

@app.post("/api/v1/translate")
async def translate(request: TranslationRequest):
    if request.source_lang not in SUPPORTED_LANGUAGES or request.target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language code")
        
    result = await translate_text(request.text, request.source_lang, request.target_lang)
    return {
        "status": "success",
        "source_lang": request.source_lang,
        "target_lang": request.target_lang,
        "original_text": request.text,
        "translated_text": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
