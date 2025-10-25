import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.services.orchestrator import run_pipeline
from tempfile import TemporaryDirectory
from typing import List

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Auto Math Grader System"}

@router.get("/results/{filename}")
async def get_result_file(filename: str):
    """Serve generated result files"""
    from app.config.settings import STATIC_OUTPUT_DIR
    file_path = os.path.join(STATIC_OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

# Allowed image file types
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadFile, file_type: str) -> None:
    """Validate uploaded file type and size"""
    if not file.filename:
        raise HTTPException(status_code=400, detail=f"{file_type} filename is required")
    
    # Check file extension
    file_ext = os.path.splitext(file.filename.lower())[1]
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"{file_type} must be an image file. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (read first chunk to estimate)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"{file_type} file size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )

@router.post("/analyze")
async def analyze(
    concept_sheet: UploadFile = File(...),
    questions: List[UploadFile] = File(...),
    solutions: List[UploadFile] = File(...),
):
    try:
        # Validate inputs
        if len(questions) == 0 or len(solutions) == 0:
            raise HTTPException(status_code=400, detail="At least one question and solution required")
        if len(questions) != len(solutions):
            raise HTTPException(status_code=400, detail="Number of questions and solutions must match")
        if len(questions) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 question-solution pairs allowed")
        
        # Validate concept sheet
        validate_file(concept_sheet, "Concept sheet")
        
        # Validate all question files
        for i, q in enumerate(questions):
            validate_file(q, f"Question {i+1}")
        
        # Validate all solution files
        for i, s in enumerate(solutions):
            validate_file(s, f"Solution {i+1}")

        with TemporaryDirectory() as tmpdir:
            concept_path = os.path.join(tmpdir, concept_sheet.filename)
            with open(concept_path, "wb") as f:
                shutil.copyfileobj(concept_sheet.file, f)

            q_paths, s_paths = [], []
            for i, q in enumerate(questions):
                qpath = os.path.join(tmpdir, f"question_{i+1}.jpg")
                with open(qpath, "wb") as f:
                    shutil.copyfileobj(q.file, f)
                q_paths.append(qpath)

            for i, s in enumerate(solutions):
                spath = os.path.join(tmpdir, f"solution_{i+1}.jpg")
                with open(spath, "wb") as f:
                    shutil.copyfileobj(s.file, f)
                s_paths.append(spath)

            try:
                result = run_pipeline(concept_path, q_paths, s_paths)
                return {
                    "success": True,
                    "analysis_table_url": result["analysis_table"],
                    "detailed_analysis_url": result["analysis_path"],
                    "message": "Analysis completed successfully"
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error during analysis: {str(e)}"
                )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )
