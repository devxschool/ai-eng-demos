"""
Example 6: Rolling Your Own Custom Chain
Demonstrates both legacy and modern approaches to creating custom chains.
"""

from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from typing import Dict, Any, List, ClassVar
import functools

# Initialize the LLM
llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)

print("=== Custom Chain Example ===")

# ============================================================================
# Approach 1: Modern LCEL-based Custom Chain (Recommended)
# ============================================================================

def create_summarize_and_translate_chain(llm):
    """Create a custom chain using modern LCEL syntax."""
    
    # Create prompt templates
    summarize_prompt = PromptTemplate.from_template(
        "Summarize the following text in exactly one clear sentence:\n\n{text}"
    )
    
    translate_prompt = PromptTemplate.from_template(
        "Translate the following text to {language}:\n\n{summary}"
    )
    
    # Create individual chains
    summarize_chain = summarize_prompt | llm
    translate_chain = translate_prompt | llm
    
    def process(inputs: Dict[str, Any]) -> Dict[str, str]:
        """Process the input through summarize then translate."""
        text = inputs["text"]
        language = inputs["language"]
        
        print(f"📝 Summarizing text...")
        # Step 1: Summarize
        summary = summarize_chain.invoke({"text": text}).strip()
        print(f"Summary: {summary}")
        
        print(f"🌍 Translating to {language}...")
        # Step 2: Translate
        translation = translate_chain.invoke({
            "summary": summary, 
            "language": language
        }).strip()
        
        return {"translation": translation, "summary": summary}
    
    return process

# ============================================================================
# Approach 2: Fixed Legacy BaseChain (For Reference)
# ============================================================================

try:
    from langchain.chains.base import Chain
    
    class SummarizeAndTranslate(Chain):
        """Custom chain that summarizes text and then translates it."""
        
        # Fix: Use ClassVar to avoid Pydantic field validation
        input_keys: ClassVar[List[str]] = ["text", "language"]
        output_keys: ClassVar[List[str]] = ["translation"]

        def _call(self, inputs: Dict[str, Any], run_manager=None) -> Dict[str, str]:
            """Execute the chain logic."""
            
            # Step 1: Summarize the text
            summary_prompt = f"Summarize in 1 sentence:\n\n{inputs['text']}"
            summary = llm.invoke(summary_prompt).strip()
            
            print(f"Summary: {summary}")
            
            # Step 2: Translate the summary
            translate_prompt = f"Translate to {inputs['language']}:\n\n{summary}"
            translation = llm.invoke(translate_prompt).strip()
            
            return {"translation": translation}

        @property
        def _chain_type(self) -> str:
            return "summarize_and_translate"

    legacy_chain_available = True
    
except Exception as e:
    print(f"⚠️  Legacy BaseChain approach failed: {e}")
    legacy_chain_available = False

# ============================================================================
# Test Both Approaches
# ============================================================================

sample_text = """
LangChain is a powerful framework that enables developers to build applications 
powered by large language models. It provides a standardized interface for chains, 
agents, and memory components. The framework makes it easy to combine different 
tools and create complex workflows. With LangChain, you can build chatbots, 
question-answering systems, content generators, and much more. The modular 
design allows for easy customization and extension of functionality.
"""

print("\n=== Approach 1: Modern LCEL Custom Chain ===")

try:
    # Create and test modern chain
    modern_chain = create_summarize_and_translate_chain(llm)
    
    result = modern_chain({
        "text": sample_text, 
        "language": "Spanish"
    })
    
    print(f"\nFinal Translation: {result['translation']}")
    
    # Test with different language
    print("\n--- Testing with French ---")
    result_french = modern_chain({
        "text": "LangChain lets you build amazing AI applications with ease.", 
        "language": "French"
    })
    
    print(f"French Translation: {result_french['translation']}")

except Exception as e:
    print(f"Modern chain error: {e}")

print("\n=== Approach 2: Legacy BaseChain (Fixed) ===")

if legacy_chain_available:
    try:
        # Test legacy chain
        legacy_chain = SummarizeAndTranslate()
        
        result = legacy_chain.invoke({
            "text": sample_text, 
            "language": "German"
        })
        
        print(f"German Translation: {result['translation']}")
        
    except Exception as e:
        print(f"Legacy chain error: {e}")
else:
    print("Legacy BaseChain not available - this is expected in newer LangChain versions")

# ============================================================================
# Approach 3: Simple Function-based Chain (Ultra Simple)
# ============================================================================

print("\n=== Approach 3: Simple Function Chain ===")

def simple_summarize_and_translate(text: str, language: str) -> str:
    """Ultra-simple custom chain as a plain function."""
    
    # Step 1: Summarize
    summary_result = llm.invoke(f"Summarize in 1 sentence:\n\n{text}")
    print(f"Summary: {summary_result}")
    
    # Step 2: Translate  
    translation_result = llm.invoke(f"Translate to {language}:\n\n{summary_result}")
    
    return translation_result

try:
    simple_result = simple_summarize_and_translate(
        "Python is a versatile programming language used for web development, data science, and AI.",
        "Italian"
    )
    print(f"Italian Translation: {simple_result}")
    
except Exception as e:
    print(f"Simple function error: {e}")

print("\n✅ Custom chain examples completed!")
print("\n💡 Recommendation: Use Approach 1 (Modern LCEL) for new projects!") 