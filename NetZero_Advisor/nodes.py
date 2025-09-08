import os
from langchain_openai import ChatOpenAI
from common.logger import get_logger
from common.exceptions import BaseAIError

logger = get_logger(__name__)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
)

def extractor_agent(state: dict) -> dict:
    """Extracts sustainability/energy data from uploaded file."""
    text = state.get("file_content", "")
    if not text:
        raise BaseAIError("No file content provided.")
    logger.info("Extractor processed input file.")
    return {"raw_text": text, **state}

def calculator_agent(state: dict) -> dict:
    """Estimates carbon footprint (mock calculation)."""
    raw_text = state.get("raw_text", "")
    # Mock calc for demo
    footprint = raw_text.count("energy") * 10
    logger.info(f"Calculator estimated footprint={footprint}")
    return {"footprint": footprint, **state}

def advisor_agent(state: dict) -> dict:
    """LLM suggests improvements based on extracted data + footprint."""
    footprint = state.get("footprint", 0)
    raw_text = state.get("raw_text", "")
    goal = state.get("goal", "")

    prompt = f"""
    You are a sustainability advisor. A report was provided with footprint={footprint}.
    Goal: {goal}.
    Suggest 3-5 practical improvements (e.g., renewable %, offsetting, efficiency).
    """
    try:
        response = llm.invoke(prompt)
        suggestions = response.content
        logger.info("Advisor generated suggestions.")
        return {"suggestions": suggestions, **state}
    except Exception as e:
        logger.error(f"Advisor failed: {e}")
        raise BaseAIError("Advisor agent failed to generate suggestions.")

def writer_agent(state: dict) -> dict:
    """Writes the final NetZero roadmap."""
    suggestions = state.get("suggestions", "")
    goal = state.get("goal", "")
    if not suggestions:
        raise BaseAIError("No suggestions provided by advisor.")

    roadmap = f"## NetZero Roadmap for Goal: {goal}\n\n{suggestions}"
    logger.info("Writer generated roadmap.")
    return {"plan": roadmap, **state}
