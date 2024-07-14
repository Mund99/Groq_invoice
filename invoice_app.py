import inspect
import pandas as pd
import json
from groq import Groq
import google.generativeai as genai
import streamlit as st

from config import *
import db_functions
from function_tool_creator import create_multiple_function_tools

initial_system_msg = [{"role": "system", "content": SYSTEM_MESSAGE}]
groq_models = ["gemma-7b-it", "gemma2-9b-it", "whiper-large-v3", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
gemini_models = ["gemini-1.5-flash", "gemini-1.0-pro", "gemini-1.0-pro-001", "gemini-1.0-pro-latest", "gemini-1.0-pro-vision-latest", "gemini-1.5-flash-001", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-1.5-pro-001", "gemini-1.5-pro-latest", "gemini-pro", "gemini-pro-vision"]

# Get all functions from db_functions
all_functions = [func for name, func in inspect.getmembers(db_functions, inspect.isfunction)]
db_functions_list = [func for func in all_functions if func.__module__ == 'db_functions']
# Create function tools list
tools = create_multiple_function_tools(db_functions_list)
# Create available_functions dictionary
available_functions = {func.__name__: func for func in db_functions_list}


#------------------------------#
# Handling model configuration 

def clear_session_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.0
    if "api_key" not in st.session_state:
        st.session_state.api_key = None
    if "gemini_chat" not in st.session_state:
        st.session_state.gemini_chat = None

def handle_model_config_change(selected_model, temperature):
    model_changed = st.session_state.selected_model != selected_model
    temp_changed = st.session_state.temperature != temperature

    if model_changed or temp_changed:
        # Store the new values
        new_model = selected_model
        new_temp = temperature

        # Clear and reinitialize the session state
        clear_session_state()
        initialize_session_state()

        # Set the new values
        st.session_state.selected_model = new_model
        st.session_state.temperature = new_temp
        st.session_state.messages = initial_system_msg

        # Set up the appropriate model
        if new_model in gemini_models:
            st.session_state.gemini_chat = setup_gemini_model()
        else:
            st.session_state.api_key = st.secrets["api"]["GROQ_API_KEY"]

#------------------------------#
# Page layout configuration 

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
            clear_session_state()
            st.rerun()

    # Close the title container
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        Try to ask questions related to invoices such as \n
        "Show me the product database" "我要查阅产品数据库", \n
        "Check if ABD Trading is in the customer database, show me details.", \n
        """
    )

    # Create the rainbow divider
    st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)

def sidebar_model_config():
    st.sidebar.header("Model Configuration")
    selected_model = st.sidebar.selectbox(
        label="Select Model:",
        options=list(MODELS_DETAILS.keys()),
        format_func=lambda x: f"{MODELS_DETAILS[x]['name']} ({MODELS_DETAILS[x]['developer']})",
        index=11,
    )

    temperature = st.sidebar.slider(
        label="Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,  # Default temperature
        step=0.01,
    )
        
    return selected_model, temperature

def display_internal_process():
    # Add a checkbox to toggle the internal model process display
    show_internal_process = st.sidebar.checkbox("Show Internal Model Process", value=True)

    if show_internal_process:
        if st.session_state.selected_model in groq_models:
            st.sidebar.markdown("### Internal Model Process (Using Groq API)")
            
            for msg in st.session_state.messages[1:]:
                if msg['role'] == 'user':
                    st.sidebar.markdown(f"**User:**")
                    st.sidebar.markdown(f"```\n{msg['content'][:200]}...\n```")
                elif msg['role'] == 'assistant':
                    st.sidebar.markdown(f"**Assistant:**")
                    if 'content' in msg:
                        st.sidebar.markdown(f"```\n{msg['content'][:200]}...\n```")
                    if 'tool_calls' in msg:
                        for tool_call in msg['tool_calls']:
                            st.sidebar.markdown(f"Tool Call: `{tool_call['function']['name']}`")
                            st.sidebar.markdown("Arguments:")
                            st.sidebar.json(tool_call['function']['arguments'])
                elif msg['role'] == 'tool':
                    st.sidebar.markdown(f"**Tool Response:**")
                    st.sidebar.markdown(f"```\n{msg['content'][:200]}...\n```")
                
                st.sidebar.markdown("---")
        
        elif st.session_state.selected_model in gemini_models:
            st.sidebar.markdown("### Internal Model Process (Using Gemini API)")
            
            for msg in st.session_state.gemini_chat.history:
                for part in msg.parts:
                    part_dict = type(part).to_dict(part)
                    
                    if msg.role == 'user':
                        st.sidebar.markdown(f"**User:**")
                    elif msg.role == 'model':
                        st.sidebar.markdown(f"**Model:**")
                    
                    if 'text' in part_dict:
                        st.sidebar.markdown(f"```\n{part_dict['text'][:200]}...\n```")
                    elif 'function_call' in part_dict:
                        func_call = part_dict['function_call']
                        st.sidebar.markdown(f"Function Call: `{func_call['name']}`")
                        st.sidebar.markdown(f"Arguments:")
                        st.sidebar.json(func_call['args'])
                    elif 'function_response' in part_dict:
                        func_response = part_dict['function_response']
                        st.sidebar.markdown(f"Function Response:")
                        st.sidebar.json(func_response)
                    else:
                        st.sidebar.markdown(f"Unknown part type:")
                        st.sidebar.json(part_dict)
                
                st.sidebar.markdown("---")
                
#------------------------------#
# Processing the chat response by the model 

def get_chat_response(prompt):
    try:
        if st.session_state.selected_model in groq_models:
            chat_completion = handle_chat_completion()
            response_msg = chat_completion.choices[0].message

            if not response_msg.tool_calls:
                display_assistant_message(response_msg.content)
            else:
                handle_tool_calls(response_msg)
        elif st.session_state.selected_model in gemini_models:
            response = st.session_state.gemini_chat.send_message(prompt)
            display_assistant_message(response.text)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}", icon="🚨")
        return None

def setup_gemini_model():
    genai.configure(api_key=st.secrets["api"]["GOOGLE_API_KEY"])

    model = genai.GenerativeModel(
        model_name=f"models/{st.session_state.selected_model}",
        system_instruction = SYSTEM_MESSAGE,
        generation_config={"temperature":st.session_state.temperature},
        tools = db_functions_list
    )
    
    chat = model.start_chat(enable_automatic_function_calling=True)
    return chat



#------------------------------#
# Groq chat completion and tool calls 

def handle_chat_completion():
    client = Groq(api_key=st.session_state.api_key)
    chat_completion = client.chat.completions.create(
        model=st.session_state.selected_model,
        temperature=st.session_state.temperature,
        messages=st.session_state.messages,
        tools=tools,
        tool_choice="auto",
        stream=False,
    )
    return chat_completion

def handle_tool_calls(response_msg):
    st.session_state.messages.append(create_tool_call_message(response_msg))

    for tool_call in response_msg.tool_calls:
        function_response = execute_tool_call(tool_call)
        st.session_state.messages.append(
            create_tool_response_message(tool_call, function_response)
        )

    chat_completion = handle_chat_completion()
    response_msg = chat_completion.choices[0].message
    display_assistant_message(response_msg.content)

def create_tool_call_message(response_msg):
    return {
        "role": response_msg.role,
        "tool_calls": [
            {
                "id": tool_call.id,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
                "type": tool_call.type,
            }
            for tool_call in response_msg.tool_calls
        ],
    }

def execute_tool_call(tool_call):
    function_name = tool_call.function.name
    function_to_call = available_functions[function_name]
    function_args = json.loads(tool_call.function.arguments)
    return function_to_call(**function_args)

def create_tool_response_message(tool_call, function_response):
    return {
        "role": "tool",
        "content": json.dumps(function_response),
        "tool_call_id": tool_call.id,
    }


#------------------------------#
# Handling user input 

def handle_user_input():
    prompt = st.chat_input("Enter your prompt here...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👦🏻"):
            st.markdown(prompt)
    return prompt

#------------------------------#
# Displaying messages 

def display_assistant_message(content):
    with st.chat_message("assistant", avatar="💬"):
        st.markdown(content)
    st.session_state.messages.append({"role": "assistant", "content": content})

def display_chat_history():
    for message in st.session_state.messages[1:]:  # Skip the initial system message
        if message["role"] not in ["user", "assistant"] or "tool_calls" in message:
            continue  # Skip messages
        with st.chat_message(
            message["role"], avatar="👦🏻" if message["role"] == "user" else "💬"
        ):
            st.markdown(message["content"])

#------------------------------#
# Main function to run the chatbot
def run_chatbot():
    initialize_session_state()
    set_page_config()
    display_title_and_button()

    selected_model, temperature = sidebar_model_config()
    display_internal_process()
    handle_model_config_change(selected_model, temperature)

    display_chat_history()  # Display chat history

    if prompt := handle_user_input():  # Handle user input
        get_chat_response(prompt)  # Get chat response from model
        st.rerun()
    
if __name__ == "__main__":
    run_chatbot()
