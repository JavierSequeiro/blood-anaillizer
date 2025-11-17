from google import genai
from google.genai import types
from fpdf import FPDF
import re
import os
import datetime
# Debugging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.genai.errors import APIError
from utils.myFPDF import SequeFPDF

class LLMReportGenerator:

    def __init__(self, prompt, user_type, language="en", file_name="myFile"):
        self.prompt = prompt
        self.user_type = user_type.lower()
        self.client = genai.Client(api_key="AIzaSyB6ls_XH2rRw8-afQXqrkNevv52THSpiyM")

        self.languages_correspondances = {"en": "English",
                                          "es": "Spanish",
                                          "ch": "Chinese",
                                          "fr": "French"}
        
        self.filename = file_name
 
        try:
            self.language = self.languages_correspondances[language]
        except KeyError:
            self.language = "English"

    @retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(APIError))

    def generate_report(self,save_result=True):

        system_instruction = self._get_base_instruction()
        # Set System Instruction
        config = types.GenerateContentConfig(system_instruction=system_instruction)

        myprompt = [self.prompt]

        try:
            print(f"Generating report for user type: **{self.user_type.capitalize()}**...")
            
            # Use a capable model like gemini-2.5-pro or gemini-2.5-flash or gemini-2.5-flash-lite
            response = self.client.models.generate_content(
                model='gemini-2.5-flash-lite', # Or 'gemini-2.5-pro' for more complex reasoning
                contents=myprompt,
                config=config,
            )

            if save_result:
                self.generate_pdf(response.text,)
            cleaned_response = self.force_latin1_compatibility(text=response.text)
            return cleaned_response
        except APIError as e:
            return f"Non-retryable API call: {e}"
        except Exception as e:
            return f"An unexpected error occurred during API call: {e}"

    def _get_base_instruction(self):

        base_instruction = "You are an expert AI clinician tasked with analyzing and summarizing blood tests results"

        if self.user_type == 'patient':
            # Low complexity, reassuring tone
            
            # system_instruction = (
            #     f"""
            #         You are a friendly and empathetic health advisor. Your goal is to help a person
            #         understand their lab results in a simple, clear, and positive way.

            #         Here are the person's lab results:
            #         {base_instruction}

            #         Please write a summary for the patient following these guidelines:
            #         0.  Write the report in {self.language} MANDATORY.
            #         1.  Simple Language: Explain the results as if you were talking to a friend.
            #         2.  Normal Results: Start by congratulating the person for the normal results.
            #         3.  Areas for Improvement: For each value outside of the normal range:
            #             a. Explain very simply what that parameter measures.
            #             b. Offer 2-3 practical and actionable lifestyle recommendations.
            #         4.  Positive and Motivational Tone.
            #         5.  Clear Structure: Short, easy-to-read paragraphs.
            #         6. Organize the report into 2–4 coherent paragraphs.
            #         7.  Final Disclaimer: You must end with the following text in the specified language:
            #             "Remember, this is an interpretation to help you understand your results.
            #             It does not replace a consultation with your doctor. Always talk to your doctor!"
            #         """
            #         )

            # system_instruction = (
            #     f"""
            #     You are an **Empathetic Health Coach and AI Report Generator**. Your primary goal is to interpret the provided blood test results for a patient using an encouraging, clear, and non-technical tone.

            #     Your response **MUST** strictly follow the detailed structure, headings, and formatting provided below. Adhere to the language specified in self.language.

            #     Here are the patient's lab results:
            #     {base_instruction}

            #     --- RESPONSE STRUCTURE MANDATE ---
                
            #     1.  **Report Structure and Tone:**
            #         * Maintain a **friendly, motivational, and highly accessible** tone throughout.
            #         * **STRICTLY AVOID** complex medical jargon, technical names for diseases, or clinical formulas.
            #         * Do not include the intro/outro lines "Here are the person's lab results" or "Please write a summary for the patient following these guidelines".

            #     2.  **Output Format (Must include all these section headers in this order):**

            #         **SUMMARY:**
            #         * Provide a 1-2 sentence overview, highlighting that results are mostly healthy but require minor lifestyle adjustments (like the sample report).

            #         **POSITIVE HIGHLIGHTS:**
            #         * List 3-5 parameters that are within optimal range (e.g., kidney function, white blood cells). Start by congratulating the person.

            #         **AREAS OF CONCERN:**
            #         * For each parameter outside the normal range, create a numbered list.
            #         * For each numbered item, include: **Parameter Name (Priority Level)**, **Result (with range)**, and **Recommendation** (2-3 highly practical, actionable lifestyle steps).
            #         * Use Priority Levels: **High, Moderate, Low** based on deviation from the normal range (e.g., LDL Cholesterol is Moderate).

            #         **RECOMMENDED ACTIONS:**
            #         * Provide a numbered list of 3-5 concrete next steps (e.g., "Schedule follow-up," "Start supplement," "Retest in 3 months").

            #         **LIFESTYLE RECOMMENDATIONS:**
            #         * Provide a list for **Nutrition, Exercise, Sleep, Stress, and Hydration** (5 total categories). Ensure each item is on its own line and prefixed cleanly with the list marker.

            #         **IMPORTANT NOTE:**
            #         * Include a standard medical disclaimer. You MUST use the following text (or its direct translation into {self.language}):
            #             "This analysis is based on a single blood test and AI interpretation. Individual results should always be interpreted by a qualified healthcare professional who can consider your complete medical history, symptoms, and other clinical factors. Always consult with your physician before making significant changes to your health regimen or starting new supplements."
                        
            #         **NEXT STEPS:**
            #         * End with the final call to action: "Please share these results with your primary care physician for personalized medical advice." (or its direct translation).
            #     """
            # )
            system_instruction = (
                f"""
                You are an **Empathetic Health Coach and AI Report Generator**. Your primary goal is to interpret the provided blood test results for a patient using an encouraging, clear, and non-technical tone.

                Your response **MUST** strictly follow the detailed structure, headings, and formatting provided below. Adhere to the language specified in self.language.
                Your response and section headers **MUST** also be written in {self.language} language.

                Here are the patient's lab results:
                {base_instruction}

                --- RESPONSE STRUCTURE MANDATE ---
                
                1.  **Report Structure and Tone:**
                    * Maintain a **friendly, motivational, and highly accessible** tone throughout.
                    * **STRICTLY AVOID** complex medical jargon, technical names for diseases, or clinical formulas.
                    * **MANDATORY BOLDING:** Bold all key parameters, findings, recommendations, and section names within the text.
                    * Do not include the intro/outro lines "Here are the person's lab results" or "Please write a summary for the patient following these guidelines".

                2.  **Output Format (Must include all these section headers in this order):**

                    **SUMMARY:**
                    * Write a single, comprehensive paragraph (2-3 sentences) summarizing the results, emphasizing that results are **mostly healthy** but require minor **lifestyle adjustments**.

                    **POSITIVE HIGHLIGHTS:**
                    * Write a single, comprehensive paragraph (3-5 sentences) that congratulates the person on their **excellent markers**. Mention key systems like **kidney function**, **blood cell counts**, and **electrolyte balance**, ensuring these systems are **bolded**.

                    **AREAS OF CONCERN:**
                    * For each parameter outside the normal range, create a **single, clearly separated paragraph** starting with the numbered item.
                    * The format for each numbered paragraph must be: **N. Parameter Name (Priority Level):** The paragraph must then describe the **Result (with range)** and provide 2-3 **practical, actionable lifestyle recommendations**.
                    * Use Priority Levels: **High, Moderate, Low** based on deviation from the normal range (e.g., LDL Cholesterol is **Moderate**).

                    **RECOMMENDED ACTIONS:**
                    * Write a single, comprehensive paragraph (3-5 sentences) detailing the **concrete next steps**. Integrate the 3-5 key actions (e.g., **scheduling follow-up**, **incorporating more protein**, **retesting in 3 months**) into the paragraph naturally without using an explicit numbered list.

                    **LIFESTYLE RECOMMENDATIONS:**
                    * Write a single, comprehensive paragraph covering **Nutrition**, **Exercise**, **Sleep**, **Stress**, and **Hydration**. Ensure each of these five categories is **bolded** within the text and followed by its specific advice. Do not use any list markers or separate lines for these items.

                    **IMPORTANT NOTE:**
                    * Write a single, standalone paragraph for the medical disclaimer. You MUST use the following text (or its direct translation into {self.language}):
                        "This analysis is based on a single blood test and AI interpretation. Individual results should always be interpreted by a qualified healthcare professional who can consider your **complete medical history**, symptoms, and other clinical factors. Always consult with your physician before making significant changes to your health regimen or starting new supplements."
                        
                    **NEXT STEPS:**
                    * Write a single, final sentence that serves as the call to action: "Please share these results with your primary care physician for **personalized medical advice**." (or its direct translation).
                """
            )

        elif self.user_type == 'doctor':
            # High complexity, technical tone
            # system_instruction = (f"""
            #     You are a licensed medical doctor specializing in clinical laboratory interpretation.
            #     Below are the patient's blood test results:

            #     {base_instruction}

            #     Please write a concise medical report that follows these guidelines:
            #     0.  Write the report in {self.language} MANDATORY.
            #     1. Summarize all normal findings briefly.
            #     2. Describe in more detail the parameters marked as “Low” or “High”.
            #     3. If any abnormal or borderline values could be associated, mention them as hypotheses.
            #     4. Use clear, professional medical language in English.
            #     5. Organize the report into 2–4 coherent paragraphs.
            #     6. End with this disclaimer in the specified language:
            #     “This report is for informational purposes only and does not replace professional medical evaluation.”
            #     """)

            system_instruction = (
                f"""
                You are a **Specialized Clinical Pathologist and Medical Consultant**. Your primary goal is to provide a comprehensive, objective, and technical analysis of the provided blood test results, suitable for review by a practicing healthcare professional.

                Your response **MUST** strictly follow the detailed structure, headings, and formatting provided below. Adhere to the language specified in self.language.
                Your response and section headers **MUST** also be written in {self.language} language.

                Here are the patient's lab results:
                {base_instruction}

                --- RESPONSE STRUCTURE MANDATE ---
                
                1.  **Report Structure and Tone:**
                    * Maintain a **strictly technical, formal, and objective tone**. Avoid patient-facing language (e.g., "friendly," "motivational").
                    * **MANDATORY TERMINOLOGY:** Use precise medical and laboratory terminology (e.g., use 'erythrocytes' instead of 'red blood cells,' 'leukocyte' instead of 'white blood cell,' 'reference interval' instead of 'range').
                    * **MANDATORY BOLDING:** Bold all key parameters, clinical findings, potential diagnoses, and section names for emphasis.
                    * Do not include the intro/outro lines "Here are the person's lab results" or "Please write a summary for the patient following these guidelines".

                2.  **Output Format (Must include all these section headers in this order):**

                    **CLINICAL SUMMARY:**
                    * Write a single, concise paragraph (2-3 sentences) providing a high-level overview of the **global hematological and biochemical status**, noting both the overall stability and the specific systems with deviations.

                    **NORMAL PARAMETERS:**
                    * Write a single, comprehensive paragraph (3-5 sentences) summarizing the key systems and parameters found to be within their respective **reference intervals**. Highlight essential functions like **renal indices**, **hepatic enzymes**, or **coagulation factors**.

                    **ABNORMAL FINDINGS AND INTERPRETATION:**
                    * For each parameter outside the reference interval, create a **single, clearly separated paragraph** starting with the numbered item.
                    * The format for each numbered paragraph must be: **N. Parameter Name (Magnitude of Deviation):** The paragraph must then state the **Result (with reference interval)**, describe the **clinical implications**, and discuss the **most relevant differential diagnoses (DDx)**.
                    * Use Deviation descriptors: **Marked, Moderate, Mild** based on deviation from the reference interval.

                    **DIFFERENTIAL DIAGNOSIS:**
                    * Write a single, comprehensive paragraph (3-5 sentences) consolidating all abnormal findings and proposing 3-5 **probable diagnostic hypotheses**. Justify each hypothesis based on the **laboratory correlation** without using an explicit numbered list.

                    **RECOMMENDED CLINICAL ACTIONS:**
                    * Write a single, comprehensive paragraph (3-5 sentences) detailing the **concrete next diagnostic and management steps**. Integrate the 3-5 key actions (e.g., **follow-up assays**, **imaging studies**, **specific consultations**, **management initiation**) into the paragraph naturally without using an explicit numbered list.

                    **DISCLAIMER (MANDATORY):**
                    * Write a single, standalone paragraph for the clinical disclaimer. You MUST use the following text (or its direct translation into {self.language}):
                        "This AI interpretation is for informational and consultative purposes only. It is based solely on the provided laboratory data and does not substitute for a comprehensive **clinical assessment**, physical examination, or professional medical diagnosis by the treating physician. Results must be evaluated within the context of the patient's **full medical history** and current symptomatology."
                        
                    **FURTHER EVALUATION:**
                    * Write a single, final sentence that reinforces the need for **physician oversight**: "Final diagnosis and treatment plan must be determined by the treating physician following a complete **clinical correlation**." (or its direct translation).
                """
            )
        else:
            # Default or fallback instruction
            print(f"Warning: Unknown user type '{self.user_type}'. Using standard professional analysis.")
            system_instruction = f"{base_instruction} Provide a balanced, professional analysis."

        return system_instruction
    
    

    def render_markdown_text(self, pdf, text, font_type, font_size, line_height, write_bold=False):
        """
        Renders text, now with specific handling for Section Headers, list items, 
        and general paragraphs, managing the manual bolding and wrapping logic.
        """

        HEADER_PATTERN = re.compile(r'^(\*\*.*?\*\*\s*[:：]?)')
        # --- Pre-processing: Clean up non-breaking spaces ---
        text = text.replace('\xa0', ' ').strip()
        
        # ------------------------------------------------------------------------
        # A. Handle BOLD SECTION HEADERS (e.g., **SUMMARY:** Your recent blood test...)
        # ------------------------------------------------------------------------
        header_match = HEADER_PATTERN.match(text)

        if header_match:
            # Extract the bold header part (e.g., **SUMMARY:**)
            header_markdown = header_match.group(1) 
            header_text = header_markdown.strip('*:：').strip() # Remove ** and :/:
            
            bold_title = re.search(r'\*\*(.*?)\*\*', header_markdown).group(1)
            # Text remaining after the header
            text_content = text[header_match.end():].strip()
            
            # Render the header text in bold
            pdf.set_font(font_type, "B", font_size)
            pdf.cell(pdf.get_string_width(bold_title), line_height, f"{bold_title}", ln=1, align='')

            # if ':' in header_markdown or '：' in header_markdown:
            #     pdf.set_font(font_type, "B", font_size)
                # pdf.cell(pdf.get_string_width(': '), line_height, ': ', ln=0, align='')
            
            # Switch font back to regular for the body text
            pdf.set_font(font_type, "", font_size)
            
            # Render the remaining text (always Latin mode for these headers)
            words = re.findall(r'\S+\s*|\s+', text_content)
            bold_check = False
            for word in words:
                # print(f"WORD: {word}")
                

                if word.startswith("**"):
                    bold_check = True
                    word = word.lstrip("**")

                
                if bold_check or write_bold:
                    pdf.set_font(font_type, "B", font_size)
                else:
                    pdf.set_font(font_type, "", font_size)

                if word.endswith("**") or word.endswith("** ") or word.endswith("**.") or word.endswith("**. ") or word.endswith("**,") or word.endswith("**, ")  or word.endswith("**:") or word.endswith("**;"):
                    bold_check = False
                    word = word.replace("**","")

                word_width = pdf.get_string_width(word)
                if pdf.get_x() + word_width > pdf.w - pdf.r_margin:
                    pdf.ln(line_height) 
                    pdf.set_x(pdf.l_margin) # Start new line from left margin
                
                pdf.cell(word_width, line_height, word, border=0, ln=0, align='')
            
            if len(words) != 0:
                pdf.ln(line_height) # Final line break after the header paragraph
            return
        
        else:

            # Render the remaining text (always Latin mode for these headers)
            words = re.findall(r'\S+\s*|\s+', text)
            bold_check = False
            for word in words:
                # print(f"WORD: {word}")
                

                if word.startswith("**"):
                    bold_check = True
                    word = word.lstrip("**")

                
                if bold_check or write_bold:
                    pdf.set_font(font_type, "B", font_size)
                else:
                    pdf.set_font(font_type, "", font_size)

                if word.endswith("**") or word.endswith("** ") or word.endswith("**.") or word.endswith("**. ") or word.endswith("**,") or word.endswith("**, ")  or word.endswith("**:") or word.endswith("**;"):
                    bold_check = False
                    word = word.replace("**","")

                word_width = pdf.get_string_width(word)
                if pdf.get_x() + word_width > pdf.w - pdf.r_margin:
                    pdf.ln(line_height) 
                    pdf.set_x(pdf.l_margin) # Start new line from left margin
                
                pdf.cell(word_width, line_height, word, border=0, ln=0, align='')
            
            pdf.ln(line_height) # Final line break after the header paragraph
            return


    def chinese_render_markdown_text(self, pdf, text, font_type, font_size, line_height):
        """
        Renders text, now with specific handling for Section Headers, list items, 
        and general paragraphs, managing the manual bolding and wrapping logic.
        """

        HEADER_PATTERN = re.compile(r'^(\*\*.*?\*\*\s*[:：]?)')
        # --- Pre-processing: Clean up non-breaking spaces ---
        text = text.replace('\xa0', ' ').strip()
        
        # ------------------------------------------------------------------------
        # A. Handle BOLD SECTION HEADERS (e.g., **SUMMARY:** Your recent blood test...)
        # ------------------------------------------------------------------------
        header_match = HEADER_PATTERN.match(text)

        if header_match:
            # Extract the bold header part (e.g., **SUMMARY:**)
            header_markdown = header_match.group(1) 
            header_text = header_markdown.strip('*:：').strip() # Remove ** and :/:
            
            bold_title = re.search(r'\*\*(.*?)\*\*', header_markdown).group(1)
            bold_title = bold_title.replace("**","")
            
            
            # Render the header text in bold
            pdf.set_font(font_type, "", font_size)
            pdf.cell(pdf.get_string_width(bold_title), line_height, f"{bold_title}", ln=1, align='')
            
            # Text remaining after the header
            text_content = text[header_match.end():].strip()
            text_content = text_content.replace("**","")
            pdf.multi_cell(0, line_height, text_content, border=0, align="L")
            
            # Add final line break for paragraph spacing
            pdf.ln(3) 
            return

        # After finishing the entire paragraph, move cursor down
        pdf.ln(line_height)

    

    def force_latin1_compatibility(self, text):
        """
        Removes or replaces problematic non-latin-1 characters 
        (like smart quotes and en dashes) with safe ASCII equivalents.
        """
        
        text = text.replace('•', '-')
        # Replace the problematic en dash (\u2013) and em dash (\u2014) with a hyphen
        text = text.replace('–', '-') 
        text = text.replace('—', '-') 
        
        # Replace smart quotes with straight quotes
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace('‘', "'").replace('’', "'")
        
        # Now, encode/decode to clean out any remaining characters outside latin-1.
        # We use 'latin-1' here to preserve the accents (é, à, ç, etc.)
        safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
        
        return safe_text

    def generate_pdf(self, response):
        
        # ... (Output path setup is unchanged)
        output_folder = f"data/output/reports/{self.filename}"
        os.makedirs(output_folder, exist_ok=True)
        if self.user_type == "doctor":
            output_path = os.path.join(output_folder, f"LLM_Generated_Report_Doctor_Version_{self.language}.pdf")
        else:
            output_path = os.path.join(output_folder, f"LLM_Generated_Report_Patient_Version_{self.language}.pdf")

        # Create PDF
        # pdf = FPDF()
        pdf = SequeFPDF()

        DEFAULT_FONT_NAME = 'DefaultUnicode'
        try:
            pdf.add_font('ChineseFont', '', './utils/SimHei.ttf', uni=True)
            CHINESE_FONT_LOADED = True

            
            pdf.add_font(DEFAULT_FONT_NAME,'', './utils/DejaVuSans.ttf')
            pdf.add_font(DEFAULT_FONT_NAME,'B', './utils/DejaVuSans-Bold.ttf')
            pdf.add_font(DEFAULT_FONT_NAME,'I', './utils/DejaVuSans-Oblique.ttf')
        except Exception:
            # Handle case where font files are missing
            print("Warning: Chinese font loading failed. Chinese characters will not render.")
            CHINESE_FONT_LOADED = False

        pdf.set_auto_page_break(auto=True, margin=25)
        pdf.add_page()


        # --- Body: Use the new Markdown rendering function ---
        pdf_font_size = 8.5
        pdf_line_height = 5
        

        pdf.set_font(DEFAULT_FONT_NAME, size=pdf_font_size)
        
        # Split into paragraphs and render each one
        # if CHINESE_FONT_LOADED:
        #     pass
        # else:
        #     response = self.force_latin1_compatibility(text=response)
        paragraphs = [p.strip() for p in response.split("\n\n") if p.strip()]
        # print(paragraphs)
        for i, para in enumerate(paragraphs):
            if CHINESE_FONT_LOADED and self.contains_chinese_characters(para):
                # Apply the dedicated Chinese font and encoding
                # pdf.set_font('ChineseFont', '', size=10) 
                # Note: For Chinese, you might need a different rendering method 
                # or a simple pdf.multi_cell(0, 6, para) if using the FPDF
                # extension FPDF-TPL which supports Unicode.
                # pdf.multi_cell(0, 6, para)
                font_type = 'ChineseFont'
                self.chinese_render_markdown_text(pdf, para, font_type, pdf_font_size, pdf_line_height)

            else:
                # The complex part: rendering text with bolding and word wrapping
                font_type = DEFAULT_FONT_NAME
                if i == len(paragraphs)-1:
                    print("LAST PARAGRAPH BOLD")
                    self.render_markdown_text(pdf, para, font_type, pdf_font_size, pdf_line_height, write_bold=True)
                else:
                    self.render_markdown_text(pdf, para, font_type, pdf_font_size, pdf_line_height)
                pdf.ln(3) # Paragraph spacing
            
        pdf_stream = pdf.output()
      
        return bytes(pdf_stream)
    
    def contains_chinese_characters(self, text: str) -> bool:
        # (Insert the regex detection function here)
        cjk_pattern = re.compile(r'[\u4e00-\u9fff]')
        return bool(cjk_pattern.search(text))   
