import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- App Configuration ---
st.set_page_config(
    page_title="EduGenius - AI Assistant",
    page_icon="🧠",
    layout="wide"
)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI Components ---
st.title("🧠 EduGenius – Your Study Companion")
st.markdown("Ask me anything related to your subjects, syllabus, or exams!")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your Hugging Face API Key", 
                          type="password",
                          value=os.getenv("HF_API_KEY", ""))
    model_options = {
        "Llama 3.3 70B (Advanced)": "meta-llama/Llama-3.3-70B-Instruct",
        "GPT-2 (Basic)": "gpt2"
    }
    
    selected_model_name = st.selectbox(
        "Select Model",
        options=list(model_options.keys()),
        index=0  # Default to the first option
    )
    model_name = model_options[selected_model_name]

# --- Helper Functions ---
def get_hf_response(message, model_name, api_key):
    """Get response from Hugging Face Inference API"""
    if not api_key:
        return "⚠️ Please enter your Hugging Face API key in the sidebar."
    
    if "llama" in model_name.lower():
        API_URL = "https://router.huggingface.co/featherless-ai/v1/chat/completions"
    else:
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        if "llama" in model_name.lower():
            # Format for Llama 3.3 70B
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7,
                "max_tokens": 100
            }
        else:
            # Format for standard Hugging Face models
            payload = {
                "inputs": message,
                "parameters": {
                    "max_new_tokens": 100,
                    "return_full_text": False,
                    "temperature": 0.7
                }
            }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle the response based on model type
        if "llama" in model_name.lower():
            # Handle Llama 3.3 70B response format
            if isinstance(result, dict) and "choices" in result:
                return result["choices"][0]["message"]["content"]
        else:
            # Handle standard Hugging Face model response
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and "generated_text" in result[0]:
                    return result[0]["generated_text"]
                return str(result[0])
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
        
        return "I received a response, but couldn't process it. Please try again."
        
    except requests.exceptions.HTTPError as http_err:
        return f"⚠️ HTTP error occurred: {http_err}"
    except Exception as e:
        return f"⚠️ An error occurred: {str(e)}"

# --- Main Chat Interface ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask EduGenius..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_hf_response(prompt, model_name, api_key)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Add some styling
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage.user {
        background-color: #f0f2f6;
    }
    .stChatMessage.assistant {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)
