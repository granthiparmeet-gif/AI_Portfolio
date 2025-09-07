import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from common.logger import get_logger
from common.exceptions import OpenAIError  # <-- ensure this import

logger = get_logger(__name__)

_RAG_PROMPT = ChatPromptTemplate.from_template(
    "You are an assistant for question-answering tasks.\n"
    "Use the following pieces of retrieved context to answer the question.\n"
    "If you don't know the answer, just say you don't know.\n"
    "Keep the answer concise.\n\n"
    "Question: {input}\n"
    "Context:\n{context}\n\n"
    "Answer:"
)

def get_answer(question: str, retriever):
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        doc_chain = create_stuff_documents_chain(llm, _RAG_PROMPT)
        rag_chain = create_retrieval_chain(retriever, doc_chain)
        result = rag_chain.invoke({"input": question})
        logger.info(f"Answered: {question[:60]} -> {result.get('answer','')[:60]}")
        return result
    except Exception as e:
        logger.error(f"OpenAI/LangChain failed: {e}")
        raise OpenAIError("Something went wrong generating the answer.")