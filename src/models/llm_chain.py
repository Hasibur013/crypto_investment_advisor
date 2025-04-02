# src/models/llm_chain.py
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
import os

def get_llm_chain(vectorstore):
    llm = ChatGroq(
        temperature=0.5,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"  # or try "llama3-8b-8192"
    )
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
    return qa_chain


