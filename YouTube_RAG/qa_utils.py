import os
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from common.logger import get_logger
from common.exceptions import OpenAIError

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
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": _RAG_PROMPT},
            return_source_documents=True,
        )
        result = rag_chain({"query": question})
        logger.info(f"Answered: {question[:60]} -> {result.get('result','')[:60]}")
        return {
            "answer": result.get("result", ""),
            "context": result.get("source_documents", []),
        }
    except Exception as e:
        logger.error(f"OpenAI/LangChain failed: {e}")
        raise OpenAIError("Something went wrong generating the answer.")
