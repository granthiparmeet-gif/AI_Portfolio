import pdfplumber
from common.logger import get_logger
from common.exceptions import ContractParseError

logger = get_logger(__name__)

def extract_text_from_pdf(file) -> str:
    """Extracts text from a PDF file using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        if not text.strip():
            raise ContractParseError("No text could be extracted from PDF.")
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        logger.error(f"PDF parsing failed: {e}")
        raise ContractParseError("Could not process contract PDF.")
