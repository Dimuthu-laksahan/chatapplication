from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import Tool

from langchain_ollama.chat_models import ChatOllama

# ---- 1) Define Tools ----

def calculator_tool(input_str: str) -> str:
    try:
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

# ---- 2) Setup Ollama LLM ----

llm = ChatOllama(
    model="smollm2:135m",              # change to your model name
    base_url="http://localhost:11434",
    temperature=0.7,
)

# ---- 3) History / Memory Setup ----

class InMemoryHistory(BaseChatMessageHistory):
    def __init__(self):
        self.messages: list[HumanMessage | AIMessage] = []

    def add_messages(self, messages):
        self.messages.extend(messages)

    def clear(self):
        self.messages = []

    def get_messages(self):
        return self.messages

# A store to hold histories by session id
history_store: dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in history_store:
        history_store[session_id] = InMemoryHistory()
    return history_store[session_id]

# ---- 4) Prompt Template ----

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the tools when needed."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Combine prompt + llm into a runnable
base_runnable = prompt | llm  # this builds a runnable

# Wrap runnable with history (memory)
agent_runnable = RunnableWithMessageHistory(
    runnable=base_runnable,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# ---- 5) Tool-Calling Logic ----
# Use a simple RunnableLambda to wrap the agent + tool-calling logic.

def agent_logic_fn(inputs, config):
    """
    inputs: {"input": <user input>}
    config: {"configurable": {"session_id": <id>}}
    """
    user_input = inputs["input"]
    session_id = config["configurable"]["session_id"]
    history = get_session_history(session_id)

    # First, call the agent runnable to decide what to do
    # it will get the chat history and user input
    response = agent_runnable.invoke(inputs, config=config)
    ai_msg = response  # this is likely an AIMessage or string

    # Parse the AI's text to see if it wants to call a tool
    # For simplicity, here we just run tools manually based on simple markers.
    # (In production you'd use a proper agent executor with tool-calling logic.)
    result = None
    if "calculator(" in ai_msg.content:
        # very naive extraction
        expr = ai_msg.content.split("calculator(")[1].split(")")[0]
        result = calculator_tool(expr)
    elif "run_python(" in ai_msg.content:
        code = ai_msg.content.split("run_python(")[1].rsplit(")", 1)[0]
        result = run_python_tool(code)

    # Add user message + AI message to history
    history.add_messages([HumanMessage(content=user_input), AIMessage(content=ai_msg.content)])

    # If there's a tool result, add the tool result as another AI message
    if result is not None:
        history.add_messages([AIMessage(content=f"Tool result: {result}")])
        return result

    return ai_msg.content

agent = RunnableLambda(agent_logic_fn)

# ---- 6) Run / Test ----

def chat(session_id: str, user_input: str):
    out = agent.invoke({"input": user_input}, config={"configurable": {"session_id": session_id}})
    print("AI:", out)
    print("History:", get_session_history(session_id).get_messages())

if __name__ == "__main__":
    chat("user1", "What is 10 + 20?")
    chat("user1", "Now run a python code: factorial of 5 using run_python")

