# Configuration Guide - Adapting to Your Dataframe Structure

This guide helps you configure the API to work with your specific dataframe structure from `PDFReaderNam` and `DFAnalyzer`.

## Step 1: Identify Your Dataframe Columns

First, you need to know what columns your dataframe has. Run this test script:

```python
# test_dataframe_structure.py
from utils.our_pdf_reader import PDFReaderNam
from utils.df_analyzer import DFAnalyzer

# Use one of your sample PDFs
pdf_path = "data/pdf/Blood_Test_Sample_JS.pdf"

# Extract data
reader = PDFReaderNam(pdf_path=pdf_path)
data, data_dict, data_df = reader.analyze_pdf(to_df=True)

# Print dataframe structure
print("=" * 50)
print("DATAFRAME COLUMNS:")
print("=" * 50)
print(data_df.columns.tolist())
print()

print("=" * 50)
print("SAMPLE ROW:")
print("=" * 50)
print(data_df.iloc[0].to_dict())
print()

print("=" * 50)
print("FIRST 3 ROWS:")
print("=" * 50)
print(data_df.head(3))
```

Run it:
```bash
python test_dataframe_structure.py
```

## Step 2: Map Your Columns

Based on the output, identify which columns correspond to:

| Required Field | Your Column Name | Example Values |
|---------------|------------------|----------------|
| Biomarker/Test Name | ? | Hemoglobin, Glucose, etc. |
| Measured Value | ? | 14.5, 105, etc. |
| Unit | ? | g/dL, mg/dL, etc. |
| Reference Min | ? | 13.5, 70, etc. |
| Reference Max | ? | 17.5, 100, etc. |

## Step 3: Update api.py

Once you know your column names, update the `dataframe_to_biomarkers()` function in `api.py`:

### Example 1: Standard Column Names

If your dataframe has columns: `['Test', 'Value', 'Unit', 'Ref Low', 'Ref High']`

```python
def dataframe_to_biomarkers(df: pd.DataFrame) -> List[Dict]:
    biomarkers = []
    
    for _, row in df.iterrows():
        try:
            biomarker = {
                "name": str(row['Test']),
                "value": float(row['Value']),
                "unit": str(row['Unit']),
                "referenceRange": {
                    "min": float(row['Ref Low']),
                    "max": float(row['Ref High'])
                }
            }
            biomarkers.append(biomarker)
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Skipping row due to error: {e}")
            continue
    
    return biomarkers
```

### Example 2: Alternative Column Names

If your dataframe has columns: `['Biomarker', 'Result', 'Units', 'Lower Bound', 'Upper Bound']`

```python
def dataframe_to_biomarkers(df: pd.DataFrame) -> List[Dict]:
    biomarkers = []
    
    for _, row in df.iterrows():
        try:
            biomarker = {
                "name": str(row['Biomarker']),
                "value": float(row['Result']),
                "unit": str(row['Units']),
                "referenceRange": {
                    "min": float(row['Lower Bound']),
                    "max": float(row['Upper Bound'])
                }
            }
            biomarkers.append(biomarker)
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Skipping row due to error: {e}")
            continue
    
    return biomarkers
```

### Example 3: Spanish Column Names

If your dataframe has Spanish columns: `['Prueba', 'Valor', 'Unidad', 'Mínimo', 'Máximo']`

```python
def dataframe_to_biomarkers(df: pd.DataFrame) -> List[Dict]:
    biomarkers = []
    
    for _, row in df.iterrows():
        try:
            biomarker = {
                "name": str(row['Prueba']),
                "value": float(row['Valor']),
                "unit": str(row['Unidad']),
                "referenceRange": {
                    "min": float(row['Mínimo']),
                    "max": float(row['Máximo'])
                }
            }
            biomarkers.append(biomarker)
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Skipping row due to error: {e}")
            continue
    
    return biomarkers
```

### Example 4: Combined Range Column

If your reference range is in a single column like `'Range'` with format "13.5 - 17.5":

```python
def dataframe_to_biomarkers(df: pd.DataFrame) -> List[Dict]:
    biomarkers = []
    
    for _, row in df.iterrows():
        try:
            # Parse range string
            range_str = str(row['Range'])
            range_parts = range_str.split('-')
            ref_min = float(range_parts[0].strip())
            ref_max = float(range_parts[1].strip())
            
            biomarker = {
                "name": str(row['Test']),
                "value": float(row['Value']),
                "unit": str(row['Unit']),
                "referenceRange": {
                    "min": ref_min,
                    "max": ref_max
                }
            }
            biomarkers.append(biomarker)
        except (KeyError, ValueError, TypeError, IndexError) as e:
            logger.warning(f"Skipping row due to error: {e}")
            continue
    
    return biomarkers
```

## Step 4: Handle Missing or Optional Data

If some rows might have missing values, use `.get()` with defaults:

```python
def dataframe_to_biomarkers(df: pd.DataFrame) -> List[Dict]:
    biomarkers = []
    
    for _, row in df.iterrows():
        try:
            # Use .get() with defaults for optional fields
            name = str(row.get('Test', 'Unknown'))
            value = row.get('Value', None)
            unit = str(row.get('Unit', ''))
            ref_min = row.get('Ref Low', None)
            ref_max = row.get('Ref High', None)
            
            # Skip if critical data is missing
            if value is None or ref_min is None or ref_max is None:
                continue
            
            biomarker = {
                "name": name,
                "value": float(value),
                "unit": unit,
                "referenceRange": {
                    "min": float(ref_min),
                    "max": float(ref_max)
                }
            }
            biomarkers.append(biomarker)
        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping row due to error: {e}")
            continue
    
    return biomarkers
```

## Step 5: Test the Conversion

Create a test script to verify the conversion works:

```python
# test_biomarker_conversion.py
from utils.our_pdf_reader import PDFReaderNam
from api import dataframe_to_biomarkers
import json

pdf_path = "data/pdf/Blood_Test_Sample_JS.pdf"

# Extract data
reader = PDFReaderNam(pdf_path=pdf_path)
data, data_dict, data_df = reader.analyze_pdf(to_df=True)

# Convert to biomarkers
biomarkers = dataframe_to_biomarkers(data_df)

# Print results
print("=" * 50)
print(f"EXTRACTED {len(biomarkers)} BIOMARKERS:")
print("=" * 50)
print(json.dumps(biomarkers, indent=2))
```

Run it:
```bash
python test_biomarker_conversion.py
```

Expected output:
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
  },
  {
    "name": "Glucose",
    "value": 105.0,
    "unit": "mg/dL",
    "referenceRange": {
      "min": 70.0,
      "max": 100.0
    }
  }
]
```

## Common Issues and Solutions

### Issue 1: KeyError on Column Names

**Error:**
```
KeyError: 'Test'
```

**Solution:** Your column name doesn't match. Run Step 1 again to identify the correct column name.

### Issue 2: ValueError on Type Conversion

**Error:**
```
ValueError: could not convert string to float
```

**Solution:** Your value column might contain non-numeric data like "N/A" or "<5". Add handling:

```python
try:
    value = float(str(row['Value']).replace('<', '').replace('>', '').replace(',', '.'))
except ValueError:
    continue  # Skip this row
```

### Issue 3: Different Units in Same Column

If unit is embedded in value (e.g., "14.5 g/dL"):

```python
import re

value_str = str(row['Value'])
# Extract number
match = re.search(r'([\d.]+)', value_str)
value = float(match.group(1)) if match else None

# Extract unit
unit_match = re.search(r'[a-zA-Z/]+', value_str)
unit = unit_match.group(0) if unit_match else ''
```

### Issue 4: Index Column Being Read as Data

If pandas reads row numbers as data, skip them:

```python
# Add at the start of dataframe_to_biomarkers()
df = df.reset_index(drop=True)
```

## Advanced: Data Validation

Add validation to ensure data quality:

```python
def dataframe_to_biomarkers(df: pd.DataFrame) -> List[Dict]:
    biomarkers = []
    
    for idx, row in df.iterrows():
        try:
            name = str(row['Test']).strip()
            value = float(row['Value'])
            unit = str(row['Unit']).strip()
            ref_min = float(row['Ref Low'])
            ref_max = float(row['Ref High'])
            
            # Validation checks
            if not name or name == 'nan':
                logger.warning(f"Row {idx}: Missing biomarker name")
                continue
            
            if value < 0:
                logger.warning(f"Row {idx}: Negative value for {name}")
                continue
            
            if ref_min >= ref_max:
                logger.warning(f"Row {idx}: Invalid reference range for {name}")
                continue
            
            biomarker = {
                "name": name,
                "value": value,
                "unit": unit,
                "referenceRange": {
                    "min": ref_min,
                    "max": ref_max
                }
            }
            biomarkers.append(biomarker)
            
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Row {idx}: Skipping due to error: {e}")
            continue
    
    logger.info(f"Successfully extracted {len(biomarkers)} valid biomarkers")
    return biomarkers
```

## Need Help?

If you're still having issues:

1. Run the test scripts in this guide
2. Check the server logs for error messages
3. Print your dataframe structure
4. Verify your PDFReaderNam outputs the expected format
5. Test with a known good PDF file
