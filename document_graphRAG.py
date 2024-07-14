import os
import re
import json
import subprocess
import pandas as pd
import streamlit as st
import networkx as nx
from pyvis.network import Network

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
                    responses[method] = self.process_response(response.stdout.strip(), method)
                else:
                    responses[method] = "No response found."
            except Exception as e:
                print(f"Error during {method} chat: {e}")
                responses[method] = "An error occurred during the query."
        return responses

    def process_response(self, response, method):
        try:
            # Extract only the answer part after SUCCESS:
            if method == 'global':
                match = re.search(r'SUCCESS: Global Search Response: (.*)', response, re.DOTALL)
            elif method == 'local':
                match = re.search(r'SUCCESS: Local Search Response: (.*)', response, re.DOTALL)

            if match:
                answer = match.group(1).strip()
                print(f"Extracted answer: {answer}")  # Debug statement
                return answer
            else:
                return "No valid answer found."
        except Exception as e:
            print(f"Error processing response: {e}")  # Debug statement
            return "An error occurred while processing the response."

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

# Function to read parquet files and return DataFrames
def read_parquet_files(base_dir):
    nodes_file = os.path.join(base_dir, "create_final_nodes.parquet")
    relationships_file = os.path.join(base_dir, "create_final_relationships.parquet")
    nodes_df = pd.read_parquet(nodes_file)
    relationships_df = pd.read_parquet(relationships_file)

    print("Nodes DataFrame columns:", nodes_df.columns)  # Debug statement
    print("Relationships DataFrame columns:", relationships_df.columns)  # Debug statement

    return nodes_df, relationships_df

# Function to create a graph from the DataFrames
def create_graph(nodes_df, relationships_df):
    graph = nx.Graph()

    # Adjust the column names based on your DataFrame structure
    node_id_col = 'id'  # Corrected node id column name
    node_label_col = 'title'  # Corrected node label column name
    source_id_col = 'source'  # Corrected source id column name
    target_id_col = 'target'  # Corrected target id column name
    edge_label_col = 'description'  # Corrected edge label column name

    # Add nodes to the graph
    for _, row in nodes_df.iterrows():
        graph.add_node(row[node_id_col], label=row[node_label_col])

    # Add edges to the graph
    for _, row in relationships_df.iterrows():
        graph.add_edge(row[source_id_col], row[target_id_col], label=row[edge_label_col])

    return graph

# Function to visualize the graph using pyvis with dynamic resizing and interactivity
def visualize_graph(graph):
    net = Network(notebook=True, width="100%", height="750px", bgcolor="#222222", font_color="white")
    net.from_nx(graph)

    # Add dynamic resizing and other interactivity options
    options = {
        "nodes": {
            "shape": "dot",
            "size": 10,
            "font": {"size": 16}
        },
        "edges": {
            "color": {"inherit": "from"},
            "smooth": {"type": "dynamic"}
        },
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 95,
                "springConstant": 0.04,
                "damping": 0.09
            },
            "minVelocity": 0.75
        },
        "interaction": {
            "hover": True,
            "tooltipDelay": 200,
            "hideEdgesOnDrag": True,
            "hideNodesOnDrag": True
        }
    }

    net.set_options(json.dumps(options))
    net.show("graph.html")
    st.write("### Interactive Graph")
    st.components.v1.html(open("graph.html", "r").read(), height=800)

# Streamlit UI for uploading and processing text file
def upload_and_process_text():
    st.title('Document graphRAG - Chat with document graphs using local LLM')
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
    st.title('Document graphRAG - Chat with document graphs using local LLM')
    text_path = st.session_state.get('text_path')
    if not text_path or not os.path.exists(text_path):
        st.error("Text file missing or not found. Please go back and upload a TXT file.")
        return

    if 'chat_instance' not in st.session_state:
        st.session_state['chat_instance'] = ChatWithText(text_path=text_path)

    # Visualize the graph only after reaching this page
    base_dir = "ragtest/output/output/artifacts"
    try:
        nodes_df, relationships_df = read_parquet_files(base_dir)
        graph = create_graph(nodes_df, relationships_df)
        visualize_graph(graph)
    except FileNotFoundError as e:
        st.warning(str(e))

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
