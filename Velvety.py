#Velvety.py
import streamlit as st
import google.genai as genai
from datetime import datetime, timedelta
import os


# 1. PAGE SETUP & PASTEL STYLING

st.set_page_config(page_title="Velvety 🌸", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    /* Pastel Background */
    .stApp {
        background-color: #FCE4EC;
    }
    /* Make all default text dark and readable */
    p, label, span, .stMarkdown {
        color: #000000 !important;
        font-weight: 500;
    }
    /* Input box styling */
    .stTextInput > div > div > input {
        background-color: #F3E5F5;
        color: #000000 !important;
        border: 2px solid #E1BEE7;
        border-radius: 12px;
        padding: 10px;
    }
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #FFF9C4;
        color: #000000 !important;
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


# 2. SESSION STATE

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
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

# Models to try, in order. If one is unavailable, the next is used.
MODELS = ["gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash"]


def get_api_key():
    """Look for the key in env variable, then Streamlit secrets, then sidebar box."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return st.sidebar.text_input("Gemini API key", type="password")


# 3. LOGIN SCREEN

st.title("Velvety ✨🌸")

if not st.session_state.logged_in:
    st.subheader("Welcome, sweetie! 💕 Please enter your email to enter the pastel doom room:")
    email_input = st.text_input("Your Email Address", placeholder="e.g., bestie@gmail.com")

    if st.button("Enter Velvety 🌸"):
        if email_input.strip() and "@" in email_input:
            st.session_state.logged_in = True
            st.session_state.user_email = email_input
            st.rerun()
        else:
            st.warning("Please enter a valid email address first! ✨")
else:

    # 4. MAIN APP INTERFACE

    st.caption(f"Logged in as: 🌸 `{st.session_state.user_email}` | Pick an animal for diabolical facts!")

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

    remaining_factual = max(0, 12 - st.session_state.question_count)
    st.write(f"🌸 **Questions Left for 12h:** `{remaining_factual}/12`")

    user_question = st.text_input("Ask your question here...", placeholder="e.g., Why is the sky blue?")

    # Logout option
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.rerun()

    api_key = get_api_key()

    # 5. AI LOGIC

    if st.button("Ask your pet 💖"):
        if not user_question.strip():
            st.warning("Please type a question first, sweetie! ✨")
        elif not api_key:
            st.warning("No API key found! Add it in the sidebar or set GEMINI_API_KEY. 🔑")
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
                Do NOT answer the question factually. Give a completely non-factual, absurd, unhinged, brain-rot answer (using meme slang like skibidi, rizz, 67 aura points lost, brain short-circuiting, total gibberish).

                Rules:
                1. Roleplay as a broken, brain-fried {selected_animal_persona}.
                2. ZERO accurate facts. Complete absurd nonsense.
                3. Use emojis like 🧠💥, 😵, 🌀, 🤖, 🌸.
                4. Keep it short and funny.
                """

            # The API call is OUTSIDE the if/else, so both modes use it
            try:
                client = genai.Client(api_key=api_key)

                response = None
                last_error = None
                for model_name in MODELS:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=f"{system_prompt}\n\nUser Question: {user_question}"
                        )
                        break  # it worked, stop trying other models
                    except Exception as model_error:
                        last_error = model_error

                if response is None:
                    raise last_error

                if st.session_state.first_question_time is None:
                    st.session_state.first_question_time = datetime.now()
                st.session_state.question_count += 1

                if is_brain_rot:
                    st.error(f"**{selected_animal_name} [BRAIN MELTED MODE 🧠💥]:**\n\n{response.text}")
                else:
                    st.success(f"**{selected_animal_name} says:**\n\n{response.text}")
                    st.balloons()

            except Exception as e:
                st.warning(f"🌸 Something went wrong: {e}")