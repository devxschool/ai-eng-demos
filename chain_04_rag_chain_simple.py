"""
Example 4: Simple RAG Chain (without langchain_community)
Demonstrates basic retrieval-augmented generation using simple text similarity.
This version works without additional dependencies.
"""

import os
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize the LLM
llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)

# Sample knowledge base
knowledge_base = [
    "LangChain is a framework for developing applications powered by language models.",
    "It provides tools for chaining together different components like LLMs, prompts, and data sources.",
    "The main benefits of LangChain include modularity, composability, and ease of use.",
    "Common use cases include chatbots, question-answering systems, and content generation.",
    "LangChain supports various memory types for maintaining conversation context.",
    "Agents in LangChain can use tools to interact with external systems.",
    "Prompt templates help standardize and reuse prompts across applications."
]

def simple_retrieval(query, documents, top_k=2):
    """Simple keyword-based retrieval without vector embeddings."""
    query_words = set(query.lower().split())
    
    # Score documents based on keyword overlap
    scored_docs = []
    for doc in documents:
        doc_words = set(doc.lower().split())
        overlap = len(query_words.intersection(doc_words))
        scored_docs.append((overlap, doc))
    
    # Return top_k documents sorted by score
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:top_k] if score > 0]

# Create a RAG prompt template
rag_prompt = PromptTemplate.from_template("""
Use the following context to answer the question. If the context doesn't contain 
relevant information, say so.

Context:
{context}

Question: {question}

Answer:""")

# Create the RAG chain
rag_chain = LLMChain(llm=llm, prompt=rag_prompt)

def ask_question(question):
    """Ask a question using simple RAG."""
    print(f"\n=== Question: {question} ===")
    
    # Retrieve relevant documents
    relevant_docs = simple_retrieval(question, knowledge_base)
    
    if not relevant_docs:
        context = "No relevant information found in the knowledge base."
    else:
        context = "\n".join(f"- {doc}" for doc in relevant_docs)
    
    print("Retrieved context:")
    print(context)
    
    # Generate answer using LLM
    response = rag_chain.run({
        "context": context,
        "question": question
    })
    
    print(f"\nAnswer: {response}")
    return response

# Test the simple RAG system
print("=== Simple RAG Chain Example ===")

# Test questions
test_questions = [
    "What is LangChain?",
    "What are the benefits of using LangChain?",
    "How can I use LangChain for chatbots?",
    "What is quantum computing?"  # This should show no relevant context
]

for question in test_questions:
    ask_question(question)
    print("-" * 50) 