import json
import os
from pathlib import Path
from typing import List

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SOURCE_CANDIDATES = ["Gurbani.txt", "gurbani.txt"]
INDEX_PATH = DATA_DIR / "index.faiss"
CHUNKS_PATH = DATA_DIR / "chunks.json"


def load_source_text() -> str:
    for name in SOURCE_CANDIDATES:
        candidate = DATA_DIR / name
        if candidate.exists():
            content = candidate.read_text(encoding="utf-8").strip()
            if content:
                return content

    raise SystemExit(
        "No OCR source found. Place Gurbani.txt (or gurbani.txt) in the data directory."
    )


def chunk_text(text: str, chunk_size: int = 150, overlap: int = 50) -> List[str]:
    words = text.replace("\n", " ").split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        if end == len(words):
            break
        start += step
    return chunks


def embed_texts(client: OpenAI, texts: List[str], model: str) -> np.ndarray:
    embeddings: list[np.ndarray] = []
    for text in texts:
        resp = client.embeddings.create(model=model, input=text)
        embedding = np.array(resp.data[0].embedding, dtype="float32")
        embeddings.append(embedding)
    matrix = np.vstack(embeddings)
    faiss.normalize_L2(matrix)
    return matrix


def build_index() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required in .env")

    raw = load_source_text()
    chunks = chunk_text(raw)

    if not chunks:
        raise SystemExit("No text to index; check Gurbani.txt before building.")

    print(f"Preparing {len(chunks)} chunks for indexing.")

    client = OpenAI(api_key=api_key)
    matrix = embed_texts(client, chunks, "text-embedding-3-large")

    dim = matrix.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(matrix)
    faiss.write_index(index, INDEX_PATH.as_posix())

    chunk_payload = [
        {"id": idx, "text": chunk}
        for idx, chunk in enumerate(chunks, start=1)
    ]
    CHUNKS_PATH.write_text(json.dumps(chunk_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Index built with", len(chunks), "chunks.")


def main() -> None:
    build_index()


if __name__ == "__main__":
    main()
