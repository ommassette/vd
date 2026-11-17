import concurrent.futures
import hashlib
import logging
import os
import queue
import re
import threading
from functools import lru_cache
from pathlib import Path
from typing import Iterator, List

import chromadb
import ollama
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text-v2-moe")

KEEP_ALIVE = "5m"       # reduced to free RAM faster on 4GB VPS
NUM_CTX = 1536          # optimized down from 3072 for faster CPU prompt processing
EMBED_BATCH = 32        # chunks per embedding request
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
TOP_K = 4
MIN_SIMILARITY = float(os.environ.get("MIN_SIMILARITY", "0.25"))

# nomic embedding models expect these prefixes
DOC_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "

# Graph is opt-in: it runs the chat model in the background and slows everything else.
ENABLE_GRAPH = os.environ.get("ENABLE_GRAPH", "0") == "1"
GRAPH_MAX_CHUNKS = 15

CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", "rag_data/chroma")
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection_research = chroma_client.get_or_create_collection(
    name="valgus_services_rag",
    metadata={"hnsw:space": "cosine"},
)

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "neo4j123")

NO_ANSWER = "I don't know based on the provided services documents."
SYSTEM_PROMPT = (
    "Answer the question using only the context provided. Be concise. "
    f'If the context does not contain the answer, reply exactly: "{NO_ANSWER}"'
)

STOPWORDS = {
    "what", "which", "when", "where", "who", "whom", "whose", "this", "that",
    "these", "those", "with", "from", "have", "does", "about", "your", "there",
    "their", "will", "would", "could", "should", "into", "than", "then", "them",
    "they", "been", "being", "some", "tell", "give", "please", "much", "many",
}


# ----------------------------------------------------------------------------
# Text + embeddings
# ----------------------------------------------------------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"-\n(\w)", r"\1", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = text.replace("•", "\n- ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def embed_texts(texts: List[str], prefix: str) -> List[List[float]]:
    out: List[List[float]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        batch = [prefix + t for t in texts[i:i + EMBED_BATCH]]
        resp = ollama.embed(model=EMBED_MODEL, input=batch, keep_alive=KEEP_ALIVE, options={"timeout": 120.0})
        out.extend(resp.embeddings)
    return out


@lru_cache(maxsize=256)
def embed_query(query: str) -> tuple:
    return tuple(embed_texts([query], QUERY_PREFIX)[0])


# ----------------------------------------------------------------------------
# Neo4j
# ----------------------------------------------------------------------------
_graph = None
_graph_lock = threading.Lock()


def get_graph() -> Neo4jGraph:
    global _graph
    with _graph_lock:
        if _graph is None:
            _graph = Neo4jGraph(
                url=NEO4J_URI,
                username=NEO4J_USER,
                password=NEO4J_PASSWORD,
                refresh_schema=False,
            )
        return _graph


_graph_queue: "queue.Queue[List[Document]]" = queue.Queue()


def _graph_worker() -> None:
    transformer = LLMGraphTransformer(
        llm=ChatOllama(model=MODEL, temperature=0, keep_alive=KEEP_ALIVE)
    )
    while True:
        docs = _graph_queue.get()
        try:
            graph_docs = transformer.convert_to_graph_documents(docs)
            get_graph().add_graph_documents(
                graph_docs, baseEntityLabel=True, include_source=True
            )
        except Exception:
            logger.exception("Neo4j graph extraction failed")
        finally:
            _graph_queue.task_done()


if ENABLE_GRAPH:
    threading.Thread(target=_graph_worker, daemon=True).start()


# ----------------------------------------------------------------------------
# Ingestion
# ----------------------------------------------------------------------------
def _upsert(ids, documents, metadatas, embeddings, batch: int = 500) -> None:
    for i in range(0, len(ids), batch):
        s = slice(i, i + batch)
        collection_research.upsert(
            ids=ids[s], documents=documents[s],
            metadatas=metadatas[s], embeddings=embeddings[s],
        )


def process_and_ingest_document(file_path: str) -> None:
    path = Path(file_path)
    if not path.exists():
        logger.error("File not found: %s", file_path)
        return

    source = str(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    existing = collection_research.get(where={"source": source}, limit=1, include=["metadatas"])
    if existing["ids"]:
        if (existing["metadatas"][0] or {}).get("file_hash") == digest:
            logger.info("Unchanged, skipping: %s", file_path)
            return
        delete_document_from_vector_db(file_path)

    loader = PyPDFLoader(source) if path.suffix.lower() == ".pdf" else TextLoader(source, encoding="utf-8")
    pages = loader.load()
    for page in pages:
        page.page_content = clean_text(page.page_content)
    pages = [p for p in pages if p.page_content]
    if not pages:
        logger.warning("No extractable text in %s", file_path)
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = [c for c in splitter.split_documents(pages) if len(c.page_content) >= 40]
    if not chunks:
        return

    texts = [c.page_content for c in chunks]
    embeddings = embed_texts([f"{path.stem}\n{t}" for t in texts], DOC_PREFIX)

    ids = [f"{digest[:12]}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": source,
            "file_name": path.name,
            "page": int(c.metadata.get("page", 0)),
            "file_hash": digest,
        }
        for c in chunks
    ]
    _upsert(ids, texts, metadatas, embeddings)

    if ENABLE_GRAPH:
        step = max(1, len(texts) // GRAPH_MAX_CHUNKS)
        sample = texts[::step][:GRAPH_MAX_CHUNKS]
        _graph_queue.put([Document(page_content=t, metadata={"source": source}) for t in sample])


def delete_document_from_vector_db(file_path: str) -> None:
    results = collection_research.get(where={"source": str(Path(file_path))})
    if results and results["ids"]:
        collection_research.delete(ids=results["ids"])


# ----------------------------------------------------------------------------
# Retrieval
# ----------------------------------------------------------------------------
def fast_graph_retrieve(query: str) -> List[str]:
    keywords = list(dict.fromkeys(
        w.lower() for w in re.findall(r"\w+", query)
        if len(w) > 3 and w.lower() not in STOPWORDS
    ))[:5]
    if not keywords:
        return []
    try:
        rows = get_graph().query(
            """
            MATCH (n:__Entity__)-[r]-(m:__Entity__)
            WHERE any(kw IN $keywords WHERE toLower(n.id) CONTAINS kw)
            RETURN n.id AS entity, type(r) AS relation, m.id AS related
            LIMIT 8
            """,
            {"keywords": keywords},
        )
    except Exception as e:
        logger.warning("Neo4j query skipped: %s", e)
        return []
    return [f"{r['entity']} -{r['relation']}-> {r['related']}" for r in rows]


def _label(meta: dict) -> str:
    name = meta.get("file_name", "unknown")
    if name.lower().endswith(".pdf"):
        return f"{name}, p.{int(meta.get('page', 0)) + 1}"
    return name


def hybrid_retrieve(query: str, k: int = TOP_K, min_similarity: float = MIN_SIMILARITY) -> str:
    query_embedding = list(embed_query(query))

    graph_future = None
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        if ENABLE_GRAPH:
            graph_future = executor.submit(fast_graph_retrieve, query)
        response = collection_research.query(
            n_results=k,
            query_embeddings=[query_embedding],
            include=["documents", "distances", "metadatas"],
        )
        graph_facts = graph_future.result() if graph_future else []

    documents = response.get("documents", [[]])[0]
    distances = response.get("distances", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]

    passages = [
        f"[{_label(meta)}]\n{doc}"
        for doc, dist, meta in zip(documents, distances, metadatas)
        if (1.0 - dist) >= min_similarity
    ]

    sections = []
    if passages:
        sections.append("Text passages:\n" + "\n\n---\n\n".join(passages))
    if graph_facts:
        sections.append("Graph facts:\n" + "\n".join(graph_facts))
    return "\n\n".join(sections)


# ----------------------------------------------------------------------------
# Generation
# ----------------------------------------------------------------------------
def warm_up() -> None:
    ollama.embed(model=EMBED_MODEL, input="warm up", keep_alive=KEEP_ALIVE, options={"timeout": 120.0})
    ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": "hi"}],
        options={"num_predict": 1, "num_ctx": NUM_CTX, "timeout": 120.0},
        keep_alive=KEEP_ALIVE,
    )


def stream_chatbot_response(question: str) -> Iterator[str]:
    context = hybrid_retrieve(question)
    if not context:
        yield NO_ANSWER
        return

    stream = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        options={"temperature": 0, "num_predict": 256, "num_ctx": NUM_CTX},
        keep_alive=KEEP_ALIVE,
        stream=True,
    )
    for part in stream:
        if part.message.content:
            yield part.message.content


def generate_chatbot_response(question: str) -> str:
    return "".join(stream_chatbot_response(question))