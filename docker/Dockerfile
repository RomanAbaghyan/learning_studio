FROM python:3.12-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8735 ACADEMY_DB=/data/academy.db ACADEMY_DEBUG=0 ACADEMY_CPP=0
WORKDIR /app
RUN groupadd --gid 10001 academy && useradd --uid 10001 --gid academy --no-create-home academy \
    && mkdir /data && chown academy:academy /data
COPY backend/requirements/runtime.lock /tmp/requirements/runtime.lock
RUN pip install --no-cache-dir -r /tmp/requirements/runtime.lock
EXPOSE 8735
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import json, os, urllib.request; assert json.load(urllib.request.urlopen('http://127.0.0.1:' + os.environ['PORT'] + '/api/health', timeout=3))['ok']"
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8735", "--no-proxy-headers"]

FROM node:22-bookworm-slim AS node

FROM base AS development
USER root
RUN apt-get update && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY backend/requirements/dev.lock /tmp/requirements/dev.lock
RUN pip install --no-cache-dir --timeout 120 --retries 5 -r /tmp/requirements/dev.lock
COPY . .
USER academy
ENV ACADEMY_DEBUG=1 ACADEMY_SECURE_COOKIES=0
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8735", "--reload", "--reload-dir", "/app/backend", "--no-proxy-headers"]

FROM base AS production
COPY backend/ backend/
COPY frontend/ frontend/
COPY tools/database.py tools/database.py
USER academy
