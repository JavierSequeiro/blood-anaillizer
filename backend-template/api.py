"""
Blood Test Analysis API - Integrated with Existing Backend

This FastAPI backend integrates your existing PDF processing pipeline with the frontend.
It uses your custom classes: PDFReaderNam, DFAnalyzer, MedPrompter, and LLMReportGenerator.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import pandas as pd
import tempfile
import os
import logging
from pathlib import Path

# Import your existing classes
# Make sure these imports match your actual file structure
from utils.our_pdf_reader import PDFReaderNam
from utils.df_analyzer import DFAnalyzer
from utils.prompter import MedPrompter
from utils.LLMReportGeneratoy import LLMReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blood Test Analysis API")

origins = ["https://blood-anaillizer.netlify.app/",
           "https://localhost:3000"]
        #    "*"] # "https://localhost:3000", local
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API validation
class ReferenceRange(BaseModel):
    min: float
    max: float

# class Biomarker(BaseModel):
#     name: str
#     value: float
#     unit: str
#     referenceRange: ReferenceRange

class Biomarker(BaseModel):
    id: str
    name: str
    value: float
    unit: str
    referenceRange: ReferenceRange
    category: str

class AnalysisResponse(BaseModel):
    biomarkers: List[Biomarker]
    report: str
    fileName: str

class RegenerateReportRequest(BaseModel):
    biomarkers: List[Biomarker]
    language: Optional[str] = "en"
    user_type: Optional[str] = "Patient"

class PDFRequest(BaseModel):
    report: str
    # language: Optional[str] = "en"
    # user_type: Optional[str] = "patient"

class GeneratedReport(BaseModel):
    # pdf_blob: Union[bytearray, bytes]
    pdf_blob: Optional[bytes]

def dataframe_to_biomarkers(df: pd.DataFrame) -> List[Dict]:
    """
    Convert your dataframe format to the frontend biomarker format
    
    Expected dataframe columns (adjust based on your actual DFAnalyzer output):
    - Test name column (e.g., 'Test', 'Biomarker', 'Parameter')
    - Value column (e.g., 'Value', 'Result')
    - Unit column (e.g., 'Unit')
    - Reference range columns (e.g., 'Ref Low', 'Ref High' or 'Lower Bound', 'Upper Bound')
    
    Modify this function based on your actual dataframe structure
    """
    biomarkers = []
    
    # # Adjust these column names to match your actual dataframe structure
    # # Common variations in your code might be:
    # # Test name: 'Test', 'Biomarker', 'Parameter', 'Variable'
    # # Value: 'Value', 'Result', 'Measured Value'
    # # Unit: 'Unit', 'Units'
    # # Range: 'Ref Low'/'Ref High', 'Lower Bound'/'Upper Bound', 'Min'/'Max'
    
    # for _, row in df.iterrows():
    #     try:
    #         # Try to extract biomarker data
    #         # Adjust these column names based on your DFAnalyzer output
    #         biomarker = {
    #             "name": str(row.get('Test', row.get('Biomarker', row.get('Parameter', '')))),
    #             "value": float(row.get('Value', row.get('Result', 0))),
    #             "unit": str(row.get('Unit', row.get('Units', ''))),
    #             "referenceRange": {
    #                 "min": float(row.get('Ref Low', row.get('Lower Bound', row.get('Min', 0)))),
    #                 "max": float(row.get('Ref High', row.get('Upper Bound', row.get('Max', 0))))
    #             }
    #         }
            
    #         # Only add if we have valid data
    #         if biomarker["name"] and biomarker["value"] is not None:
    #             biomarkers.append(biomarker)
    #     except (KeyError, ValueError, TypeError) as e:
    #         # Skip rows with missing or invalid data
    #         logger.warning(f"Skipping row due to error: {e}")
    #         continue
    # data, biomarkers_dict, biomarkers_df = PDFReaderNam()
    return biomarkers

def process_pdf_file(file_path: str) -> pd.DataFrame:
    """
    Process PDF file using your PDFReaderNam class
    
    Returns: DataFrame with blood test data
    """
    try:
        logger.info(f"Starting PDF Reading for {file_path}...")
        
        # Use your PDFReaderNam class
        pdf_reader = PDFReaderNam(pdf_path=file_path)
        data, biomarkers, data_df = pdf_reader.analyze_pdf(to_df=True)
        
        logger.info("Finished PDF Reading!")
        
        return data_df, biomarkers
    
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing PDF file: {str(e)}")

def analyze_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze dataframe using your DFAnalyzer class
    
    Returns: Decorated/analyzed DataFrame
    """
    try:
        logger.info("Starting DF Analysis...")
        
        # Use your DFAnalyzer class
        analyzer = DFAnalyzer(data_df=df)
        
        # You can optionally save the colored Excel file
        # For now, we'll just return the analyzed dataframe
        df_analyzed = analyzer.get_colored_xlsx(save_xlsx=False)
        
        logger.info("Finished DF Analysis!")
        
        return df if df_analyzed is None else df_analyzed
    
    except Exception as e:
        logger.error(f"Error analyzing dataframe: {str(e)}")
        # Return original dataframe if analysis fails
        return df

def generate_report_from_df(df: pd.DataFrame, language: str = "en", user_type: str = "Patient") -> str:
    """
    Generate LLM report using your MedPrompter and LLMReportGenerator classes
    
    Args:
        df: DataFrame with blood test data
        language: Language for the report (e.g., "en", "es")
        user_type: Type of user (e.g., "Patient", "Doctor")
    
    Returns: Generated report text
    """
    try:
        logger.info("Starting Report Generation...")
        
        # Step 1: Create prompt using MedPrompter
        logger.info("Creating prompt with MedPrompter...")
        prompter = MedPrompter(data_df=df, language=language)
        report_prompt = prompter.extract_info()
        
        logger.info(f"Generated prompt: {report_prompt[:100]}...")
        
        # Step 2: Generate report using LLMReportGenerator
        logger.info("Generating LLM report...")
        llm_generator = LLMReportGenerator(
            prompt=report_prompt,
            user_type=user_type,
            language=language
        )
        llm_report = llm_generator.generate_report()
        
        logger.info("Finished Report Generation!")
        
        return llm_report
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        # Return a fallback message if report generation fails
        return f"# Blood Test Analysis Report\n\nError generating detailed report: {str(e)}\n\nPlease review the biomarker values in the table."

# API Endpoints

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Blood Test Analysis API is running",
        "version": "2.0 - Integrated Backend"
    }

@app.post("/api/analyze-blood-test", response_model=AnalysisResponse)
async def analyze_blood_test(
    file: UploadFile = File(...),
    language: str = "en",
    user_type: str = "Patient"
):
    """
    Main endpoint to analyze blood test PDF file
    
    Workflow:
    1. Receive PDF file
    2. Extract data using PDFReaderNam
    3. Analyze data using DFAnalyzer
    4. Generate prompt using MedPrompter
    5. Generate report using LLMReportGenerator
    6. Return biomarkers and report
    
    Args:
        file: PDF file with blood test results
        language: Language for the report (default: "en")
        user_type: User type for report customization (default: "Patient")
    
    Returns: Biomarkers list and LLM-generated report
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a PDF blood test report."
        )
    
    # Create temporary file to store the uploaded PDF
    temp_dir = tempfile.mkdtemp()
    temp_pdf_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        logger.info(f"Receiving file: {file.filename}")
        with open(temp_pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Step 1: Process PDF to extract data
        data_df, biomarkers = process_pdf_file(temp_pdf_path)
        print(biomarkers)
        
        if data_df is None or data_df.empty:
            raise HTTPException(
                status_code=400,
                detail="No data could be extracted from the PDF file"
            )
        
        # Step 2: Analyze dataframe
        # analyzed_df = analyze_dataframe(data_df)
        
        # Step 3: Convert to biomarkers format
        # biomarkers = dataframe_to_biomarkers(analyzed_df)
        
        if not biomarkers:
            raise HTTPException(
                status_code=400,
                detail="No valid biomarkers found in the file"
            )
        
        # Step 4: Generate LLM report
        report = generate_report_from_df(data_df, language=language, user_type=user_type)
        
        logger.info(f"Successfully processed {file.filename} - {len(biomarkers)} biomarkers found")
        
        return AnalysisResponse(
            biomarkers=biomarkers,
            report=report,
            fileName=file.filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing blood test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing blood test: {str(e)}"
        )
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {str(e)}")

@app.post("/api/generate-pdf")
# @app.post("/api/generate-pdf") #, response_model=GeneratedReport)
async def generate_pdf(
    request: PDFRequest,
):
    """
    Main endpoint to analyze blood test PDF file
    
    Workflow:
    1. Receive PDF file
    2. Extract data using PDFReaderNam
    3. Analyze data using DFAnalyzer
    4. Generate prompt using MedPrompter
    5. Generate report using LLMReportGenerator
    6. Return biomarkers and report
    
    Args:
        file: PDF file with blood test results
        language: Language for the report (default: "en")
        user_type: User type for report customization (default: "Patient")
    
    Returns: Biomarkers list and LLM-generated report
    """
    
    try:
        # print(request)
        report = request.report
        logger.info(f"ACCESSED FUNCTION")
        print(f"REPORT")
        print(report)
        # Save uploaded file
        # logger.info(f"Receiving file: {file.filename}")
        # with open(temp_pdf_path, "wb") as f:
        #     content = await file.read()
        #     f.write(content)
        
        # # Step 1: Process PDF to extract data
        # data_df, biomarkers = process_pdf_file(temp_pdf_path)
        
        # if data_df is None or data_df.empty:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="No data could be extracted from the PDF file"
        #     )
        
        # # Step 2: Analyze dataframe
        # # analyzed_df = analyze_dataframe(data_df)
        
        # # Step 3: Convert to biomarkers format
        # # biomarkers = dataframe_to_biomarkers(analyzed_df)
        
        # if not biomarkers:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="No valid biomarkers found in the file"
        #     )
        
        # # Step 4: Generate LLM report
        # report = generate_report_from_df(data_df, language=language, user_type=user_type)
        
        # logger.info(f"Successfully processed {file.filename} - {len(biomarkers)} biomarkers found")
        pdf_response_bytes = LLMReportGenerator(prompt="", user_type="patient", language="en").generate_pdf(response=report)
        logger.info(f"GENERATED PDF")
        # print(pdf_response_str)
        print(type(pdf_response_bytes))
        # return GeneratedReport(pdf_blob=pdf_response_str)
        print("Resp Before")
        resp = Response(
        content=pdf_response_bytes,
        media_type="application/pdf",
        headers={
            # This header tells the browser to download the file
            # with a specific name.
            "Content-Disposition": "attachment; filename=generated_report.pdf"})
        print("Resp After")
        return resp
        
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing blood test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing blood test: {str(e)}"
        )

@app.post("/api/regenerate-report")
async def regenerate_report(request: RegenerateReportRequest):
    """
    Regenerate report for existing biomarkers
    
    This endpoint recreates the dataframe from biomarkers and regenerates the report.
    Useful when user wants a new analysis without re-uploading the file.
    
    Args:
        request: Contains biomarkers list, language, and user_type
    
    Returns: Newly generated report
    """
    try:
        # Convert biomarkers back to dataframe format
        df_data = []
        for biomarker in request.biomarkers:
            df_data.append({
                'Test': biomarker.name,
                'Value': biomarker.value,
                'Unit': biomarker.unit,
                'Ref Low': biomarker.referenceRange.min,
                'Ref High': biomarker.referenceRange.max
            })
        
        df = pd.DataFrame(df_data)
        
        # Generate new report
        report = generate_report_from_df(
            df,
            language=request.language,
            user_type=request.user_type
        )
        
        return {"report": report}
    
    except Exception as e:
        logger.error(f"Error regenerating report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error regenerating report: {str(e)}"
        )

@app.get("/api/supported-formats")
def supported_formats():
    """Return list of supported file formats"""
    return {
        "formats": [".pdf"],
        "note": "Currently only PDF blood test reports are supported",
        "workflow": [
            "1. Upload PDF file",
            "2. PDFReaderNam extracts data",
            "3. DFAnalyzer analyzes values",
            "4. MedPrompter creates prompt",
            "5. LLMReportGenerator creates report"
        ]
    }

@app.get("/api/supported-languages")
def supported_languages():
    """Return list of supported languages"""
    return {
        "languages": ["en", "es"],
        "default": "en",
        "note": "Language applies to the LLM-generated report"
    }

if __name__ == "__main__":
    import uvicorn
    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8000)
