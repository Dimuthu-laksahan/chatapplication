import streamlit as st
from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

# -----------------------------
# 1️⃣ Initialize LLM
# -----------------------------
llm = ChatOllama(model="smollm2:135m", base_url="http://localhost:11434")

# -----------------------------
# 2️⃣ Intent Extraction Prompt (JSON enforced)
# -----------------------------
intent_prompt = PromptTemplate(
    input_variables=["message"],
    template="""
You are an intent classifier for a hotel booking chatbot.

Possible intents:
- search_hotels
- check_availability
- make_booking
- cancel_booking
- modify_booking
- faq
- unknown

User message: "{message}"

Respond **ONLY with one of the intent names above, exactly as written**, as JSON.
Example: "search_hotels"
Do NOT include any other text or explanation.
"""
)
intent_chain = intent_prompt | llm | StrOutputParser()

# -----------------------------
# 3️⃣ Entity Extraction Prompt (JSON enforced)
# -----------------------------
entity_prompt = PromptTemplate(
    input_variables=["message"],
    template="""
Extract the following entities from the user message:
- city
- check_in
- check_out
- guests
- room_type
- booking_id

Return a **valid JSON object with these keys only**. If a value is missing, use null.
Do NOT include any other text or explanation.

Message: {message}
"""
)
entity_chain = entity_prompt | llm | StrOutputParser()

# -----------------------------
# 4️⃣ Tools / Actions
# -----------------------------
def search_hotels(city):
    if not city:
        return "Please specify the city you want to search hotels in."
    return f"Hotels in {city}: Hotel A, Hotel B, Hotel C"

def check_availability(city, check_in, check_out):
    if not city or not check_in or not check_out:
        return "Please provide city, check-in, and check-out dates."
    return f"Rooms are available in {city} from {check_in} to {check_out}"

def make_booking(entities):
    if not entities.get("city") or not entities.get("check_in") or not entities.get("room_type"):
        return "Incomplete information for booking."
    return f"Booking confirmed: {entities['room_type']} room in {entities['city']} for {entities.get('guests', 1)} guest(s) on {entities['check_in']}"

def cancel_booking(booking_id):
    if not booking_id:
        return "Please provide a valid booking ID to cancel."
    return f"Booking {booking_id} has been cancelled"

# -----------------------------
# 5️⃣ Decision Router
# -----------------------------
def decision_router(intent, entities):
    if intent == "search_hotels":
        return search_hotels(entities.get("city"))

    elif intent == "check_availability":
        return check_availability(
            entities.get("city"),
            entities.get("check_in"),
            entities.get("check_out")
        )

    elif intent == "make_booking":
        return make_booking(entities)

    elif intent == "cancel_booking":
        return cancel_booking(entities.get("booking_id"))

    elif intent == "faq":
        return "You can ask about hotel facilities, amenities, or policies."

    else:
        return "Sorry, I didn't understand. Can you rephrase?"

# -----------------------------
# 6️⃣ Streamlit UI
# -----------------------------
st.title("🏨 Hotel Booking Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    # 1. Extract intent
    intent_raw = intent_chain.invoke({"message": user_input})
    try:
        intent = json.loads(intent_raw)  # force JSON parse
    except:
        intent = "unknown"

    # 2. Extract entities
    entities_json = entity_chain.invoke({"message": user_input})
    try:
        entities = json.loads(entities_json)
    except:
        entities = {
            "city": None,
            "check_in": None,
            "check_out": None,
            "guests": None,
            "room_type": None,
            "booking_id": None
        }

    # Ensure all keys exist
    entities = {k: entities.get(k) for k in ["city", "check_in", "check_out", "guests", "room_type", "booking_id"]}

    # Debug info (optional)
    st.write("Debug - Intent:", intent)
    st.write("Debug - Entities:", entities)

    # 3. Get chatbot response
    response = decision_router(intent, entities)

    # 4. Update chat history
    st.session_state.history.append(("You", user_input))
    st.session_state.history.append(("Bot", response))

# Display chat history
for speaker, message in st.session_state.history:
    st.markdown(f"**{speaker}:** {message}")


#(python -m streamlit run hotel_chatbot.py)
