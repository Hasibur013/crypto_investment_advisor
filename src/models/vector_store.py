# src/models/vector_store.py
import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .embeddings import get_embedding_model


def build_vector_store_from_docs(doc_paths):
    """
    Builds a FAISS vector store from a list of text file paths.

    Args:
        doc_paths (List[str]): Paths to documents (e.g., blog text files)

    Returns:
        FAISS vector store object
    """
    documents = []

    for path in doc_paths:
        if not os.path.exists(path):
            print(f"❌ File not found: {path}")
            continue

        try:
            loader = TextLoader(path)
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"⚠️ Failed to load {path}: {e}")

    if not documents:
        raise ValueError("No valid documents found to build vector store.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Document splitting failed. No chunks created.")

    embeddings = get_embedding_model()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    return vectorstore
