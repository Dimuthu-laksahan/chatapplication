from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain

import gradio as gr

# 1. Setup Ollama local LLM
llm = Ollama(model="smollm2:135m")  # replace with your local model name

# 2. Create a simple prompt template
prompt_template = ChatPromptTemplate.from_template("User: {input}\nAssistant:")

# 3. Create a LangChain chain
chat_chain = LLMChain(llm=llm, prompt=prompt_template)

# 4. Gradio function
def chat_with_bot(user_input):
    response = chat_chain.run(user_input)
    return response

# 5. Create Gradio UI
iface = gr.Interface(
    fn=chat_with_bot,
    inputs="text",
    outputs="text",
    title="Local Ollama Chatbot",
    description="A simple chatbot using Gradio, LangChain, and Ollama locally"
)

# 6. Launch
iface.launch()
