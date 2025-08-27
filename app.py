from flask import Flask, render_template, request
import google.generativeai as genai
import re
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configure Gemini API (⚠️ best practice: move API key into Railway "Variables" tab)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyCAyJGft7lbkyLZ4GIlP9RX5QjHQz8dD-U"))

app = Flask(__name__)

# Database setup (SQLite for simplicity)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///journal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

with app.app_context():
    db.drop_all()   # delete all old tables
    db.create_all() # recreate with session_id column

# Database model
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    analysis = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Function to analyze entry
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

    # Clean text
    cleaned_text = re.sub(r"\*\*(.*?)\*\*", r"\1", response.text)
    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

    numbered = []
    for i, line in enumerate(lines, 1):
        if re.match(r"^\d+\.", line):
            numbered.append(line)
        else:
            numbered.append(f"{i}. {line}")

    return "<br>".join(numbered)

# Routes
@app.route("/", methods=["GET", "POST"])
def home():
    analysis = None
    if request.method == "POST":
        entry = request.form["entry"]
        analysis = analyze_journal_entry(entry)

        # Save to database
        new_entry = JournalEntry(text=entry, analysis=analysis)
        db.session.add(new_entry)
        db.session.commit()

    # Show all saved entries (latest first)
    entries = JournalEntry.query.order_by(JournalEntry.timestamp.desc()).all()
    return render_template("index.html", analysis=analysis, entries=entries)

# Create tables on first run
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
