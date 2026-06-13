from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableSequence, RunnableParallel

# 1. Your LLM
chat = ChatOllama(model="smollm2:135m", base_url="http://localhost:11434")

# 2. Clarifying prompt
clarify_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
You are an assistant. The goal is to understand the user's intent clearly.
Ask one or two clarifying questions if needed.

User Input: {user_input}

Questions:
"""
)

# 3. Intent summary prompt
intent_prompt = PromptTemplate(
    input_variables=["user_input", "answers"],
    template="""
You are an assistant. Based on the user's answers, summarize the intent clearly.

User Input: {user_input}
Answers to Clarifying Questions: {answers}

Intent Summary:
"""
)

# 4. Build runnables
clarify_seq = clarify_prompt | chat | StrOutputParser()
intent_seq = intent_prompt | chat | StrOutputParser()

passthrough = RunnablePassthrough()

def wrap_answers(clarify_output_and_input):
    original = clarify_output_and_input["passed"]
    clar = clarify_output_and_input["modified"]
    return {"user_input": original["user_input"], "answers": clar}

bridge = RunnableLambda(wrap_answers)

parallel = RunnableParallel(
    passed=passthrough,
    modified=clarify_seq
)

chain = RunnableSequence(
    first=parallel,
    middle=[bridge],
    last=intent_seq
)

# 5. Run first pass: ask clarifying questions
clarifying_questions = clarify_seq.invoke({"user_input": "I want to book a hotel for next weekend"})
print("Clarifying Questions:", clarifying_questions)

# 6. Wait for user’s answers
user_answers = input("Please answer the above clarifying questions: ")

# 7. Run intent summary
res = intent_seq.invoke({"user_input": "I want to pass my exams", "answers": user_answers})
print("Intent Summary:", res)
