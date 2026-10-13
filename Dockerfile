FROM node:22-bookworm-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements-lock.txt /app/requirements-lock.txt
RUN pip install --no-cache-dir -r requirements-lock.txt
COPY backend/ /app/backend/
COPY --from=frontend /build/dist /app/frontend/dist
RUN useradd --create-home appuser && mkdir -p /app/data && chown -R appuser:appuser /app
USER appuser
WORKDIR /app/backend
ENV DATABASE_URL=sqlite:////app/data/scamshield.db
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
