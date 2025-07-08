import os
import json
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from services.file_processor import FileProcessor
from services.openai_service import OpenAIService
from services.metadata_service import MetadataService
from models.question_model import QuestionData, QuestionQuality, MetadataTag

app = FastAPI(title="Question Paper Generator", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
file_processor = FileProcessor()
openai_service = OpenAIService()
metadata_service = MetadataService()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/process-file")
async def process_file(
    file: UploadFile = File(...),
    output_folder: str = Form(...),
    include_quality_check: bool = Form(True),
    metadata_tags: str = Form("[]")
):
    """
    Process uploaded file to extract questions and analyze quality
    """
    try:
        # Validate output folder
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder, exist_ok=True)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Cannot create output folder: {str(e)}")
        
        # Parse metadata tags
        try:
            tags = json.loads(metadata_tags)
        except json.JSONDecodeError:
            tags = []
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text content based on file type
            extracted_text = await file_processor.extract_text(tmp_file_path, file.filename)
            
            # Extract questions using OpenAI
            questions = await openai_service.extract_questions(extracted_text, file.filename)
            
            # Analyze question quality if requested
            quality_results = []
            if include_quality_check:
                for question in questions:
                    quality = await openai_service.analyze_question_quality(question)
                    quality_results.append(quality)
            
            # Generate metadata
            metadata = metadata_service.generate_metadata(
                filename=file.filename,
                questions=questions,
                quality_results=quality_results,
                custom_tags=tags
            )
            
            # Save results to output folder
            output_file = await save_results(
                output_folder, 
                file.filename, 
                questions, 
                quality_results, 
                metadata
            )
            
            return JSONResponse({
                "success": True,
                "message": "File processed successfully",
                "results": {
                    "extracted_questions": len(questions),
                    "quality_analyzed": len(quality_results),
                    "output_file": output_file,
                    "questions": questions[:5],  # Preview first 5 questions
                    "metadata": metadata
                }
            })
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/analyze-quality")
async def analyze_quality(question: str):
    """
    Analyze the quality of a single question
    """
    try:
        quality = await openai_service.analyze_question_quality(question)
        return JSONResponse({
            "success": True,
            "quality": quality
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality analysis error: {str(e)}")

@app.get("/api/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats
    """
    return JSONResponse({
        "formats": [
            {"extension": "pdf", "description": "PDF Documents"},
            {"extension": "docx", "description": "Microsoft Word Documents"},
            {"extension": "xlsx", "description": "Microsoft Excel Spreadsheets"},
            {"extension": "jpg", "description": "JPEG Images"},
            {"extension": "png", "description": "PNG Images"},
            {"extension": "tiff", "description": "TIFF Images"}
        ]
    })

async def save_results(output_folder: str, filename: str, questions: List[str], 
                      quality_results: List[Dict], metadata: Dict) -> str:
    """
    Save processing results to the specified output folder
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(filename).stem
    output_file = os.path.join(output_folder, f"{base_name}_processed_{timestamp}.json")
    
    results = {
        "source_file": filename,
        "processed_at": datetime.now().isoformat(),
        "metadata": metadata,
        "questions": []
    }
    
    for i, question in enumerate(questions):
        question_data = {
            "id": i + 1,
            "text": question,
            "quality": quality_results[i] if i < len(quality_results) else None
        }
        results["questions"].append(question_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return output_file

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)