from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import HumanMessage  

# Connect to your local Ollama model
chat = ChatOllama(model="smollm2:135m", base_url="http://localhost:11434")

# Prepare messages
messages = [
    ("human", "who are you")
    
]

# Invoke the model
response = chat.invoke(messages)

# Print the reply
print(response.content)
