import os
from dotenv import load_dotenv
from langsmith import Client, traceable

load_dotenv()

print("TRACING:", os.getenv("LANGSMITH_TRACING"))
print("PROJECT:", os.getenv("LANGSMITH_PROJECT"))
print("KEY:", bool(os.getenv("LANGSMITH_API_KEY")))

client = Client()

print("Testing LangSmith connection...")

@traceable(name="agentlab-test")
def test_fn():
    return "LangSmith is working"

result = test_fn()

print("RESULT:", result)
print("DONE")