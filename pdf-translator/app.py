import os
import threading
from contextlib import asynccontextmanager
from typing import Literal

import ctranslate2
from transformers import AutoTokenizer
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from opencc import OpenCC

MODEL_ID = "Helsinki-NLP/opus-mt-en-zh"
MODEL_DIR = "/app/opus-mt-en-zh"
TOKENIZER_DIR = "/app/tokenizer"
MODEL_READY = False
MODEL_ERROR = None
TRANSLATION_LOCK = threading.Lock()
translator = None
tokenizer = None
traditional_converter = OpenCC("s2t")


def ensure_translation_model():
    global MODEL_READY, MODEL_ERROR, translator, tokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True)
        translator = ctranslate2.Translator(
            MODEL_DIR,
            device="cpu",
            compute_type="int8",
        )
        MODEL_READY = True
        MODEL_ERROR = None
    except Exception as exc:
        MODEL_READY = False
        MODEL_ERROR = str(exc)
        raise


def translate_in_chunks(text: str) -> str:
    # OPUS-MT has a relatively short input window. Split by model tokens
    # instead of truncating long PDF paragraphs.
    token_ids = tokenizer.encode(text, add_special_tokens=True)
    eos_id = tokenizer.eos_token_id
    chunks = []
    start = 0
    while start < len(token_ids):
        end = min(start + 220, len(token_ids))
        chunk_ids = token_ids[start:end]
        if eos_id is not None and chunk_ids[-1] != eos_id:
            chunk_ids = chunk_ids + [eos_id]
        chunks.append(tokenizer.convert_ids_to_tokens(chunk_ids))
        start = end

    translated_parts = []
    for source_tokens in chunks:
        result = translator.translate_batch(
            [source_tokens],
            beam_size=4,
            max_decoding_length=256,
        )
        output_tokens = result[0].hypotheses[0]
        output_ids = tokenizer.convert_tokens_to_ids(output_tokens)
        translated_parts.append(
            tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        )
    return "".join(translated_parts)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ensure_translation_model()
    except Exception:
        # Keep /health available so deployment problems are diagnosable.
        pass
    yield


app = FastAPI(title="PDF Free Translator API", version="0.2.0", lifespan=lifespan)

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
        "engine": "OPUS-MT en-zh (CTranslate2 int8)",
        "model": MODEL_ID,
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
            result = translate_in_chunks(request.text)
        if request.target_language == "zh-TW":
            result = traditional_converter.convert(result)
        return {
            "translation": result,
            "engine": "OPUS-MT en-zh (CTranslate2 int8)",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Translation failed: {exc}") from exc
