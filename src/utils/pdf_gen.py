from fpdf import FPDF
import datetime
import os
import pandas as pd

class BaseReportPDF(FPDF):
    def header(self):
        # Logo or Title
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Fraud Analytics - Intelligence Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.cell(0, 10, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'R')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, f'  {label}', 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        # Encode to latin-1 to avoid fpdf unicode errors, replacing unsupported chars
        clean_text = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, clean_text)
        self.ln()

    def add_image_section(self, image_path, title=None):
        if title:
            self.chapter_title(title)
        if image_path and os.path.exists(image_path):
            try:
                # Center image, width 170mm (leaving margins)
                self.image(image_path, x=20, w=170)
                self.ln(10)
            except Exception as e:
                self.chapter_body(f"[Error embedding image: {e}]")
                self.ln()

def create_report(question, summary_text, image_path, output_path):
    """Legacy function for Graph RAG - kept for compatibility."""
    pdf = BaseReportPDF()
    pdf.add_page()
    
    pdf.chapter_title("Analysis Objective")
    pdf.chapter_body(question)
    
    pdf.add_image_section(image_path, "Graph Visualization")

    pdf.chapter_title("AI Intelligence Report")
    clean_summary = summary_text.replace("###", "").replace("**", "").replace("* ", "- ")
    pdf.chapter_body(clean_summary)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    return output_path

def create_trends_report(source_name, sections, output_path):
    """
    Generate a generic report for Trends & Insights.
    sections: List of dicts {'title': str, 'content': str, 'image': str (opt)}
    """
    pdf = BaseReportPDF()
    pdf.add_page()

    # Introduction
    pdf.chapter_title("Source Dataset")
    pdf.chapter_body(f"Data Source: {source_name}")
    
    for section in sections:
        if section.get('title'):
            pdf.chapter_title(section['title'])
        
        if section.get('content'):
            # Basic markdown stripping
            clean_content = section['content'].replace("###", "").replace("**", "").replace("```", "")
            pdf.chapter_body(clean_content)
        
        if section.get('image'):
            pdf.add_image_section(section['image'])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    return output_path
