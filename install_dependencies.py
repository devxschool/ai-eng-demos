#!/usr/bin/env python3
"""
Installation script for LangChain chains examples.
This script helps install all required dependencies.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return success status."""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.output}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def main():
    print("=== LangChain Chains Examples - Dependency Installation ===\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install core dependencies
    print("\n📦 Installing core LangChain dependencies...")
    core_deps = [
        "langchain>=0.1.0",
        "langchain-core>=0.1.0", 
        "langchain-openai>=0.0.5",
        "openai>=1.0.0"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install '{dep}'"):
            print(f"Failed to install {dep}")
    
    # Install community package (optional but recommended)
    print("\n📦 Installing LangChain community package...")
    if not run_command("pip install 'langchain-community>=0.0.10'"):
        print("⚠️  langchain-community failed to install - some examples may not work")
    
    # Install vector store dependencies (optional)
    print("\n📦 Installing vector store dependencies...")
    if not run_command("pip install 'faiss-cpu>=1.7.0'"):
        print("⚠️  faiss-cpu failed to install - RAG example may not work")
    
    # Install testing dependencies
    print("\n📦 Installing testing dependencies...")
    test_deps = ["pytest>=7.4.0", "pytest-asyncio>=0.21.0"]
    for dep in test_deps:
        run_command(f"pip install '{dep}'")
    
    print("\n✅ Installation completed!")
    print("\n🔑 Next steps:")
    print("1. Set your OpenAI API key:")
    print("   export OPENAI_API_KEY=your_api_key_here")
    print("\n2. Test the installation:")
    print("   python3 chain_07_testing_chains.py  # No API key needed")
    print("   python3 chain_01_basic_llm_chain.py  # Requires API key")
    print("\n3. If langchain_community is missing, you can:")
    print("   - Run: pip install langchain-community")
    print("   - Or use: python3 chain_04_rag_chain_simple.py (no community deps)")

if __name__ == "__main__":
    main() 