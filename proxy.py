from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Ollama server configuration
OLLAMA_API_BASE = "http://localhost:11434/api"
NOMIC_EMBED_MODEL = "nomic-embed-text"

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/v1/embeddings', methods=['POST'])
def get_embeddings():
    data = request.json

    # Log the received data
    app.logger.debug(f"Received data: {data}")

    # Check if the required fields are in the request
    if 'input' not in data:
        return jsonify({'error': 'Missing "input" field in request data'}), 400

    # Prepare the request for Ollama
    input_texts = data['input']
    embeddings = []

    for input_text in input_texts:
        ollama_request = {
            "model": NOMIC_EMBED_MODEL,
            "prompt": input_text
        }

        # Log the request to Ollama
        app.logger.debug(f"Sending request to Ollama: {ollama_request}")

        # Call the Ollama API
        response = requests.post(f"{OLLAMA_API_BASE}/embeddings", json=ollama_request)

        # Log the response from Ollama
        app.logger.debug(f"Ollama response status: {response.status_code}")
        app.logger.debug(f"Ollama response data: {response.text}")

        if response.status_code != 200:
            return jsonify({'error': 'Error from Ollama API', 'details': response.text}), response.status_code

        ollama_response = response.json()

        # Check if the 'embedding' key exists in the Ollama response
        if 'embedding' not in ollama_response:
            return jsonify({'error': 'Malformed response from Ollama API', 'details': ollama_response}), 500

        embeddings.append(ollama_response['embedding'])

    # Prepare the response in OpenAI format
    openai_response = {
        "data": [{"object": "embedding", "embedding": emb} for emb in embeddings],
        "model": NOMIC_EMBED_MODEL,
        "usage": {
            "prompt_tokens": len(data['input']),
            "total_tokens": len(data['input'])  # Adjust this based on actual usage
        }
    }

    # Log the final response
    app.logger.debug(f"Response to client: {openai_response}")

    return jsonify(openai_response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
