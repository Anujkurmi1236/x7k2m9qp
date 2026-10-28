## Run the API

From this directory, install the locked dependencies and start the FastAPI
application with:

```bash
uv sync
uv run python run_api.py
```

The API listens on `http://127.0.0.1:8000` by default. Configure the runner
with `API_HOST`, `API_PORT`, and `API_RELOAD` environment variables:

```bash
API_HOST=0.0.0.0 API_PORT=8000 API_RELOAD=true uv run python run_api.py
```

The health endpoint is available at `GET /api/health`.