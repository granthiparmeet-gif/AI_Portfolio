import os
from typing import List
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from common.logger import get_logger
from common.exceptions import RAGException, DataProcessingError

logger = get_logger(__name__)

def load_pdf_text(file_bytes) -> str:
    try:
        reader = PdfReader(file_bytes)
        pages = [p.extract_text() or "" for p in reader.pages]
        text = "\n\n".join(p.strip() for p in pages if p)
        logger.info(f"Extracted ~{len(text)} chars from PDF")
        return text
    except Exception as e:
        logger.error(f"PDF parse failed: {e}")
        raise DataProcessingError("Could not read the PDF. Please upload a valid report.")

def build_retriever_from_text(text: str):
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
        chunks = splitter.split_text(text or "")
        docs = [Document(page_content=c) for c in chunks]
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
        vs = FAISS.from_documents(docs, embeddings)
        logger.info(f"Built retriever with {len(docs)} chunks")
        return vs.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    except Exception as e:
        logger.error(f"Retriever build failed: {e}")
        raise RAGException("Failed to build retriever over the PDF.")