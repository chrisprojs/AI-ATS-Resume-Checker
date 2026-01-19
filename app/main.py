from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import get_settings

from app.controllers.resume_controller import router as resume_router


app = FastAPI(title="PDF Resume Summarizer & News Search", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok", "app": get_settings().app_name}

app.include_router(resume_router)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):  # noqa: ANN001
    # Generic fallback to avoid leaking stack traces
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

# Entry point for `uvicorn app.main:app --reload`
def get_app() -> FastAPI:
    return app

