import os
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from common.logger import get_logger
from common.exceptions import OpenAIError

try:  # RetrievalQA only exists in newer releases
    from langchain.chains import RetrievalQA
except ImportError:
    RetrievalQA = None
    create_stuff_documents_chain = None
    create_retrieval_chain = None

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
        if RetrievalQA is not None:
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
        if create_stuff_documents_chain is not None and create_retrieval_chain is not None:
            doc_chain = create_stuff_documents_chain(llm, _RAG_PROMPT)
            rag_chain = create_retrieval_chain(retriever, doc_chain)
            result = rag_chain.invoke({"input": question})
            logger.info(f"Answered: {question[:60]} -> {result.get('answer','')[:60]}")
            return {"answer": result.get("answer", ""), "context": result.get("context", [])}
        docs = retriever.get_relevant_documents(question)
        context_str = "\n\n".join(doc.page_content or "" for doc in docs)
        prompt = _RAG_PROMPT.format_prompt(input=question, context=context_str)
        response = llm(messages=prompt.to_messages())
        answer = response.generations[0][0].text.strip()
        logger.info(f"Answered (manual): {question[:60]} -> {answer[:60]}")
        return {"answer": answer, "context": docs}
    except Exception as e:
        logger.error(f"OpenAI/LangChain failed: {e}")
        raise OpenAIError("Something went wrong generating the answer.")
