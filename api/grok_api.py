import os
from groq import Groq

def get_groq_response(prompt, model="llama3-8b-8192"):
    """
    Sends a user prompt to the Groq API and returns the response text.
    Raises ValueError if the API key is not set.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model
    )
    return completion.choices[0].message.content
