import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the OpenAI client
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Warning: OPENAI_API_KEY environment variable not set.")
except Exception as e:
    print(f"Error setting up OpenAI client: {e}")

def summarize_text(text: str) -> str:
    """
    Summarizes the given text using the OpenAI API.

    Args:
        text (str): The email content to be summarized.

    Returns:
        str: The summarized text, or an error message if it fails.
    """
    if not openai.api_key:
        return "Error: OpenAI API key is not configured."

    # A clear and direct prompt for the AI model
    prompt = (
        "Please summarize the following email content concisely in one or two paragraphs. "
        "Focus on the main points and any required actions. "
        "The summary will be forwarded to another person.\n\n"
        f"Email Content:\n---\n{text}\n---\n\nSummary:"
    )

    try:
        # Using the ChatCompletion endpoint
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5, # A bit of creativity but still factual
            max_tokens=250
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return f"Error: Could not generate summary. Details: {e}"
