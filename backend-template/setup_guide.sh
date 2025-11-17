#!/bin/bash

# Blood Test Analysis Backend - Setup Guide
# This script helps you set up the Python backend

echo "=========================================="
echo "Blood Test Analysis Backend Setup"
echo "=========================================="
echo ""

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

python_version=$(python3 --version)
echo "✅ Found: $python_version"
echo ""

# Check if we're in the right directory
if [ ! -f "api.py" ]; then
    echo "❌ Error: api.py not found. Please run this script from the backend-template directory."
    exit 1
fi

# Check if utils folder exists
echo "Checking for utils folder..."
if [ ! -d "utils" ]; then
    echo "❌ utils folder not found!"
    echo ""
    echo "ACTION REQUIRED:"
    echo "1. Copy your existing utils folder to this directory:"
    echo "   cp -r /path/to/your/utils ./utils"
    echo ""
    echo "2. Make sure it contains:"
    echo "   - our_pdf_reader.py (with PDFReaderNam class)"
    echo "   - df_analyzer.py (with DFAnalyzer class)"
    echo "   - prompter.py (with MedPrompter class)"
    echo "   - LLMReportGenerator.py (with LLMReportGenerator class)"
    echo ""
    exit 1
else
    echo "✅ utils folder found"
    
    # Check for required files
    required_files=("our_pdf_reader.py" "df_analyzer.py" "prompter.py" "LLMReportGenerator.py")
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ -f "utils/$file" ]; then
            echo "   ✅ utils/$file"
        else
            echo "   ❌ utils/$file (MISSING)"
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  WARNING: Some required files are missing in utils folder"
        echo "   Missing: ${missing_files[*]}"
        echo "   The API may not work correctly without these files."
        echo ""
    fi
fi
echo ""

# Create virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup .env file
echo "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "⚠️  ACTION REQUIRED:"
    echo "   Edit .env file and add your LLM API key:"
    echo "   nano .env"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Final instructions
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. If you haven't already, edit .env and add your API keys:"
echo "   nano .env"
echo ""
echo "2. Test your dataframe structure (IMPORTANT):"
echo "   python test_dataframe_structure.py"
echo ""
echo "3. Update api.py with your column names based on step 2"
echo "   See CONFIGURATION_GUIDE.md for details"
echo ""
echo "4. Start the server:"
echo "   uvicorn api:app --reload --port 8000"
echo ""
echo "5. Test the API:"
echo "   curl http://localhost:8000/"
echo ""
echo "6. Upload a test PDF:"
echo "   curl -X POST http://localhost:8000/api/analyze-blood-test \\"
echo "        -F 'file=@your_test.pdf'"
echo ""
echo "For detailed documentation, see README.md"
echo ""
