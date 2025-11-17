# Blood Test Analysis Python Backend - Integrated Version

This FastAPI backend integrates your existing PDF processing pipeline with the Blood Test Analysis Platform frontend. It uses your custom classes for end-to-end blood test analysis.

## Architecture

The backend integrates your existing workflow:

```
PDF Upload → PDFReaderNam → DFAnalyzer → MedPrompter → LLMReportGenerator → Frontend
```

### Your Custom Classes Used:
- **PDFReaderNam**: Extracts blood test data from PDF files
- **DFAnalyzer**: Analyzes dataframe and creates colored outputs
- **MedPrompter**: Generates prompts from biomarker data
- **LLMReportGenerator**: Creates medical reports using LLM

## Project Structure

```
backend-template/
├── api.py                    # FastAPI server (THIS FILE)
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
└── utils/                   # Your existing utils folder
    ├── our_pdf_reader.py    # PDFReaderNam class
    ├── df_analyzer.py       # DFAnalyzer class
    ├── prompter.py          # MedPrompter class
    └── LLMReportGenerator.py # LLMReportGenerator class
```

## Setup Instructions

### 1. Copy Your Utils Folder

Copy your existing `utils/` folder into the `backend-template/` directory:

```bash
cd backend-template/
cp -r /path/to/your/utils ./utils
```

Make sure your utils folder contains:
- `our_pdf_reader.py` with `PDFReaderNam` class
- `df_analyzer.py` with `DFAnalyzer` class
- `prompter.py` with `MedPrompter` class
- `LLMReportGenerator.py` with `LLMReportGenerator` class

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Important**: If your utils classes require additional dependencies, add them to `requirements.txt`

### 3. Configure Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your LLM API key and any other required credentials:

```env
LLM_API_KEY=your_actual_api_key_here
OPENAI_API_KEY=sk-...  # If using OpenAI
ANTHROPIC_API_KEY=sk-ant-...  # If using Claude
```

### 4. Adjust Column Mapping

**IMPORTANT**: Update the `dataframe_to_biomarkers()` function in `api.py` to match your actual dataframe column names.

Your `PDFReaderNam` and `DFAnalyzer` output a dataframe. Check what columns it has and update this section in `api.py`:

```python
def dataframe_to_biomarkers(df: pd.DataFrame) -> List[Dict]:
    for _, row in df.iterrows():
        biomarker = {
            # UPDATE THESE to match your actual column names!
            "name": str(row.get('Test', '')),  # Change 'Test' to your column name
            "value": float(row.get('Value', 0)),  # Change 'Value' to your column name
            "unit": str(row.get('Unit', '')),  # Change 'Unit' to your column name
            "referenceRange": {
                "min": float(row.get('Ref Low', 0)),  # Change to your column name
                "max": float(row.get('Ref High', 0))  # Change to your column name
            }
        }
```

### 5. Run the Server

```bash
# Development mode with auto-reload
uvicorn api:app --reload --port 8000

# Or run directly
python api.py
```

The API will be available at `http://localhost:8000`

### 6. Test the Integration

```bash
# Health check
curl http://localhost:8000/

# Upload a blood test PDF
curl -X POST "http://localhost:8000/api/analyze-blood-test" \
     -F "file=@/path/to/Blood_Test_Sample_JS.pdf" \
     -F "language=en" \
     -F "user_type=Patient"
```

## API Endpoints

### `POST /api/analyze-blood-test`

Upload and analyze a blood test PDF file.

**Parameters:**
- `file`: PDF file (required)
- `language`: Report language - "en" or "es" (optional, default: "en")
- `user_type`: User type - "Patient" or "Doctor" (optional, default: "Patient")

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/analyze-blood-test?language=es&user_type=Patient" \
     -F "file=@Blood_Test_Sample_JS.pdf"
```

**Response:**
```json
{
  "biomarkers": [
    {
      "name": "Hemoglobin",
      "value": 14.5,
      "unit": "g/dL",
      "referenceRange": {
        "min": 13.5,
        "max": 17.5
      }
    }
  ],
  "report": "# Blood Test Analysis Report\n\n...",
  "fileName": "Blood_Test_Sample_JS.pdf"
}
```

### `POST /api/regenerate-report`

Regenerate the report for existing biomarkers (useful when user wants report in different language).

**Request Body:**
```json
{
  "biomarkers": [...],
  "language": "es",
  "user_type": "Patient"
}
```

**Response:**
```json
{
  "report": "# Informe de Análisis de Sangre\n\n..."
}
```

### `GET /api/supported-formats`

Get supported file formats and workflow information.

### `GET /api/supported-languages`

Get supported languages for report generation.

## Workflow

1. **User uploads PDF** via frontend
2. **FastAPI receives file** and saves temporarily
3. **PDFReaderNam processes PDF** → extracts text and creates dataframe
4. **DFAnalyzer analyzes dataframe** → identifies normal/abnormal values
5. **MedPrompter creates prompt** → structures biomarker data for LLM
6. **LLMReportGenerator creates report** → sends prompt to LLM, receives medical analysis
7. **API returns** biomarkers array + LLM report to frontend
8. **Frontend displays** color-coded biomarkers and shows report

## Troubleshooting

### Import Errors

If you get import errors like `ModuleNotFoundError: No module named 'utils'`:

1. Make sure your utils folder is in the correct location
2. Check that all your utils files have the correct class names
3. Verify Python can find the modules:
   ```python
   import sys
   print(sys.path)
   ```

### Column Name Mismatch

If biomarkers aren't being extracted correctly:

1. Print your dataframe to see column names:
   ```python
   # In api.py, add after process_pdf_file():
   print("DataFrame columns:", data_df.columns.tolist())
   print("Sample row:", data_df.iloc[0].to_dict())
   ```

2. Update the `dataframe_to_biomarkers()` function with correct column names

### PDF Processing Errors

If PDFs aren't processing:

1. Check the PDF format is compatible with your `PDFReaderNam`
2. Verify easyocr is properly installed
3. Check server logs for detailed error messages
4. Test your `PDFReaderNam` directly in a separate script

### LLM Report Generation Fails

If report generation fails:

1. Verify your LLM API key is correct in `.env`
2. Check your API quota/rate limits
3. Test your `LLMReportGenerator` directly with sample data
4. Review the generated prompt to ensure it's valid

## Language Support

The backend supports both English and Spanish:

- **English** (`language="en"`): Default, medical report in English
- **Spanish** (`language="es"`): Medical report in Spanish

Pass the language parameter when uploading:
```bash
curl -X POST "http://localhost:8000/api/analyze-blood-test?language=es" \
     -F "file=@test.pdf"
```

## Frontend Integration

The frontend is already configured to call this backend. When a user uploads a PDF:

1. File sent to `POST /api/analyze-blood-test`
2. Backend processes with your classes
3. Returns biomarkers + LLM report
4. Results saved to Supabase database
5. User sees color-coded visualization + AI analysis

## Production Deployment

For production:

1. **Update CORS** in `api.py`:
   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```

2. **Secure your API keys** - never commit `.env` to git

3. **Deploy to cloud**:
   - AWS Lambda + API Gateway
   - Google Cloud Run
   - Heroku
   - Digital Ocean App Platform

4. **Update frontend** with production URL in `/utils/pythonApi.ts`:
   ```typescript
   const PYTHON_API_URL = 'https://your-api-domain.com';
   ```

5. **Enable HTTPS** for secure PDF uploads

6. **Add rate limiting** to prevent abuse

## Development Tips

### Testing Your Classes Directly

Before running the full API, test your classes work correctly:

```python
from utils.our_pdf_reader import PDFReaderNam
from utils.df_analyzer import DFAnalyzer
from utils.prompter import MedPrompter
from utils.LLMReportGenerator import LLMReportGenerator

# Test PDF reading
pdf_path = "test.pdf"
reader = PDFReaderNam(pdf_path=pdf_path)
data, data_dict, data_df = reader.analyze_pdf(to_df=True)
print("Columns:", data_df.columns.tolist())

# Test analyzer
analyzer = DFAnalyzer(data_df=data_df)
df_colored = analyzer.get_colored_xlsx(save_xlsx=False)

# Test prompter
prompter = MedPrompter(data_df=data_df, language="en")
prompt = prompter.extract_info()
print("Prompt:", prompt)

# Test LLM generator
generator = LLMReportGenerator(prompt=prompt, user_type="Patient", language="en")
report = generator.generate_report()
print("Report:", report)
```

### Logging

The API includes comprehensive logging. Check logs to debug issues:

```bash
# Logs will show:
# - File upload events
# - PDF processing progress
# - Dataframe extraction
# - Report generation
# - Any errors with full stack traces
```

## Support

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify your utils classes work independently
3. Test with the sample PDF: `Blood_Test_Sample_JS.pdf`
4. Ensure all dependencies are installed
5. Check that column names match between your dataframe and the API

For FastAPI documentation: https://fastapi.tiangolo.com/
