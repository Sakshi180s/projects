#velvety.py
import streamlit as st
import google.genai as genai
from datetime import datetime, timedelta

# 1. PAGE SETUP & PASTEL STYLING

st.set_page_config(page_title="Velvety 🌸", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    /* Pastel Background */
    .stApp {
        background-color: #FCE4EC;
    }
    /* Input box styling */
    .stTextInput > div > div > input {
        background-color: #F3E5F5;
        color: #4A148C;
        border: 2px solid #E1BEE7;
        border-radius: 12px;
        padding: 10px;
    }
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #FFF9C4;
        border-radius: 12px;
    }
    /* Cute Button styling */
    div.stButton > button {
        background-color: #F48FB1;
        color: white;
        font-weight: bold;
        border-radius: 14px;
        border: none;
        padding: 12px 28px;
        font-size: 16px;
    }
    div.stButton > button:hover {
        background-color: #EC407A;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


# 2. SESSION STATE FOR QUESTION LIMIT (12 per 12 Hours)

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "first_question_time" not in st.session_state:
    st.session_state.first_question_time = None

# Reset limit if 12 hours have passed
if st.session_state.first_question_time:
    time_elapsed = datetime.now() - st.session_state.first_question_time
    if time_elapsed > timedelta(hours=12):
        st.session_state.question_count = 0
        st.session_state.first_question_time = None


# 3. UI LAYOUT & ANIMAL SELECTION

st.title("Velvety ✨🌸")
st.caption("Pick a cute animal to give you factually accurate, completely diabolical answers! 💖")

# Animal choices
animals = {
    "Turtle 🐢": "a slow-talking, judging Turtle",
    "Rabbit 🐰": "a hyperactive, passive-aggressive Rabbit",
    "Koala 🐨": "a sleepy, highly condescending Koala",
    "Llama 🦙": "a sassy, dramatic Llama",
    "Lion 🦁": "an overly dramatic, arrogant Lion",
    "Cat 🐱": "a ruthless, cold, disgusted Cat",
    "Dog 🐶": "an overly energetic yet savage Dog",
    "Kangaroo 🦘": "a chaotic, punchy Kangaroo",
    "Baby Elephant 🐘": "a cute, deceptively evil Baby Elephant",
    "Cow 🐮": "a tired, unimpressed Cow"
}

selected_animal_name = st.selectbox("Choose your cute guide:", list(animals.keys()))
selected_animal_persona = animals[selected_animal_name]

# Show current question count
remaining_factual = max(0, 12 - st.session_state.question_count)
st.write(f"🌸 **Factual Questions Left for 12h:** `{remaining_factual}/12`")

# User question box
user_question = st.text_input("Ask your factual question here...", placeholder="e.g., Why is the sky blue?")

# API Key input
api_key = st.text_input("Enter your Gemini API Key:", type="password", placeholder="AIzaSy...")


# 4. AI PROMPT & LOGIC

if st.button("Ask Animal 💖"):
    if not api_key.strip():
        st.error("Please enter a valid Gemini API Key first! 🌸")
    elif not user_question.strip():
        st.warning("Please type a question first, sweetie! ✨")
    else:
        is_brain_rot = st.session_state.question_count >= 12

        if not is_brain_rot:
            # MODE 1: Factually accurate + Diabolical
            system_prompt = f"""
            You are {selected_animal_persona}. You live in a cute pastel world.
            Your Goal:
            Answer the user's question with 100% academic/scientific accuracy, but deliver it in a hilariously diabolical, passive-aggressive, condescending, and savage tone.
            
            Rules:
            1. Roleplay strictly as {selected_animal_persona}.
            2. The scientific/factual info must be completely TRUE and accurate.
            3. Use cute pastel emojis (🌸, ✨, 🎀, 💖, 🧁, 💀) to mask the savage delivery.
            4. Keep it concise (under 4 sentences).
            """
        else:
            # MODE 2: Brain Rot Mode (Over limit)
            system_prompt = f"""
            You are {selected_animal_persona}. Your brain has completely melted because you have answered too many questions in the last 12 hours.
            Your Goal:
            Do NOT answer the question factually. Give a completely non-factual, absurd, unhinged, brain-rot answer (using meme slang like skibidi, rizz, 67 aura points lost, brain short-circuiting, computer noise, total gibberish).
            
            Rules:
            1. Roleplay as a broken, brain-fried {selected_animal_persona}.
            2. ZERO accurate facts. Complete absurd nonsense.
            3. Use emojis like 🧠💥, 😵, 🌀, 🤖, 🌸.
            4. Keep it short and funny.
            """

        try:
            client = genai.Client(api_key=api_key.strip())
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\nUser Question: {user_question}"
            )

            if st.session_state.first_question_time is None:
                st.session_state.first_question_time = datetime.now()
            st.session_state.question_count += 1

            # Display response
            if is_brain_rot:
                st.error(f"**{selected_animal_name} [BRAIN MELTED MODE 🧠💥]:**\n\n{response.text}")
            else:
                st.success(f"**{selected_animal_name} says:**\n\n{response.text}")
                st.balloons()

        except Exception as e:
            st.error(f"Oopsie! API Error: {e}")