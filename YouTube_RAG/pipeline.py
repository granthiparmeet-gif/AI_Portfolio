from dotenv import load_dotenv
from .transcript_utils import extract_video_id, get_transcript
from .retriever_utils import build_retriever
from .qa_utils import get_answer
from common.exceptions import BaseAIError  # updated import

load_dotenv()

def answer_question(url: str, question: str):
    try:
        video_id = extract_video_id(url)
        text = get_transcript(video_id)
        retriever = build_retriever(text)
        return get_answer(question, retriever)  # returns {"answer","context"}
    except BaseAIError as e:  # updated exception
        return {"answer": f"Error: {str(e)}", "context": []}