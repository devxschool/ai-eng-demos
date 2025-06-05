import time
from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI

# 1. Set up an in-memory cache
set_llm_cache(InMemoryCache())
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

# 2. Measure first invocation
start = time.perf_counter()
resp1 = llm.invoke("Tell me a dad joke.")
first_elapsed = time.perf_counter() - start
print(resp1.content)
print(f"First run (uncached): {first_elapsed:.2f}s")

# 3. Measure second invocation
start = time.perf_counter()
resp2 = llm.invoke("Tell me a dad joke.")
second_elapsed = time.perf_counter() - start
print(resp2.content)
print(f"Second run (cached): {second_elapsed:.4f}s")