# Backend Integration Checklist

Use this checklist to ensure your Python backend is properly integrated with the frontend.

## ✅ Pre-Integration Setup

### 1. Copy Your Utilities
- [ ] Copy your `utils/` folder to `backend-template/`
- [ ] Verify `utils/our_pdf_reader.py` exists and contains `PDFReaderNam`
- [ ] Verify `utils/df_analyzer.py` exists and contains `DFAnalyzer`
- [ ] Verify `utils/prompter.py` exists and contains `MedPrompter`
- [ ] Verify `utils/LLMReportGenerator.py` exists and contains `LLMReportGenerator`

### 2. Install Dependencies
```bash
cd backend-template
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

- [ ] Virtual environment created
- [ ] All dependencies installed without errors
- [ ] Add any additional dependencies your utils need to `requirements.txt`

### 3. Configure Environment
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

- [ ] `.env` file created
- [ ] LLM API key added to `.env`
- [ ] Any other required API keys added

## ✅ Configuration

### 4. Identify Your Dataframe Structure
```bash
python test_dataframe_structure.py path/to/sample.pdf
```

- [ ] Test script runs without errors
- [ ] Dataframe columns identified
- [ ] Sample data displayed correctly

Record your column names:
- Test/Biomarker name column: `_________________`
- Value column: `_________________`
- Unit column: `_________________`
- Reference min column: `_________________`
- Reference max column: `_________________`

### 5. Update API Configuration

Edit `api.py` and update the `dataframe_to_biomarkers()` function:

- [ ] Test name column updated
- [ ] Value column updated
- [ ] Unit column updated
- [ ] Reference range min column updated
- [ ] Reference range max column updated

Example:
```python
biomarker = {
    "name": str(row['YOUR_NAME_COLUMN']),  # ← Update this
    "value": float(row['YOUR_VALUE_COLUMN']),  # ← Update this
    "unit": str(row['YOUR_UNIT_COLUMN']),  # ← Update this
    "referenceRange": {
        "min": float(row['YOUR_MIN_COLUMN']),  # ← Update this
        "max": float(row['YOUR_MAX_COLUMN'])  # ← Update this
    }
}
```

### 6. Test Biomarker Conversion
```bash
python test_biomarker_conversion.py
```

- [ ] Conversion script runs without errors
- [ ] Biomarkers extracted correctly
- [ ] JSON output looks correct

Expected output format:
```json
[
  {
    "name": "Hemoglobin",
    "value": 14.5,
    "unit": "g/dL",
    "referenceRange": {
      "min": 13.5,
      "max": 17.5
    }
  }
]
```

## ✅ Testing

### 7. Start the Server
```bash
uvicorn api:app --reload --port 8000
```

- [ ] Server starts without errors
- [ ] Server running on `http://localhost:8000`
- [ ] No import errors in logs

### 8. Test Health Endpoint
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "ok",
  "message": "Blood Test Analysis API is running",
  "version": "2.0 - Integrated Backend"
}
```

- [ ] Health check returns 200 OK
- [ ] Response matches expected format

### 9. Test PDF Upload
```bash
curl -X POST "http://localhost:8000/api/analyze-blood-test" \
     -F "file=@path/to/test.pdf" \
     -F "language=en"
```

- [ ] Upload completes successfully
- [ ] Returns biomarkers array
- [ ] Returns LLM report
- [ ] fileName matches uploaded file

### 10. Check Logs

Look for these log messages:
- [ ] "Starting PDF Reading..."
- [ ] "Finished PDF Reading!"
- [ ] "Starting DF Analysis..."
- [ ] "Finished DF Analysis!"
- [ ] "Starting Report Generation..."
- [ ] "Finished Report Generation!"

## ✅ Frontend Integration

### 11. Verify Frontend Configuration

In `/utils/pythonApi.ts`:
- [ ] `PYTHON_API_URL` is set to `http://localhost:8000`
- [ ] API functions imported in `App.tsx`

### 12. Test Frontend Upload

1. Start frontend (if not already running)
2. Log in to the app
3. Try uploading a PDF blood test file

- [ ] File upload accepts PDF files
- [ ] Upload shows loading state
- [ ] Biomarkers display correctly
- [ ] Color coding works (red/orange/green)
- [ ] LLM report displays
- [ ] Test saved to database

### 13. Test Full Workflow

Complete workflow test:
1. [ ] Sign up new user account
2. [ ] Upload first blood test PDF
3. [ ] View biomarkers in table
4. [ ] View LLM report
5. [ ] Upload second blood test PDF
6. [ ] View "Past Tests" tab
7. [ ] View "Evolution" charts
8. [ ] Regenerate report (if implemented)
9. [ ] Log out
10. [ ] Log back in
11. [ ] Verify tests are still there

## ✅ Error Handling

### 14. Test Error Cases

- [ ] Upload non-PDF file → Should show error
- [ ] Upload corrupted PDF → Should handle gracefully
- [ ] Upload PDF with no data → Should show appropriate message
- [ ] Network error → Should show error message
- [ ] LLM API failure → Should fallback gracefully

## ✅ Production Readiness

### 15. Security

- [ ] `.env` file in `.gitignore`
- [ ] No API keys hardcoded in code
- [ ] CORS configured for production domain
- [ ] Input validation in place

### 16. Performance

- [ ] Large PDFs process in reasonable time (<30 seconds)
- [ ] Temporary files cleaned up after processing
- [ ] Memory usage acceptable

### 17. Documentation

- [ ] README.md reviewed and updated
- [ ] Configuration guide updated with your actual column names
- [ ] Any custom modifications documented

## ✅ Deployment (Optional)

### 18. Deploy Backend

Choose a platform:
- [ ] AWS Lambda
- [ ] Google Cloud Run
- [ ] Heroku
- [ ] Digital Ocean
- [ ] Other: _________________

Deployment steps:
- [ ] Backend deployed
- [ ] Environment variables configured on server
- [ ] HTTPS enabled
- [ ] Production URL obtained

### 19. Update Frontend

In `/utils/pythonApi.ts`:
```typescript
const PYTHON_API_URL = 'https://your-production-api.com';
```

- [ ] Frontend updated with production URL
- [ ] CORS configured on backend for frontend domain
- [ ] End-to-end test from production frontend to production backend

## 🎉 Integration Complete!

Once all checkboxes are marked, your integration is complete!

## Troubleshooting

### Common Issues

**PDFReaderNam import fails:**
- Verify utils folder is in the correct location
- Check Python path includes current directory
- Ensure all dependencies are installed

**Biomarkers not extracting:**
- Run `test_dataframe_structure.py` to verify columns
- Check column names match exactly (case-sensitive)
- Review logs for ValueError or KeyError

**LLM report not generating:**
- Verify LLM API key in `.env`
- Check API quota/limits
- Review LLMReportGenerator logs
- Test LLMReportGenerator independently

**Frontend can't connect:**
- Verify backend is running on port 8000
- Check CORS settings in api.py
- Ensure no firewall blocking requests
- Check browser console for errors

**Files not uploading:**
- Verify file size limits
- Check PDF is not corrupted
- Ensure multipart/form-data support
- Review FastAPI logs

## Support Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pandas Docs**: https://pandas.pydata.org/docs/
- **Your Backend Docs**: See README.md and CONFIGURATION_GUIDE.md

## Notes

Add any custom notes or issues encountered during integration:

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

**Integration Date:** _______________

**Integrated By:** _______________

**Status:** ☐ In Progress  ☐ Complete  ☐ Needs Review
