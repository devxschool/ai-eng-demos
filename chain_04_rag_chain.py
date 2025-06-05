"""
Example 4: Retrieval-Augmented Generation Chain
Demonstrates how to create a RAG chain using modern LangChain LCEL syntax.
Note: Requires langchain-community and faiss-cpu packages.
"""

import os
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate

# Initialize the LLM
llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)

# Create a sample text file if it doesn't exist
sample_text = """
LangChain is a framework for developing applications powered by language models.
It provides tools for chaining together different components like LLMs, prompts, and data sources.
The main benefits of LangChain include modularity, composability, and ease of use.
Common use cases include chatbots, question-answering systems, and content generation.
LangChain supports various memory types for maintaining conversation context.
Agents in LangChain can use tools to interact with external systems.
Prompt templates help standardize and reuse prompts across applications.
Chains allow you to combine multiple steps into reusable workflows.
The framework supports both synchronous and asynchronous operations.
"""

if not os.path.exists("example.txt"):
    with open("example.txt", "w") as f:
        f.write(sample_text)
    print("Created example.txt with sample content")

def create_simple_rag_chain(retriever, llm):
    """Create a simple RAG chain using modern LCEL syntax."""
    
    # Create a prompt template for RAG
    rag_prompt = PromptTemplate.from_template("""
    You are an assistant for question-answering tasks. Use the following pieces of 
    retrieved context to answer the question. If you don't know the answer, say that 
    you don't know. Use three sentences maximum and keep the answer concise.

    Context:
    {context}

    Question: {question}

    Answer:""")
    
    # Create the chain using LCEL syntax (prompt | llm)
    qa_chain = rag_prompt | llm
    
    def rag_function(query_dict):
        """RAG function that retrieves and generates."""
        question = query_dict["input"]
        
        # Retrieve relevant documents using modern invoke method
        docs = retriever.invoke(question)
        
        # Combine document content
        context = "\n".join([doc.page_content for doc in docs])
        
        # Generate answer using LCEL syntax
        answer = qa_chain.invoke({
            "context": context,
            "question": question
        })
        
        return {
            "answer": answer,
            "context": docs,
            "source_documents": docs  # For compatibility
        }
    
    return rag_function

try:
    print("=== RAG Chain Example ===")
    
    # Build a tiny vector store
    docs = TextLoader("example.txt").load()
    store = FAISS.from_documents(docs, OpenAIEmbeddings())
    
    # Create the simple RAG chain
    rag_chain = create_simple_rag_chain(store.as_retriever(), llm)
    
    # Test questions
    test_questions = [
        "What is LangChain?",
        "What are the main benefits of LangChain?", 
        "How does LangChain help with memory?",
        "What is quantum computing?"  # This should show it doesn't know
    ]
    
    for question in test_questions:
        print(f"\n=== Question: {question} ===")
        
        # Query the chain
        response = rag_chain({"input": question})
        
        print("Answer:", response["answer"])
        print("\nSource documents:")
        for i, doc in enumerate(response["context"]):
            print(f"  {i+1}. {doc.page_content[:100]}...")
        print("-" * 50)

except ImportError as e:
    print(f"Import Error: {e}")
    print("\nTo fix this, install the required packages:")
    print("  pip install langchain-community faiss-cpu")
    print("\nOr use the simplified version:")
    print("  python3 chain_04_rag_chain_simple.py")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e).__name__}")
    print("\nTroubleshooting:")
    print("1. Make sure you have installed: pip install langchain-community faiss-cpu")
    print("2. Verify your OpenAI API key is set: export OPENAI_API_KEY=your_key")
    print("3. Try the simplified version: python3 chain_04_rag_chain_simple.py") 