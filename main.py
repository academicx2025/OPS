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
from services.enhanced_metadata_service import EnhancedMetadataService
from services.image_extractor import ImageExtractor
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
enhanced_metadata_service = EnhancedMetadataService()
image_extractor = ImageExtractor()

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
    extract_images: bool = Form(True),
    metadata_tags: str = Form("[]")
):
    """
    Process uploaded file to extract questions, analyze quality, and extract images
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
            
            # Prepare questions data for enhanced metadata generation
            questions_data = []
            for i, question in enumerate(questions):
                question_data = {
                    "text": question,
                    "quality": quality_results[i] if i < len(quality_results) else {}
                }
                questions_data.append(question_data)
            
            # Extract images if requested
            image_results = {}
            if extract_images:
                # Create image output folder
                image_folder = os.path.join(output_folder, "question_images")
                os.makedirs(image_folder, exist_ok=True)
                
                # Find questions that likely have images
                questions_with_images = [
                    {"question_id": f"Q{i+1:04d}", "text": q["text"]} 
                    for i, q in enumerate(questions_data) 
                    if enhanced_metadata_service._has_image_content(q["text"])
                ]
                
                # Extract images from document
                extracted_images = image_extractor.extract_images_from_document(
                    tmp_file_path, image_folder, questions_with_images
                )
                
                # Process extracted images
                image_results = image_extractor.process_extracted_images(extracted_images)
                
                # Create image manifest
                if extracted_images:
                    manifest_path = image_extractor.create_image_manifest(image_folder, image_results)
            
            # Generate enhanced metadata
            enhanced_results = enhanced_metadata_service.generate_enhanced_metadata(
                questions_data, file.filename, output_folder
            )
            
            return JSONResponse({
                "success": True,
                "message": "File processed successfully with enhanced metadata",
                "results": {
                    "extracted_questions": len(questions),
                    "quality_analyzed": len(quality_results),
                    "images_extracted": image_results.get("total_images", 0) if extract_images else 0,
                    "questions_with_images": image_results.get("questions_with_images", 0) if extract_images else 0,
                    "json_file": enhanced_results["json_file"],
                    "output_folder": output_folder,
                    "preview_questions": [
                        {
                            "question_id": f"Q{i+1:04d}",
                            "text": q["text"][:200] + "..." if len(q["text"]) > 200 else q["text"],
                            "has_image": enhanced_metadata_service._has_image_content(q["text"])
                        }
                        for i, q in enumerate(questions_data[:5])
                    ],
                    "summary": enhanced_results["output_summary"]["metadata"],
                    "image_details": image_results if extract_images else None
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



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)