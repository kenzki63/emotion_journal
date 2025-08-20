from flask import Flask, render_template, request
import google.generativeai as genai
import re

# configure API
genai.configure(api_key="AIzaSyCAyJGft7lbkyLZ4GIlP9RX5QjHQz8dD-U")  # replace with your real key

app = Flask(__name__)

def analyze_journal_entry(entry: str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    The user wrote this journal entry: "{entry}"

    Task:
    1. Identify the main emotions expressed.
    2. Summarize the mood in one short sentence.
    3. Suggest a gentle coping strategy or encouragement if emotions are negative.
    4. If positive, suggest how the user can keep the good mood.

    Format the response clearly as numbered points.
    """
    response = model.generate_content(prompt)

    # Remove Markdown bold **text**
    cleaned_text = re.sub(r"\*\*(.*?)\*\*", r"\1", response.text)

    # Ensure each line becomes a numbered bullet (if not already)
    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]
    numbered = []
    for i, line in enumerate(lines, 1):
        # Avoid double-numbering if AI already added "1.", "2.", etc.
        if re.match(r"^\d+\.", line):
            numbered.append(line)
        else:
            numbered.append(f"{i}. {line}")
    return "<br>".join(numbered)  # return with <br> for HTML rendering

@app.route("/", methods=["GET", "POST"])
def home():
    analysis = None
    if request.method == "POST":
        entry = request.form["entry"]
        analysis = analyze_journal_entry(entry)
    return render_template("index.html", analysis=analysis)

if __name__ == "__main__":
    app.run(debug=True)