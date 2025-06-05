"""
Example 5: Branching Logic with a Router Chain
Demonstrates how to route questions to different specialized chains.
"""

from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

# Initialize the LLM
llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)

print("=== Router Chain Example ===")

def create_simple_router(llm):
    """Create a simple router using modern LCEL syntax."""
    
    # Router prompt to classify questions
    router_prompt = PromptTemplate.from_template("""
    You are a question classifier. Given a question, classify it as either "math" or "general".
    
    Classification rules:
    - "math": Questions involving numbers, calculations, equations, or mathematical operations
    - "general": All other questions including weather, advice, facts, etc.
    
    Question: {question}
    
    Classification (respond with only "math" or "general"):""")
    
    # Math solver prompt
    math_prompt = PromptTemplate.from_template("""
    Solve this math problem step by step. Show your work clearly.
    
    Problem: {question}
    
    Solution:""")
    
    # General assistant prompt  
    general_prompt = PromptTemplate.from_template("""
    Answer this question kindly and helpfully. Be informative and friendly.
    
    Question: {question}
    
    Answer:""")
    
    # Create chains using LCEL syntax
    router_chain = router_prompt | llm
    math_chain = math_prompt | llm
    general_chain = general_prompt | llm
    
    def route_question(query_dict):
        """Route the question to appropriate chain."""
        question = query_dict["question"]
        
        # Step 1: Classify the question
        classification = router_chain.invoke({"question": question}).strip().lower()
        print(f"🤖 Classification: {classification}")
        
        # Step 2: Route to appropriate chain
        if "math" in classification:
            print("📊 Routing to math chain...")
            result = math_chain.invoke({"question": question})
        else:
            print("💬 Routing to general chain...")
            result = general_chain.invoke({"question": question})
        
        return result
    
    return route_question

def create_legacy_router_chain(llm):
    """Alternative approach for router chains with explicit prompts."""
    try:
        from langchain.chains.router import MultiRouteChain, LLMRouterChain
        from langchain.chains.router.llm_router import RouterOutputParser
        from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
        
        # Define destinations with prompts
        destinations = {
            "math": {
                "description": "Good for mathematical calculations and solving equations",
                "prompt_template": "Solve this math problem step by step: {input}"
            },
            "general": {
                "description": "Good for general questions and conversations", 
                "prompt_template": "Answer this question helpfully: {input}"
            }
        }
        
        # Create router prompt
        router_prompt = PromptTemplate(
            template=MULTI_PROMPT_ROUTER_TEMPLATE,
            input_variables=["input"],
            output_parser=RouterOutputParser(),
        )
        
        # Create router chain
        router_chain = LLMRouterChain.from_llm(llm, router_prompt)
        
        # Create destination chains
        from langchain.chains import LLMChain
        destination_chains = {}
        for name, config in destinations.items():
            prompt = PromptTemplate.from_template(config["prompt_template"])
            chain = LLMChain(llm=llm, prompt=prompt)
            destination_chains[name] = chain
        
        # Create multi-route chain
        multi_chain = MultiRouteChain(
            router_chain=router_chain,
            destination_chains=destination_chains,
            default_chain=destination_chains["general"]
        )
        
        return multi_chain
        
    except Exception as e:
        print(f"Legacy router creation failed: {e}")
        return None

# Try both approaches
print("\n=== Approach 1: Simple Modern Router ===")

try:
    # Create simple router
    simple_router = create_simple_router(llm)
    
    # Test questions
    test_questions = [
        "What is 29*17?",
        "Calculate the area of a circle with radius 5",
        "What's the weather like?", 
        "Tell me about artificial intelligence"
    ]
    
    for question in test_questions:
        print(f"\n--- Question: {question} ---")
        result = simple_router({"question": question})
        print(f"Answer: {result}")
        print("-" * 40)

except Exception as e:
    print(f"Simple router error: {e}")

print("\n=== Approach 2: Legacy Router Chain ===")

try:
    # Try legacy router chain
    legacy_router = create_legacy_router_chain(llm)
    
    if legacy_router:
        print("Testing legacy router...")
        math_result = legacy_router.run({"input": "What is 15 + 27?"})
        print(f"Math result: {math_result}")
        
        general_result = legacy_router.run({"input": "What is the capital of France?"})
        print(f"General result: {general_result}")
    else:
        print("Legacy router not available - using simple router only")

except Exception as e:
    print(f"Legacy router error: {e}")
    print("This is expected - legacy router chains have complex dependencies")

print("\n✅ Router chain examples completed!") 