FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and install the open-source English-to-Chinese package at image-build time.
RUN python - <<'PY'
import argostranslate.package
import argostranslate.translate

argostranslate.package.update_package_index()
packages = [
    p for p in argostranslate.package.get_available_packages()
    if p.from_code == "en" and p.to_code == "zh"
]
if not packages:
    raise SystemExit("No Argos Translate en-to-zh package is available")
package = packages[-1]
package_path = argostranslate.package.download_package(package)
argostranslate.package.install_from_path(package_path)
if argostranslate.translate.get_translation_from_codes("en", "zh") is None:
    raise SystemExit("Argos Translate en-to-zh model installation failed")
PY

COPY app.py .
EXPOSE 10000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}"]
