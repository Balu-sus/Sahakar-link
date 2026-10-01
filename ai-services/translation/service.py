import os
import httpx

# IndicTrans2 supported major language codes mapping
SUPPORTED_LANGUAGES = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "te": "tel_Telu",
    "ta": "tam_Taml",
    "kn": "kan_Knda",
    "mr": "mar_Deva",
    "bn": "ben_Beng",
    "gu": "guj_Gujr"
}

INDICTRANS2_ENDPOINT = os.getenv("INDICTRANS2_ENDPOINT", "http://localhost:8003/v1/translate")

async def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translates text between Indian languages using IndicTrans2 service."""
    if source_lang == target_lang:
        return text
        
    src_code = SUPPORTED_LANGUAGES.get(source_lang, "eng_Latn")
    tgt_code = SUPPORTED_LANGUAGES.get(target_lang, "hin_Deva")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                INDICTRANS2_ENDPOINT,
                json={
                    "text": text,
                    "source_language": src_code,
                    "target_language": tgt_code
                },
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json().get("translated_text", text)
        except Exception:
            # Local fallback simulator during development phase
            return f"[{target_lang.upper()} Translated]: {text}"
    return text
