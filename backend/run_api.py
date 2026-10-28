import os
from pathlib import Path

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        app_dir=str(Path(__file__).resolve().parent),
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", os.getenv("API_PORT", "8000"))),
        reload=os.getenv("API_RELOAD", "").lower() in {"1", "true", "yes"},
    )
