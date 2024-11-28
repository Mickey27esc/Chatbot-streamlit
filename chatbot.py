
import streamlit as st
import google.generativeai as genai

st.title("🤖📂 Gemini based RAG App")

API_KEY = st.sidebar.text_input("GEMINI API Key", type="password")

# Set Gemini API key from Streamlit secrets
genai.configure(api_key=API_KEY)

# Initialize model
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize chat
if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.model.start_chat(
        history=st.session_state.chat_history,
    )
    

# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Escribe aquí..."):
    # Add user message to chat history
    st.session_state.chat_history.append(
        dict(
            role='user',
            content=prompt,
        )
    )
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):   
        # Call Gemini API to generate the assistant's response based on chat
        response = st.session_state.chat.send_message(prompt)
        st.markdown(response.text)  # Display the response
    # Add AI message to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
