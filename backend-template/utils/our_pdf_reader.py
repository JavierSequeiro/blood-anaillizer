import pdfplumber
import re
import pandas as pd
from google import genai
from google.genai import types
import os
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.genai.errors import APIError

class PDFReader_:

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
    
    @retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(APIError)) 
    def get_llm_response(self, prompt):

        # # Set System Instruction
        # config = types.GenerateContentConfig(system_instruction=system_instruction)

        myprompt = [prompt]
        gemini_api_key = os.environ.get("GEMINI-API-KEY")
        client = genai.Client(api_key=gemini_api_key)

        try:
            # Use a capable model like gemini-2.5-pro or gemini-2.5-flash or gemini-2.5-flash-lite
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite', # Or 'gemini-2.5-pro' for more complex reasoning
                contents=myprompt)
            
            return response.text
            
        except APIError as e:
            return f"Non-retryable API call: {e}"
        except Exception as e:
            return f"An unexpected error occurred during API call: {e}"

    
    def standardize_biomarkers(self, biomarkers_list, language):

        languages_correspondances = {"en": "English",
                                        "es": "Spanish",
                                        "ch": "Chinese",
                                        "fr": "French"}
        language = languages_correspondances[language]

        biomarkers_list = "Active B12, Alanine Aminotransferase (ALT), Albumin, Alkaline Phosphatase (ALP), Anti-Müllerian Hormone, Apolipoprotein A (APOA), Apolipoprotein B (APOB), Calcium, Chloride, Cortisol (9am), Creatine Kinase, Creatinine, eGFR, Ferritin, Folate (serum), Follicle Stimulating Hormone (FSH), Free Androgen Index, Gamma GT, Globulin, Haematocrit (HCT), Haemoglobin, HbA1c, HDL, hs-CRP, Iron, Lactate Dehydrogenase (LDH), LDL, Lipoprotein a (Lp(a)), Luteinising Hormone (LH), Magnesium (Serum), Mean Corpuscular Haemoglobin Concentration (MCHC), Monocytes, Non-HDL Cholesterol, Oestradiol (Oestrogen), Omega 6: Omega 3 Ratio, Platelet Count, Progesterone, Prolactin, Red Blood Cell (RBC), Sex Hormone Binding Globulin (SHBG), Sodium, Testosterone (total), Thyroglobulin Antibodies, Thyroid Peroxidase Antibodies, Thyroid Stimulating Hormone (TSH), Thyroxine (T4, Free Direct), Total Cholesterol, Total IgA, Total Protein, Transferrin Saturation, Triglyceride-to-HDL Ratio (TG:HDL Ratio), Triglycerides, Triiodothyronine (T3, Free), Urea, Uric Acid, Vitamin A, Vitamin D (25 OH), Vitamin E, White Blood Cell Count (WBC)"
        gen_prompt = f"""Overall List of Biomarkers: {biomarkers_list}.
                    Based on the overall list of biomarkers provided (JUST PROVIDE THE BIOMARKER, NO MORE WORDS), retrieve in {language} (IMPORTANT!) the biomarker that might represent the following one:
                    """
        
        for biomarker in biomarkers_list:
            biomarker_name = biomarker["name"]
            full_prompt = gen_prompt + biomarker_name
            standard_biomarker_name = self.get_llm_response(prompt=full_prompt)
            
            # Set new name
            biomarker["name"] = standard_biomarker_name
            biomarker["id"] = standard_biomarker_name

        return biomarkers_list


    
    def analyze_pdf(self, language, to_df=True):
        text_per_lines = self.read_pdf()

        # Pattern for normal ranges (low - high)
        pattern_range = (
            r"([A-Za-z0-9ÁÉÍÓÚÜáéíóúüñ\(\)/\-\s\*\.]+?)"  # test name
            r"\s+H?([\d.,]+(?:E\d+)?)"                   # value
            r"\s*([a-zA-Z0-9/%µ\.\*]*)?"                 # unit
            r"\s+([\d.,]+)\s*(?:-|à)\s*([\d.,]+)(?=\s|$)"       # ref low and high (with or without dash)
        )

        # Pattern for thresholds (< or > inside line, with or without brackets)
        pattern_threshold = (
            r"([A-Za-z0-9ÁÉÍÓÚÜáéíóúüñ\(\)/\-\s\*\.]+?)"
            r"\s*([<>])?\s*([\d.,]+(?:E\d+)?)"
            r"\s*([a-zA-Z0-9/%µ\.\,\^]*\s*m2|[a-zA-Z0-9/%µ\.\,\^]*)?"
            r"\s*([<>])\s*(?:\s*à\s*)?([\d.,]+)"
        )

        data = []
        data_dict = []
        for line in text_per_lines:
            line = line.strip()
            if "soit" in line:
                # print(line)
                segments = line.split("soit")
                segments[0]  = segments[0].replace("soit ","")
                segments[0] = re.sub(r'[0-9,%]','', segments[0])
                line = segments[0] + segments[1]
                # line = line.replace("soit ","")
                # line = re.sub(r'[0-9%]','', line)
                # print(f"After: {line}")
            if not line:
                continue
            if line.startswith(("Page", "Página")):
                continue
            if not any(c.isdigit() for c in line):
                continue

            # Replace commas with dots for decimals
            line = line.replace(",", ".")
            line = line.replace("[", "").replace("]", "").replace(",", ".").replace("*", "").replace("(","").replace(")","")

            # Case 1: normal ranges
            for match in re.finditer(pattern_range, line):
                test, value, unit, ref_low, ref_high = match.groups()
                value = value.replace(" ", "")
                ref_low = ref_low.replace(" ", "")
                ref_high = ref_high.replace(" ", "")
                
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
                
        # data_dict_standardized = self.standardize_biomarkers(biomarkers_list=data_dict, language=language)
        
        if to_df: 
            data_df = pd.DataFrame(data,columns=["Test", "Value", "Unit", "Ref Low", "Ref High" , "Category"])
            return data, data_dict, data_df
            # return data, data_dict_standardized, data_df
        else:
            return data, data_dict