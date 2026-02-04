import pdfplumber
import os
from pathlib import Path

def parse_resume(file_path: str) -> str:
    """
    Extract text from PDF, DOCX, or TXT files.
    """
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return parse_pdf(file_path)
        elif file_ext == '.txt':
            return parse_txt(file_path)
        elif file_ext == '.docx':
            return parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return ""

def parse_pdf(file_path: str) -> str:
    """
    Extract text from PDF file.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    
    return text

def parse_txt(file_path: str) -> str:
    """
    Read text from TXT file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""

def parse_docx(file_path: str) -> str:
    """
    Extract text from DOCX file.
    """
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove special characters but keep alphanumeric and basic punctuation
    return text.lower()
