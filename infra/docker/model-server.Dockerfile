FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY model_server/pyproject.toml* ./
RUN uv sync --frozen --no-dev 2>/dev/null || pip install fastapi uvicorn mlflow boto3

COPY model_server/src ./src

ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/src"

EXPOSE 8001

CMD ["uvicorn", "model_server.main:app", "--host", "0.0.0.0", "--port", "8001"]
