FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY constraints.txt ./constraints.txt
COPY unison-common /app/unison-common
COPY unison-intent-graph/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -c ./constraints.txt /app/unison-common \
    && pip install --no-cache-dir -c ./constraints.txt -r requirements.txt

COPY unison-intent-graph/src/ ./src/
COPY unison-intent-graph/tests/ ./tests/

ENV PYTHONPATH=/app/src
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
