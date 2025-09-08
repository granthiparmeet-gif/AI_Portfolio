from .parser import extract_text_from_pdf
from .qa_utils import get_contract_answer
from common.exceptions import BaseAIError

def analyze_contract(uploaded_file, question: str) -> str:
    try:
        text = extract_text_from_pdf(uploaded_file)
        return get_contract_answer(text, question)
    except BaseAIError as e:
        return f"Error: {str(e)}"
