import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from common.logger import get_logger
from common.exceptions import OpenAIError

logger = get_logger(__name__)

_CONTRACT_PROMPT = ChatPromptTemplate.from_template(
    "You are a contract analysis assistant.\n"
    "Context: {context}\n\n"
    "Question: {question}\n"
    "Answer clearly, but if unsure, say 'Not specified in this contract.'"
)

def get_contract_answer(text: str, question: str) -> str:
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        prompt = _CONTRACT_PROMPT.format(context=text[:4000], question=question)
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)
        logger.info(f"Q: {question[:60]} -> A: {answer[:60]}")
        return answer
    except Exception as e:
        logger.error(f"OpenAI contract QA failed: {e}")
        raise OpenAIError("LLM failed during contract analysis.")
