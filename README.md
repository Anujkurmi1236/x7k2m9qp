# Wind Forecast vs Actual

A full-stack application for comparing GB wind-generation forecasts with
actual generation. The backend is a FastAPI service backed by Parquet data,
and the frontend is a React/Vite dashboard with forecast, error, and accuracy
charts.

## Project structure

```text
backend/
  app.py              FastAPI routes and forecast calculations
  run_api.py          Uvicorn runner
  data/               Actual and forecast Parquet files
  scripts.py          BMRS data-fetching helpers
frontend/
  src/                React dashboard and API client
  Dockerfile          Production frontend image
docker-compose.yml    Backend and frontend services
```

## Run with Docker Compose

Build and start both services from the repository root:

```bash
docker compose up --build
```

Open the dashboard at <http://localhost:5173>.

The backend is available at <http://localhost:8000>, and its health endpoint
is:

```text
http://localhost:8000/api/health
```

Stop the services with:

```bash
docker compose down
```

The frontend image is built with
`VITE_FASTAPI_BASE_URL=http://localhost:8000`, which is the URL the browser
uses to reach the published backend port.

## Deploy on Render with Docker

Deploy the backend and frontend as two separate Render Web Services. Render
does not deploy both Compose services as a single service.

### Backend Web Service

Create a Docker Web Service with:

- **Root Directory:** `backend`
- **Dockerfile Path:** `Dockerfile`
- **Docker Command:** leave blank to use the Dockerfile `CMD`
- **Region:** Singapore

The backend image uses Render's `PORT` environment variable and listens on
`0.0.0.0`. After deployment, check:

```text
https://<backend-service>.onrender.com/api/health
```

### Frontend Web Service

Create a second Docker Web Service with:

- **Root Directory:** `frontend`
- **Dockerfile Path:** `Dockerfile`
- **Docker Command:** leave blank to use the Dockerfile `CMD`
- **Region:** Singapore

Add this Docker build argument in the frontend service:

```text
VITE_FASTAPI_BASE_URL=https://<backend-service>.onrender.com
```

Vite embeds this value during the image build, so it must be the public
backend URL and must be set before each frontend build. Do not use
`http://localhost:8000` in the Render frontend service.

## Run the backend locally

The backend requires Python 3.13 or newer and uses `uv` for dependency
management:

```bash
cd backend
uv sync
uv run python run_api.py
```

The API listens on `http://127.0.0.1:8000` by default. Configure the runner
with environment variables:

```bash
API_HOST=0.0.0.0 API_PORT=8000 API_RELOAD=true uv run python run_api.py
```

## Run the frontend locally

```bash
cd frontend
pnpm install
pnpm run dev
```

The Vite development server runs at <http://localhost:5173>. Configure the
backend URL in `frontend/.env`:

```env
VITE_FASTAPI_BASE_URL=http://127.0.0.1:8000
```

Use `frontend/.env.example` as a starting point. Vite exposes only variables
prefixed with `VITE_` to browser code.

## API endpoints

### `GET /api/health`

Returns the service health status:

```json
{"ok": true}
```

### `GET /api/forecast`

Returns the forecast selected at the requested cutoff alongside actual
generation:

```text
/api/forecast?date=2026-01-15&cutoff=09:00
```

### `GET /api/accuracy`

Returns accuracy metrics over a date range:

```text
/api/accuracy?date_from=2026-01-01&date_to=2026-01-31&cutoff=09:00
```

## Validation

Run the backend tests:

```bash
cd backend
uv run python -m unittest test_app.py
```

Build the frontend:

```bash
cd frontend
pnpm run build
```