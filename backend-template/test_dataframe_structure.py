#!/usr/bin/env python3
"""
Test script to identify your dataframe structure

This script helps you understand what columns your PDFReaderNam 
and DFAnalyzer output, so you can configure api.py correctly.

Usage:
    python test_dataframe_structure.py path/to/your/test.pdf
"""

import sys
import os

try:
    from utils.our_pdf_reader import PDFReaderNam
    from utils.df_analyzer import DFAnalyzer
except ImportError as e:
    print("=" * 60)
    print("ERROR: Could not import required modules")
    print("=" * 60)
    print(f"Error: {e}")
    print()
    print("Make sure:")
    print("1. You have copied your utils folder to this directory")
    print("2. All required files exist in utils/:")
    print("   - our_pdf_reader.py")
    print("   - df_analyzer.py")
    print("   - prompter.py")
    print("   - LLMReportGenerator.py")
    print()
    sys.exit(1)

def test_pdf_processing(pdf_path: str):
    """Test PDF processing and display dataframe structure"""
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    print("=" * 60)
    print(f"Testing PDF: {pdf_path}")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Read PDF
        print("Step 1: Reading PDF with PDFReaderNam...")
        reader = PDFReaderNam(pdf_path=pdf_path)
        data, data_dict, data_df = reader.analyze_pdf(to_df=True)
        print("✅ PDF reading successful")
        print()
        
        # Step 2: Display dataframe info
        print("=" * 60)
        print("DATAFRAME INFORMATION")
        print("=" * 60)
        print(f"Shape: {data_df.shape[0]} rows × {data_df.shape[1]} columns")
        print()
        
        # Display columns
        print("Columns:")
        for i, col in enumerate(data_df.columns, 1):
            print(f"  {i}. '{col}'")
        print()
        
        # Display sample data
        print("=" * 60)
        print("FIRST ROW (as dictionary):")
        print("=" * 60)
        if len(data_df) > 0:
            first_row = data_df.iloc[0].to_dict()
            for key, value in first_row.items():
                print(f"  '{key}': {repr(value)}")
        else:
            print("  (No data)")
        print()
        
        # Display first 3 rows
        print("=" * 60)
        print("FIRST 3 ROWS:")
        print("=" * 60)
        print(data_df.head(3).to_string())
        print()
        
        # Step 3: Test DFAnalyzer (optional)
        try:
            print("=" * 60)
            print("Step 2: Testing DFAnalyzer...")
            print("=" * 60)
            analyzer = DFAnalyzer(data_df=data_df)
            df_analyzed = analyzer.get_colored_xlsx(save_xlsx=False)
            print("✅ DFAnalyzer processing successful")
            
            if df_analyzed is not None:
                print()
                print("Analyzed dataframe columns:")
                for i, col in enumerate(df_analyzed.columns, 1):
                    print(f"  {i}. '{col}'")
            print()
        except Exception as e:
            print(f"⚠️  DFAnalyzer test failed: {e}")
            print("   (This is optional - you can still use the raw dataframe)")
            print()
        
        # Step 4: Configuration instructions
        print("=" * 60)
        print("CONFIGURATION INSTRUCTIONS")
        print("=" * 60)
        print()
        print("Based on the columns above, update api.py:")
        print()
        print("Find the dataframe_to_biomarkers() function and update:")
        print()
        print("biomarker = {")
        print(f"    'name': str(row['<YOUR_NAME_COLUMN>']),")
        print(f"    'value': float(row['<YOUR_VALUE_COLUMN>']),")
        print(f"    'unit': str(row['<YOUR_UNIT_COLUMN>']),")
        print(f"    'referenceRange': {{")
        print(f"        'min': float(row['<YOUR_MIN_COLUMN>']),")
        print(f"        'max': float(row['<YOUR_MAX_COLUMN>'])")
        print(f"    }}")
        print("}")
        print()
        print("Replace <YOUR_*_COLUMN> with your actual column names from above.")
        print()
        print("See CONFIGURATION_GUIDE.md for detailed examples.")
        print()
        
    except Exception as e:
        print("=" * 60)
        print("ERROR during PDF processing:")
        print("=" * 60)
        print(f"{type(e).__name__}: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Default test PDF path - update this to match your test file
        pdf_path = "data/pdf/Blood_Test_Sample_JS.pdf"
        
        print("No PDF path provided. Using default path:")
        print(f"  {pdf_path}")
        print()
        print("To test with a different PDF:")
        print(f"  python {sys.argv[0]} path/to/your/test.pdf")
        print()
        
        if not os.path.exists(pdf_path):
            print("=" * 60)
            print("ERROR: Default test PDF not found")
            print("=" * 60)
            print()
            print("Please provide a PDF file path:")
            print(f"  python {sys.argv[0]} path/to/your/test.pdf")
            print()
            sys.exit(1)
    
    test_pdf_processing(pdf_path)
