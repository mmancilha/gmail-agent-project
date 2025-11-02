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
    """
    if not openai.api_key:
        return "Error: OpenAI API key is not configured."

    prompt = (
        "Please summarize the following email content concisely in one or two paragraphs. "
        "Focus on the main points and any required actions. "
        "The summary will be forwarded to another person.\n\n"
        f"Email Content:\n---\n{text}\n---\n\nSummary:"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=250
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return f"Error: Could not generate summary. Details: {e}"

def generate_reply_text(original_sender: str, original_subject: str, original_content: str) -> str:
    """
    Generates a context-aware reply to an email by analyzing its sentiment and intent.
    Returns 'IGNORE' for promotional content.
    """
    if not openai.api_key:
        return "Error: OpenAI API key is not configured."

    sender_name = original_sender.split('<')[0].strip().title()

    # --- NEW, ADVANCED PROMPT WITH SENTIMENT ANALYSIS ---
    prompt = (
        "You are a highly intelligent professional assistant. Your task is to analyze the email below and generate an appropriate response based on a multi-step thought process.\n\n"
        "**Thought Process:**\n"
        "1.  **Analyze Intent:** First, determine if the email is a promotional message, newsletter, or automated notification. If so, your ONLY output must be the single word: 'IGNORE'.\n"
        "2.  **Analyze Sentiment & Urgency:** If it's a genuine email, classify its sentiment (e.g., Positive, Negative, Neutral) and its urgency (e.g., Urgent, Important, Normal).\n"
        "3.  **Draft Reply:** Based on your analysis, draft a reply that matches the tone. \n"
        "    - For **Positive/Urgent** news (like a job offer or congratulations), the tone should be enthusiastic and grateful.\n"
        "    - For **Neutral/Important** inquiries (like a meeting request), the tone should be professional and helpful.\n"
        "    - For **Negative** feedback, the tone should be empathetic and reassuring.\n"
        "4.  **Final Polish:** Ensure the reply is concise, professional, and does not include any placeholder signature like '[Your Name]'.\n\n"
        "--- START ANALYSIS ---\n"
        f"**Original Sender:** {original_sender}\n"
        f"**Original Subject:** {original_subject}\n"
        f"**Original Email Content:**\n{original_content}\n"
        "--- END ANALYSIS ---\n\n"
        f"**Draft a suitable reply to {sender_name}:**"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional AI assistant that analyzes emails for sentiment and urgency before drafting context-aware replies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7, 
            max_tokens=200
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return f"Error: Could not generate reply. Details: {e}"