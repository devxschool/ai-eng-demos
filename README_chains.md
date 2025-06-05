# LangChain Chains Examples

This collection demonstrates various types of LangChain chains and how to use them effectively.

## Files Overview

### Basic Chains
- **`chain_01_basic_llm_chain.py`** - Your first LLMChain with a simple prompt template
- **`chain_02_sequential_chain.py`** - Chaining multiple steps together (title → outline)
- **`chain_03_conversation_memory.py`** - Adding memory to maintain conversation context

### Advanced Chains  
- **`chain_04_rag_chain.py`** - Retrieval-Augmented Generation with vector store
- **`chain_05_router_chain.py`** - Branching logic that routes to different sub-chains
- **`chain_06_custom_chain.py`** - Creating your own custom chain class

### Testing
- **`chain_07_testing_chains.py`** - Unit testing chains with fake LLMs

## Prerequisites

```bash
# Install required packages
pip install langchain langchain-openai langchain-community

# For RAG example (optional)
pip install faiss-cpu

# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key_here
```

## Running the Examples

Each file can be run independently:

```bash
# Basic examples
python3 chain_01_basic_llm_chain.py
python3 chain_02_sequential_chain.py
python3 chain_03_conversation_memory.py

# Advanced examples
python3 chain_04_rag_chain.py
python3 chain_05_router_chain.py
python3 chain_06_custom_chain.py

# Testing example (no API key needed)
python3 chain_07_testing_chains.py
```

## What Each Example Teaches

### 1. Basic LLMChain (`chain_01_basic_llm_chain.py`)
- How to create a simple prompt template
- Basic LLMChain usage with `.run()`
- Single-step LLM interaction

### 2. Sequential Chain (`chain_02_sequential_chain.py`)
- Chaining multiple LLM calls together
- Using `output_key` to pass data between steps
- Setting `verbose=True` for debugging

### 3. Conversation Memory (`chain_03_conversation_memory.py`)
- Adding memory to maintain context
- ConversationBufferMemory usage
- Building chatbot-like interactions

### 4. RAG Chain (`chain_04_rag_chain.py`)
- Retrieval-Augmented Generation
- Vector store creation and querying
- Combining retrieval with generation

### 5. Router Chain (`chain_05_router_chain.py`)
- Conditional logic in chains
- Routing to different sub-chains based on input
- Specialized handling for different question types

### 6. Custom Chain (`chain_06_custom_chain.py`)
- Subclassing `BaseChain`
- Implementing `_call()` method
- Creating reusable custom logic

### 7. Testing Chains (`chain_07_testing_chains.py`)
- Using `FakeListLLM` for predictable testing
- Unit testing chain behavior
- Testing multiple scenarios

## Key Concepts

### Chain Types
- **LLMChain**: Single prompt + LLM call
- **SequentialChain**: Linear pipeline of multiple steps
- **ConversationChain**: Chatbot with memory
- **RetrievalChain**: RAG (retrieve → generate)
- **RouterChain**: Conditional branching
- **Custom Chain**: Your own logic

### Best Practices
1. **Use `verbose=True`** for debugging
2. **Test with fake LLMs** for unit tests
3. **Keep prompts external** for better version control
4. **Validate outputs** with structured parsing
5. **Monitor token usage** for cost control

### Common Patterns
```python
# Basic pattern
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run({"input": "value"})

# Sequential pattern
pipeline = SequentialChain(
    chains=[step1, step2],
    input_variables=["input"],
    output_variables=["output"]
)

# Memory pattern
chain = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory()
)
```

## Troubleshooting

### Common Issues
1. **Import errors**: Make sure you have the correct LangChain version
2. **API key errors**: Set `OPENAI_API_KEY` environment variable
3. **Module not found**: Install missing dependencies with pip

### Version Compatibility
These examples are designed for:
- `langchain >= 0.1.0`
- `langchain-openai >= 0.0.5` 
- `langchain-community >= 0.0.10`

### Dependencies
```bash
pip install langchain langchain-openai langchain-community faiss-cpu
```

## Next Steps

After running these examples, explore:
- **Agents** for more dynamic workflows
- **Tools** for external integrations  
- **Callbacks** for monitoring and logging
- **Streaming** for real-time responses
- **LangSmith** for production monitoring

## Resources

- [LangChain Documentation](https://python.langchain.com)
- [Chain Types Guide](https://python.langchain.com/docs/modules/chains/)
- [Best Practices](https://python.langchain.com/docs/guides/productionization/) 