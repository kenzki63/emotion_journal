import google.generativeai as genai

genai.configure(api_key="AIzaSyCAyJGft7lbkyLZ4GIlP9RX5QjHQz8dD-U")

import google.generativeai as genai

def analyze_journal_entry(entry: str):
    model = genai.GenerativeModel("gemini-1.5-flash")  
    prompt = f"""
    The user wrote this journal entry: "{entry}"

    Task:
    1. Identify the main emotions expressed.
    2. Summarize the mood in one short sentence.
    3. Suggest a gentle coping strategy or encouragement if emotions are negative.
    4. If positive, suggest how the user can keep the good mood.
    """
    response = model.generate_content(prompt)
    return response.text
