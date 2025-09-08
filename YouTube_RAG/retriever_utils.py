import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from common.logger import get_logger
from common.exceptions import RAGException  # now exists

logger = get_logger(__name__)

def build_retriever(text: str, k: int = 3):
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(text)
        logger.info(f"Split transcript into {len(chunks)} chunks")

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        vectorstore = FAISS.from_texts(chunks, embeddings)
        logger.info("Created FAISS vectorstore")

        return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})
    except Exception as e:
        logger.error(f"Retriever build failed: {e}")
        raise RAGException("Could not build retriever from transcript.")
