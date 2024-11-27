
import streamlit as st
import google.generativeai as genai

st.title("🤖📂 RAG App")

API_KEY = st.sidebar.text_input("GEMINI API Key", type="password")


def generate_response(input_text):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(input_text)
    st.info(response)


with st.form("my_form"):
    text = st.text_area(
        "Enter text:",
        "What are the three key pieces of advice for learning how to code?",
    )
    submitted = st.form_submit_button("Submit")
    if not API_KEY.endswith("-pk"):
        st.warning("Please enter your GEMINI API key!", icon="⚠")
    if submitted and API_KEY.endswith("-pk"):
        generate_response(text)
