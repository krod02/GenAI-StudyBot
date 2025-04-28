# _pipeline.py

import requests
import time

def create_payload(target, model, prompt, temperature=0.6, num_ctx=150, num_predict=200):
    """
    Creates a payload dictionary for sending to the Llama API (Ollama).
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict
        },
        "stream": False  # Important: we want the full output at once
    }
    return payload

def model_req(payload):
    """
    Sends the payload to the Ollama server and returns the generated response.
    """
    url = "http://localhost:11434/api/generate"  # Ollama default server
    try:
        start_time = time.time()
        response = requests.post(url, json=payload)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return elapsed_time, result.get('response', '')
        else:
            return elapsed_time, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return 0, f"Exception: {str(e)}"
