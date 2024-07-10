import os
import pandas as pd
from typing import Generator
from groq import Groq
import streamlit as st
from config import *

client = Groq(api_key=st.secrets["api"]["GROQ_API_KEY"])
initial_system_msg = [{"role": "system", "content": SYSTEM_MESSAGE}]


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = initial_system_msg
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = list(MODELS_DETAILS.keys())[
            2
        ]  # Default to Llama3-8b
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.0
    if "api_key" not in st.session_state:
        st.session_state.api_key = st.secrets["api"]["GROQ_API_KEY"]


def set_page_config():
    st.set_page_config(
        page_title="[Test] Invoice Chatbot", page_icon=":robot:", layout="wide"
    )


def display_title_and_button():
    # CSS for the rainbow divider and improved button layout
    custom_css = """
    <style>
    .rainbow-divider {
        height: 4px;
        background-image: linear-gradient(
            to right, 
            violet, 
            indigo, 
            blue, 
            green, 
            yellow, 
            orange, 
            red
        );
        margin: 20px 0;
    }
    .title-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .title-text {
        margin: 0;
        padding: 0;
        line-height: 1.2;
    }
    .stButton {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        height: 100%;
    }
    .stButton > button {
        margin: 0;
        padding: 0.25rem 0.75rem;
        height: auto;
    }
    </style>
    """

    # Inject the CSS
    st.markdown(custom_css, unsafe_allow_html=True)

    # Create the title container
    st.markdown('<div class="title-container">', unsafe_allow_html=True)

    # Create two columns: one for the title, one for the button
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(
            '<h1 class="title-text">Invoice Chatbot</h1>', unsafe_allow_html=True
        )

    with col2:
        if st.button("New Chat"):
            st.session_state.messages = initial_system_msg
            st.rerun()

    # Close the title container
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        Try to ask questions related to invoices such as "Create an invoice of product A to company ABC with quantity of 5" or "Help review the invoice number 1234".
        """
    )

    # Create the rainbow divider
    st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)


def sidebar_model_config():
    st.sidebar.header("Model Configuration")
    selected_model = st.sidebar.selectbox(
        label="Select Model:",
        options=list(MODELS_DETAILS.keys()),
        format_func=lambda x: MODELS_DETAILS[x]["name"],
        index=2,  # Default to Llama3-8b
        key="selected_model",  # Add this line
    )

    temperature = st.sidebar.slider(
        label="Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,  # Default temperature
        step=0.01,
        key="temperature",  # Add this line
    )
    return selected_model, temperature


def handle_model_config_change(selected_model, temperature):
    if st.session_state.selected_model != selected_model:
        st.session_state.messages = initial_system_msg
        st.session_state.selected_model = selected_model
        if selected_model == "Gemini-1.5-Flash":
            st.session_state.api_key = st.secrets["api"]["GOOGLE_API_KEY"]
        else:
            st.session_state.api_key = st.secrets["api"]["GROQ_API_KEY"]
    if st.session_state.temperature != temperature:
        st.session_state.messages = initial_system_msg
        st.session_state.selected_model = temperature


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def get_chat_response(prompt):
    try:
        chat_completion = client.chat.completions.create(
            model=st.session_state.selected_model,
            temperature=st.session_state.temperature,
            messages=st.session_state.messages,
            stream=True,
        )

        with st.chat_message("assistant", avatar="💬"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
        return full_response
    except Exception as e:
        st.error(e, icon="🚨")
        return None


def handle_user_input():
    if prompt := st.chat_input("Enter your prompt here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👦🏻"):
            st.markdown(prompt)
        return prompt
    return None


def update_chat_history(full_response):
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
    else:
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response}
        )


def display_chat_history():
    for message in st.session_state.messages[1:]:  # Skip the initial system message
        with st.chat_message(
            message["role"], avatar="👦🏻" if message["role"] == "user" else "💬"
        ):
            st.markdown(message["content"])

def run_chatbot():
    initialize_session_state()
    set_page_config()
    display_title_and_button()

    selected_model, temperature = sidebar_model_config()
    handle_model_config_change(selected_model, temperature)

    # Display chat history
    display_chat_history()

   # When user prompt is entered
    prompt = handle_user_input()
    if prompt:
        full_response = get_chat_response(prompt)
        if full_response:
            update_chat_history(full_response)


if __name__ == "__main__":
    run_chatbot()
