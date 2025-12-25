from openai import OpenAI
import os

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

instructions = """
You are a personal math tutor. When asked a math question,
write and run code using the python tool to answer the question.
"""

resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "code_interpreter",
            "container": {"type": "auto", "memory_limit": "4g"},
        }
    ],
    instructions=instructions,
    input="I need to solve the equation 3x + 11 = 14. Can you help me?",
)

print("Output Text:")
print(resp.output)

print("\nCode Interpreter Calls:")
print(resp.output_text)

print("\nGenerated Code:")
for item in resp.output:
    if item.type == "code_interpreter_call":
        print(item.code)
