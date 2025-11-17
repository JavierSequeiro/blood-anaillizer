from fpdf import FPDF
import os
import datetime

class SequeFPDF(FPDF):
    """Custom FPDF class to add a consistent footer on every page."""
    
    # Text you want to appear in the footer
    FOOTER_TEXT = "This report is AI-generated and intended for informational purposes only."
    
    def footer(self):
        # Set position at 15 mm from bottom
        self.set_y(-15)
        
        # Set font
        DEFAULT_FONT_NAME = "DefaultUnicode"
        self.set_font(DEFAULT_FONT_NAME, 'I', 8)
        
        # Draw a thin line above the footer text
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.2)
        # Draw line from left margin to right margin
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_y(self.get_y() + 1) # Move down slightly after the line

        # Print the disclaimer text centered
        # w=0 means fill the entire available width
        self.multi_cell(w=0, h=4, txt=self.FOOTER_TEXT, border=0, align='C')
        
        # Add page number (e.g., Page 1/N)
        # self.set_font(DEFAULT_FONT_NAME, 'I', 7)
        # self.cell(0, 3, f'Page {self.page_no()}/{{nb}}', border=0, ln=1, align='R')

    def header(self):
        logo_candidates = [
            "./utils/Company_Logo.png",
        ]
        logo_path = None
        for p in logo_candidates:
            if os.path.exists(p):
                # print(f"Path Exists")
                logo_path = p
                break

        # Insert centered logo if available
        if logo_path:
            # Compute a reasonable logo width (max 60mm or page width minus margins)
            available_width = self.w - 2 * self.l_margin
            logo_w = min(40, available_width)
            logo_x = (self.w - logo_w) / 2
            logo_y = 8
            self.image(logo_path, x=logo_x, y=logo_y, w=logo_w)
            # Move cursor below the logo
            self.set_y(logo_y + (logo_w * 0.4) + 2)
        else:
            # Space reserved when no logo
            self.ln(8)

        # Header: Title and date (centered)
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "LLM Generated Report", ln=True, align="C")

        self.set_font("Arial", size=9)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(0, 6, f"Generated: {now_str}", ln=True, align="C")

        # Separator line
        self.ln(4)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    