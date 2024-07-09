import os
import pandas as pd
from typing import Generator


from groq import Groq
import streamlit as st
from config import SYSTEM_MESSAGE, MODELS_DETAILS, TEMPERATURE


client = Groq(api_key = st.secrets["api"]["GROQ_API_KEY"])

def main():
    st.set_page_config(page_title="[Test] Invoice Chatbot", page_icon=":robot:", layout="wide")

    # Display the title and introduction of the application
    st.title("Groqing Invoices")
    st.markdown(
        """
        Try to ask questions related to invoices such as "Create an invoice of product A to company ABC with quantity of 5" or "Help review the invoice number 1234".
        """, unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Initialize chat history and selected model
    if "messages" not in st.session_state:
       st.session_state.messages = []

    if "selected_model" not in st.session_state:
       st.session_state.selected_model = None


    # Sidebar for chat history
    st.sidebar.header("Model Configuration")
    # Select Model
    with st.sidebar:
        selected_model = st.selectbox(
           label="Select Model:",
            options=list(MODELS_DETAILS.keys()),
            format_func=lambda x: MODELS_DETAILS[x]['name'],
            index=2, # Default to Llama3-8b
        )
    # Detect model change and clear chat history if model has changed
    if st.session_state.selected_model != selected_model:
       st.session_state.messages = []
       st.session_state.selected_model = selected_model

    # New Chat button at the top right
    st.markdown(
        """
        <style>
        .stButton {float: right;}
        </style>
        """, unsafe_allow_html=True
    )
    if st.button("New Chat"):
       st.session_state.messages = []
       st.experimental_rerun()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
       avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
       with st.chat_message(message["role"], avatar=avatar):
          st.markdown(message["content"])
    
    def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
       """Yield chat response content from the Groq API response."""
       for chunk in chat_completion:
          if chunk.choices[0].delta.content:
             yield chunk.choices[0].delta.content


    if prompt := st.chat_input("Enter your prompt here..."):
       st.session_state.messages.append({"role": "user", "content": prompt})

       with st.chat_message("user", avatar='👨‍💻'):
          st.markdown(prompt)

       # Fetch response from Groq API
       try:
          chat_completion = client.chat.completions.create(
             model=selected_model,
             temperature=TEMPERATURE,
             messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                *[
                      {
                         "role": msg["role"],
                         "content": msg["content"]
                      }
                      for msg in st.session_state.messages
               ]
             ],
             stream=True
          )
       # Use the generator function with st.write_stream
          with st.chat_message("assistant", avatar="🤖"):
                chat_responses_generator = generate_chat_responses(chat_completion)
                full_response = st.write_stream(chat_responses_generator)
       except Exception as e:
          st.error(e, icon="🚨")

       # Append the full response to session_state.messages
       if isinstance(full_response, str):
          st.session_state.messages.append(
                {"role": "assistant", "content": full_response})
       else:
          # Handle the case where full_response is not a string
          combined_response = "\n".join(str(item) for item in full_response)
          st.session_state.messages.append(
                {"role": "assistant", "content": combined_response})

if __name__ == "__main__":
    main()