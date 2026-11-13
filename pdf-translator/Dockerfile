FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Convert the dedicated English-to-Chinese OPUS-MT model to an int8
# CTranslate2 model during image build; the running service uses CPU.
RUN ct2-transformers-converter \
    --model Helsinki-NLP/opus-mt-en-zh \
    --output_dir /app/opus-mt-en-zh \
    --quantization int8 \
    --force

RUN python - <<'PY'
from transformers import AutoTokenizer
AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-zh").save_pretrained("/app/tokenizer")
PY

COPY app.py .
EXPOSE 10000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}"]
