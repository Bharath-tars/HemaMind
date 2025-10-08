import pdfplumber
import streamlit as st
from config.app_config import MAX_PDF_PAGES
from utils.validators import validate_pdf_file, validate_pdf_content
import easyocr
import numpy as np

# MAX_PDF_PAGES = 20  # Maximum number of pages allowed in a PDF

def extract_text_with_ocr(pdf_file):
    """Extract text from scanned PDFs using EasyOCR."""
    try:
        reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader for English
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted and extracted.strip():
                    text += extracted.strip() + "\n"
                else:
                    # Perform OCR using EasyOCR
                    page_image = page.to_image(resolution=150)
                    pil_image = page_image.annotated  # Use the annotated PIL image
                    # Convert PIL Image to NumPy array
                    np_image = np.array(pil_image)
                    ocr_result = reader.readtext(np_image, detail=0)  # Extract text
                    if ocr_result:
                        text += " ".join(ocr_result) + "\n"
        
        # Validate extracted content
        is_valid, error = validate_pdf_content(text)
        if not is_valid:
            return error
        
        # Return empty string message if no text was extracted
        if not text.strip():
            return "No text could be extracted from the PDF."
        
        return text
    
    except Exception as e:
        return f"Unexpected error extracting text from scanned PDF: {str(e)}"


def extract_text_from_pdf(pdf_file):
    """Extract and validate text from PDF file."""
    try:
        # Validate file first
        is_valid, error = validate_pdf_file(pdf_file)
        if not is_valid:
            return error

        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            if len(pdf.pages) > MAX_PDF_PAGES:
                return f"PDF exceeds maximum page limit of {MAX_PDF_PAGES}"
                
            for page in pdf.pages:
                extracted = page.extract_text()
                if not extracted or not extracted.strip():
                    # Use OCR if text extraction fails or is empty
                    return extract_text_with_ocr(pdf_file)
                text += extracted.strip() + "\n"
        
        # Validate extracted content
        is_valid, error = validate_pdf_content(text)
        if not is_valid:
            return error
            
        return text
    except ValueError as e:
        return f"Invalid PDF format: {str(e)}"
    except FileNotFoundError:
        return f"PDF file not found: {pdf_file}"
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"
    

# Test code
if __name__ == "__main__":
    result = extract_text_from_pdf("SVSaradhi_Diagnosis_Reports[1].pdf")
    print(result)