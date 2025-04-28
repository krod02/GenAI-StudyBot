# llama_interface.py

from _pipeline import create_payload, model_req








FEW_SHOT = """You are an AI tutor that helps students learn effectively. Below are examples of how you should respond:

- If the user provides study material, generate a **concise summary**.
- If the user asks for flashcards, extract **key terms and definitions**.
- If the user asks for a quiz, create **multiple-choice questions** from the provided content.

Now process the following request:
"""

def run_llama_task(task_type: str, user_input: str):
    if task_type == "summarization":
        message = f"""Summarize the following text while maintaining a neutral, general explanation. 
Keep the summary under **40 words** for clarity.

Text: "{user_input}" """
        temperature = 0.6
        num_ctx = 150
        num_predict = 200

    elif task_type == "flashcards":
        message = f"""Generate exactly **five** concise flashcards based on the topic.  
Each flashcard should include:
- A **term** (bolded).
- A **brief definition** (15 words max).

Topic: "{user_input}" """
        temperature = 0.5
        num_ctx = 150
        num_predict = 200

    elif task_type == "quiz":
        message = f"""Create a **3-question multiple-choice quiz** based on the given topic.  
Each question should have **exactly four answer choices (A, B, C, D)**.  
Mark the correct answer clearly **in parentheses** at the end.

Topic: "{user_input}" """
        temperature = 0.6
        num_ctx = 150
        num_predict = 200

    else:
        raise ValueError("Unsupported task type")

    prompt = FEW_SHOT + '\n' + message

    payload = create_payload(
        target="ollama",
        model="llama3.2:latest",
        prompt=prompt,
        temperature=temperature,
        num_ctx=num_ctx,
        num_predict=num_predict
    )

    time, response = model_req(payload=payload)
    return response
