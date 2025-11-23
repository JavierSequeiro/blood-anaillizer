import pdfplumber
import re
import pandas as pd
from utils.our_pdf_reader import PDFReader_
import pypdf
import fitz

class SyntheticTestGenerator:

    def __init__(self, logger) -> None:
        self.logger = logger


    # def generate_synthetic_report(self, pdf_path):
    #     pdfreader = PDFReader_(pdf_path=pdf_path)

        # pdf_ = pdfplumber.open(pdf_path)
        # pdf_ = pypdf.PdfReader(pdf_path)
        # print(pdf_.metadata)

        # pdf_data = pdfreader.read_pdf()
        # print(pdf_data)
        # import pypdf

        # reader = pypdf.PdfReader(pdf_path)
        # gf_fields = reader.read()
        # fields = reader.get_fields()
        # print(fields)
        # print(gf_fields)

        # Print the names and current values of all fields
        # for name, field in fields.items():
        #     print(f"Field Name: '{name}' | Type: {field.field_type} | Current Value: {field.value}")

    def generate_synthetic_report(self, pdf_path_in, pdf_path_out, replacements):
        """
        Reads a static PDF, replaces specific text values, and saves the new PDF.

        Args:
            pdf_path_in (str): Path to the original PDF file.
            pdf_path_out (str): Path to save the modified PDF file.
            replacements (dict): Dictionary where keys are the old text strings 
                                to find, and values are the new text strings to replace them with.
        """
        try:
            doc = fitz.open(pdf_path_in)
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return

        # Iterate through every page in the document
        for page in doc:
            # Loop through all replacement items provided
            for old_text, new_text in replacements.items():
                
                # Use 'search_for' to find all occurrences of the old text on the page
                # This returns a list of fitz.Rect objects (bounding boxes)
                found_rects = page.search_for(old_text)
                
                # Process each location where the old text was found
                for rect in found_rects:
                    # --- Step 1: Blank out the old text ---
                    # Draw a white-filled rectangle over the old text's bounding box.
                    # This effectively erases the old value.
                    page.draw_rect(
                        rect, 
                        color=(1, 1, 1), # White color
                        fill=(1, 1, 1), 
                        overlay=True
                    )
                    
                    # --- Step 2: Insert the new text ---
                    # The text is inserted at the top-left corner of the old rectangle.
                    # NOTE: For perfect alignment, you often need to manually adjust 
                    # the insert point (rect.tl) and guess the original font size.
                    
                    # A common default font size for reports is 9 or 10. Adjust as needed.
                    font_size_guess = 9
                    
                    # Insert the new text using the top-left point (rect.tl)
                    page.insert_text(
                        rect.bl, 
                        new_text,
                        fontsize=font_size_guess,
                        color=(0, 0, 0) # Black text
                    )

        # Save the modified document
        doc.save(pdf_path_out, deflate=True)
        doc.close()
        print(f"Successfully generated synthetic report: {pdf_path_out}")

    # update_pdf_values("original_report.pdf", "synthetic_report.pdf", blood_test_replacements)
