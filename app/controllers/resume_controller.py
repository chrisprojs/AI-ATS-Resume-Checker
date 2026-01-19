from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.schemas.resume_schema import ResumeCheckerRequest, ResumeCheckerResponse
from app.services.resume_service import ResumeServiceError, ResumeService
from app.helpers.pdf_extractor_helper import PdfExtractionError, extract_text_from_pdf

router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
    responses={404: {"description": "Not found"}}
)

@router.post("/check", response_model=ResumeCheckerResponse)
async def resume_checker(req: ResumeCheckerRequest = Depends()):
    if req.resume_file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    try:
        file_bytes = await req.resume_file.read()
        extracted_resume_text = extract_text_from_pdf(file_bytes)
    except PdfExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        service = ResumeService()
        summary = await service.analyze_resume(extracted_resume_text, req.job_post)
    except ResumeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ResumeCheckerResponse(summary=summary)