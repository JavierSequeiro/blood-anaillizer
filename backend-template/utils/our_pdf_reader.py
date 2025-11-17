import pdfplumber
import re
import pandas as pd

class PDFReaderNam:

    def __init__(self, pdf_path) -> None:
        self.path = pdf_path

    def read_pdf(self):
        all_text = ""
        with pdfplumber.open(self.path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text: # Avoid empty pages
                    all_text += text + "\n"

        text_per_lines = all_text.split("\n")
        return text_per_lines

    
    def analyze_pdf(self,to_df=True):
        text_per_lines = self.read_pdf()

        # Pattern for normal ranges (low - high)
        pattern_range = (
            r"([A-Za-z0-9ÁÉÍÓÚÜáéíóúüñ\(\)/\-\s\*\.]+?)"  # test name
            r"\s+H?([\d.,]+(?:E\d+)?)"                   # value
            r"\s*([a-zA-Z0-9/%µ\.\*]*)?"                 # unit
            r"\s+([\d.,]+)\s*(?:-|\s)\s*([\d.,]+)"       # ref low and high (with or without dash)
        )

        # Pattern for thresholds (< or > inside line, with or without brackets)
        pattern_threshold = (
            r"([A-Za-z0-9ÁÉÍÓÚÜáéíóúüñ\(\)/\-\s\*\.]+?)"
            r"\s*([<>])?\s*([\d.,]+(?:E\d+)?)"
            r"\s*([a-zA-Z0-9/%µ\.\,\^]*\s*m2|[a-zA-Z0-9/%µ\.\,\^]*)?"
            r"\s*([<>])\s*([\d.,]+)"
        )

        data = []
        data_dict = []
        for line in text_per_lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(("Page", "Página")):
                continue
            if not any(c.isdigit() for c in line):
                continue

            # Replace commas with dots for decimals
            line = line.replace(",", ".")
            line = line.replace("[", "").replace("]", "").replace(",", ".").replace("*", "")

            # Case 1: normal ranges
            for match in re.finditer(pattern_range, line):
                test, value, unit, ref_low, ref_high = match.groups()
                data.append([
                    test.strip(),
                    float(value),
                    unit if unit else "",
                    float(ref_low),
                    float(ref_high),
                    "Biomarkers"
                ])

                data_dict.append({
                    'id': test.strip(),
                    'name': test.strip(),
                    'value': float(value),
                    'unit': unit if unit else "",
                    'referenceRange': {'min':float(ref_low), 'max': float(ref_high)},
                    'category': "Biomarkers"})

            # Case 2: thresholds (< or >)
            for match in re.finditer(pattern_threshold, line):
                test, sign_val, value, unit, sign_ref, limit = match.groups()
                value = float(value.replace(",", ".")) if value else None
                limit = float(limit.replace(",", ".")) if limit else None
                
                # adjust ref range
                if sign_ref == "<":
                    ref_low, ref_high = 0.0, limit
                else:  # ">"
                    ref_low, ref_high = limit, 10e12#float("inf")

                data.append([
                    test.strip(),
                    value,
                    unit if unit else "",
                    ref_low,
                    ref_high,
                    "Biomarkers"
                ])

                data_dict.append({
                    'id': test.strip(),
                    'name': test.strip(),
                    'value': value,
                    'unit': unit if unit else "",
                    'referenceRange': {'min': ref_low, 'max': ref_high},
                    'category': "Biomarkers"})
        
        if to_df: 
            data_df = pd.DataFrame(data,columns=["Test", "Value", "Unit", "Ref Low", "Ref High" , "Category"])
            return data, data_dict, data_df
        else:
            return data, data_dict