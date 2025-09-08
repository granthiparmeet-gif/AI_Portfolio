import os
from openai import OpenAI
from common.logger import get_logger
from common.exceptions import BaseAIError

logger = get_logger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_research(query: str) -> str:
    """
    Basic research flow:
    - Calls OpenAI model to answer the query
    - In future, could extend with MCP tools or multi-agent workflows
    """
    try:
        logger.info(f"Running research for query: {query}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": query},
            ],
            temperature=0.3,
        )
        answer = response.choices[0].message.content
        logger.info(f"Research result: {answer[:60]}...")
        return answer
    except Exception as e:
        logger.error(f"Research agent failed: {e}")
        raise BaseAIError("Research agent failed to generate a response.")