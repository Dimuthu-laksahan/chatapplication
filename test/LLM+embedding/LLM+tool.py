# agent_example.py

from langchain_ollama import ChatOllama
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

# -- 1. Define the tools --

def calculator_tool(input_str: str) -> str:
    """
    Simple calculator that evaluates a math expression.
    Example: input_str = "5 * (3 + 2)"
    """
    try:
        # NOTE: eval is dangerous for arbitrary input. Use sandbox in production.
        result = eval(input_str, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error in calculation: {e}"

calculator = Tool(
    name="calculator",
    func=calculator_tool,
    description="Performs mathematical calculations, e.g. '12 / 4 + 3'."
)

def run_python_tool(code: str) -> str:
    """
    Runs a snippet of Python code and returns output.
    Example:
      code = "result = sum([1,2,3,4])"
    """
    try:
        local_vars = {}
        exec(code, {"__builtins__": {}}, local_vars)
        if "result" in local_vars:
            return str(local_vars["result"])
        return str(local_vars)
    except Exception as e:
        return f"Error in executing code: {e}"

run_python = Tool(
    name="run_python",
    func=run_python_tool,
    description="Executes Python code. Store your output in variable 'result'."
)

tools = [calculator, run_python]

# -- 2. Setup the Ollama LLM --

llm = ChatOllama(
    model="smolll m2:135m",           # change to your pulled model name
    base_url="http://localhost:11434",
    temperature=0.7
)

# -- 3. Setup memory and prompt template --

memory = ConversationBufferMemory(memory_key="chat_history")

template = """
You are a helpful assistant. Use the tools when needed.

User: {input}
Assistant:"""

prompt = PromptTemplate.from_template(template)

# -- 4. Initialize the agent --

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    prompt=prompt,
    verbose=True
)

# -- 5. Run sample queries --

def chat_with_agent(user_input: str):
    response = agent.run(user_input)
    print("Agent:", response)

if __name__ == "__main__":
    chat_with_agent("What is 12 * 7?")
    chat_with_agent("Now write a Python snippet to compute the factorial of 6.")
