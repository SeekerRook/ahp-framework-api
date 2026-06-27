FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py main.py

# DB connection strings — override at runtime via -e or docker-compose env
ENV DATA_URL=http://localhost:8132/
ENV AHP_URL=http://localhost:8888/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level","debug"]