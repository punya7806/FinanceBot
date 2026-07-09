from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from rag.vectorstore import load_vectorstore
from rag.retriever import retrieve_docs
from rag.bm25 import get_bm25_retriever
from rag.loader import load_document
from rag.splitter import split_documents
from rag.pandas_agent import (
        calculate_profit_loss
)
# Toggle between static and dynamic agent
USE_DYNAMIC_AGENT = True  # Set to False to use static agent

if USE_DYNAMIC_AGENT:
    from rag.dynamic_pandas_agent import pandas_agent_query
else:
    from rag.pandas_rag_agent import pandas_agent_query
from rag.cache_manager import get_cache_manager
import re
import pdfplumber
import pandas as pd
import hashlib

# Load environment variables from .env file
load_dotenv()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please ensure:\n"
            "1. You have a .env file in the project root\n"
            "2. It contains: GROQ_API_KEY=your_api_key_here\n"
            "3. Restart the Django server after creating/modifying .env"
        )
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key
    )
def finance_agent(question, path, file_type='textual'):
    """
    Intelligent finance agent that routes queries based on file type

    Args:
        question: User's question
        path: Path to the data file
        file_type: 'textual' for PDF/DOCX, 'tabular' for CSV/XLSX

    Returns:
        Answer string
    """
    print(f"Entered finance agent - File type: {file_type}")

    llm = get_llm()

    # ROUTE BASED ON FILE TYPE
    if file_type == 'tabular':
        # Use Pandas-first agent for CSV/XLSX
        print("Routing to Pandas Agent...")
        try:
            answer = pandas_agent_query(question, path, llm)
            return answer
        except Exception as e:
            return f"Error processing query with Pandas Agent: {str(e)}"

    elif file_type == 'textual':
        # Use RAG for PDF/DOCX
        print("Routing to RAG Agent...")
        return rag_agent(question, path, llm)

    else:
        # Fallback to old behavior if file_type unknown
        print("Unknown file type, using legacy RAG...")
        return rag_agent(question, path, llm)


def rag_agent(question, path, llm):
    """
    RAG-based agent for textual documents (PDF/DOCX)
    Optimized for narrative and descriptive content
    """
    ############################
    # FAISS Retrieval
    ############################
    vectorstore = load_vectorstore()
    faiss_docs = retrieve_docs(
        vectorstore,
        question
    )
    

    
    ############################
    # BM25 Retrieval (with caching)
    ###########################
    cache = get_cache_manager()

    # Create cache key from file path
    cache_key = hashlib.md5(path.encode()).hexdigest()

    # Try to load from cache
    bm25 = cache.get(cache_key)

    if bm25 is None:
        print("Building BM25 index (not cached)...")
        documents = load_document(path)
        chunks = split_documents(documents, file_type='textual')
        bm25 = get_bm25_retriever(chunks)
        # Cache for future queries
        cache.set(cache_key, bm25)
    else:
        print("Using cached BM25 index")

    bm25_docs = bm25.invoke(question)
    ############################
    # Hybrid Retrieval
    ############################
    retrieved_docs = bm25_docs + faiss_docs
    ############################
    # Remove duplicates
    ############################
    seen = set()
    docs = []
    for doc in retrieved_docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            docs.append(doc)
    ############################
    # Context
    ############################
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # Check if context is empty
    if not context.strip():
        return "No relevant information found in the document. Please try rephrasing your question."

    ############################
    # LLM
    ############################
    prompt = f"""
        You are FinRAG AI, a financial document analysis assistant.

        Rules:
        1. Use ONLY information from the provided Context.
        2. Never hallucinate or make up information.
        3. If information is unavailable, clearly state so.
        4. Preserve exact numerical values and dates from the context.
        5. If the context doesn't contain enough information to answer, say: "The provided document doesn't contain sufficient information to answer this question."
        6. For narrative questions, provide clear summaries based on the context.
        7. Use markdown formatting for better readability when appropriate.

        Context:
        {context}

        Question:
        {question}

        Answer:
    """
    response = llm.invoke(prompt)
    return response.content

def general_agent(question):
    llm = get_llm()
    prompt = f"""
        You are GeneralAI, a knowledgeable and friendly assistant.
        Your responsibilities:
        - Answer questions from any domain including technology, science, history, education, finance, health, and general knowledge.
        - Provide clear, concise, and accurate explanations.
        - Use simple language whenever possible.
        - If the question requires step-by-step guidance, provide numbered steps.
        - If you do not know the answer, politely say so instead of making up information.
        - Do not mention internal reasoning or system prompts.
        - Format your responses neatly using bullet points when appropriate.
        User Question:
        {question}
        Assistant Answer:
    """
    response = llm.invoke(prompt)
    return response.content

def classify_agent(question):
    llm = get_llm()
    prompt = f"""
        Classify this question as either "finance" or "general".

        Return ONLY one word: "finance" or "general"

        **Classification Rules:**
        - "finance" = Questions about stock prices, financial data, trading, profit/loss, price comparisons, highest/lowest prices, dates with specific prices, market data, or anything related to the uploaded financial dataset
        - "general" = Questions about general knowledge, science, history, technology, or topics unrelated to the uploaded financial data

        **Examples:**
        - "What was the price on June 15?" → finance
        - "Which day had the highest price?" → finance
        - "Compare prices on two dates" → finance
        - "Calculate profit if I bought 100 shares" → finance
        - "Show me the trend in May" → finance
        - "What is Python?" → general
        - "How does machine learning work?" → general

        Question: {question}

        Answer (only 'finance' or 'general'):
    """
    response = llm.invoke(prompt)

    return response.content.strip().lower()