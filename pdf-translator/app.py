import os
import threading
from contextlib import asynccontextmanager
from typing import Literal

import argostranslate.translate
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None

MODEL_READY = False
MODEL_ERROR = None
TRANSLATION_LOCK = threading.Lock()


def ensure_translation_model():
    global MODEL_READY, MODEL_ERROR
    try:
        if argostranslate.translate.get_translation_from_codes("en", "zh") is None:
            raise RuntimeError("English-to-Chinese model is not present in the container image")
        MODEL_READY = True
        MODEL_ERROR = None
    except Exception as exc:
        MODEL_READY = False
        MODEL_ERROR = str(exc)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ensure_translation_model()
    except Exception:
        # Keep the API alive so /health can report a useful setup error.
        pass
    yield


app = FastAPI(title="PDF Translator API", version="0.1.0", lifespan=lifespan)

origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://yueguov1989.github.io,http://localhost:8000,http://127.0.0.1:8000",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in origins.split(",") if item.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class TranslateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=24000)
    target_language: Literal["zh-TW", "zh-CN"] = "zh-TW"


@app.get("/health")
def health():
    return {
        "status": "ok" if MODEL_READY else "starting",
        "model_ready": MODEL_READY,
        "engine": "Argos Translate",
        "error": MODEL_ERROR,
    }


@app.post("/api/translate")
def translate(request: TranslateRequest):
    if not MODEL_READY:
        raise HTTPException(
            status_code=503,
            detail="Translation model is not ready. Check /health for setup details.",
        )
    try:
        with TRANSLATION_LOCK:
            result = argostranslate.translate.translate(request.text, "en", "zh")
        if request.target_language == "zh-TW":
            if OpenCC is None:
                raise RuntimeError("OpenCC is not installed")
            result = OpenCC("s2t").convert(result)
        return {"translation": result, "engine": "Argos Translate"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Translation failed: {exc}") from exc
