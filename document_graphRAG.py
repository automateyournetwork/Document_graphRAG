import os
import subprocess
import json
import streamlit as st

# Message classes
class Message:
    def __init__(self, content):
        self.content = content

class HumanMessage(Message):
    """Represents a message from the user."""
    pass

class AIMessage(Message):
    """Represents a message from the AI."""
    pass

# Define a class for chatting with text data using GraphRAG
class ChatWithText:
    def __init__(self, text_path):
        self.text_path = text_path
        self.conversation_history = []
        self.setup_graphrag()

    def setup_graphrag(self):
        try:
            if not os.path.exists('ragtest/input'):
                os.makedirs('ragtest/input')
            if not os.path.exists('ragtest'):
                os.makedirs('ragtest')

            text_output_path = self.text_path
            print(f"Text output path: {text_output_path}")  # Debug statement
            
            index_command = 'python -m graphrag.index --root ./ragtest'
            print(f"Running: {index_command}")  # Debug statement
            subprocess.run(index_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during GraphRAG setup: {e}")
        except Exception as e:
            print(f"General error during GraphRAG setup: {e}")

    def chat(self, question):
        responses = {}
        for method in ['global', 'local']:
            try:
                command = f'python -m graphrag.query --root ./ragtest --method {method} "{question}"'
                print(f"Running command: {command}")  # Debug statement
                response = subprocess.run(command, shell=True, capture_output=True, text=True)
                if response.stdout:
                    print(f"Raw response: {response.stdout.strip()}")  # Debug statement
                    responses[method] = self.process_response(response.stdout.strip())
                else:
                    responses[method] = "No response found."
            except Exception as e:
                print(f"Error during {method} chat: {e}")
                responses[method] = "An error occurred during the query."
        return responses

    def process_response(self, response):
        try:
            response_json = json.loads(response)
            print(f"Processed JSON response: {response_json}")  # Debug statement
            return self.ensure_string_format(response_json.get('answer', 'No valid answer found.'))
        except json.JSONDecodeError:
            print(f"JSON decode error: {response}")  # Debug statement
            return self.ensure_string_format(response)  # Return raw response if JSON decoding fails

    def ensure_string_format(self, data):
        if isinstance(data, (int, float)):
            return str(data)
        elif isinstance(data, dict):
            return {k: self.ensure_string_format(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.ensure_string_format(item) for item in data]
        return str(data)

    def debug_embedding_request(self, data):
        print(f"Embedding request data: {data}")  # Debug statement
        return data

# Streamlit UI for uploading and processing text file
def upload_and_process_text():
    st.title('Text Buddy - Chat with Text Files')
    uploaded_file = st.file_uploader("Choose a TXT file", type="txt")
    if uploaded_file:
        if not os.path.exists('ragtest/input'):
            os.makedirs('ragtest/input')
        text_path = os.path.join("ragtest/input", uploaded_file.name)
        with open(text_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.session_state['text_path'] = text_path
        st.success("Text file uploaded successfully.")
        if st.button("Proceed to Chat"):
            st.session_state['page'] = 2        

def chat_interface():
    st.title('Text Buddy - Chat with Text Files')
    text_path = st.session_state.get('text_path')
    if not text_path or not os.path.exists(text_path):
        st.error("Text file missing or not found. Please go back and upload a TXT file.")
        return

    if 'chat_instance' not in st.session_state:
        st.session_state['chat_instance'] = ChatWithText(text_path=text_path)

    user_input = st.text_input("Ask a question about the text data:")
    if user_input and st.button("Send"):
        with st.spinner('Thinking...'):
            responses = st.session_state['chat_instance'].chat(user_input)
            st.markdown("**Global Answer:**")
            st.markdown(responses.get('global', "No response found."))
            st.markdown("**Local Answer:**")
            st.markdown(responses.get('local', "No response found."))

            st.markdown("**Chat History:**")
            for message in st.session_state['chat_instance'].conversation_history:
                prefix = "*You:* " if isinstance(message, HumanMessage) else "*AI:* "
                st.markdown(f"{prefix}{message.content}")

if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state['page'] = 1

    if st.session_state['page'] == 1:
        upload_and_process_text()
    elif st.session_state['page'] == 2:
        chat_interface()
