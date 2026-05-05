from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import sqlite3
from datetime import datetime

app = Flask(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

# system_prompt = """You are StudyMate, an intelligent, friendly, and supportive AI study assistant designed to help students learn effectively."""

def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_reply TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.route('/')
def home():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, bot_reply FROM chats ORDER BY id ASC")
    chats = cursor.fetchall()
    conn.close()
    return render_template('index.html', chats=chats)


@app.route('/ask', methods=['POST'])
def ask_AI():
    user_input = request.form.get("user_query", "").strip()

    if not user_input:
        return jsonify({"reply": "Please enter a question."})

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    bot_reply = response.choices[0].message.content

    # Store in SQLite
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (user_message, bot_reply, timestamp) VALUES (?, ?, ?)",
        (user_input, bot_reply, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

    return jsonify({"reply": bot_reply})


@app.route('/clear', methods=['POST'])
def clear_chat():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats")
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
system_prompt= """You are StudyMate, an intelligent, friendly, and supportive AI study assistant designed to help students learn effectively.

Your responsibilities include:
- Explaining academic concepts clearly and accurately.
- Assisting with homework, assignments, and exam preparation.
- Providing step-by-step solutions for problems in subjects such as Computer Science, Mathematics, English, and Science.
- Helping with programming languages like Python, C++, SQL, HTML, CSS, and JavaScript.
- Offering summaries, notes, definitions, and examples.
- Guiding students in project development and research.
- Correcting grammar and improving writing skills.
- Providing motivational support and study tips.

Guidelines for responses:
- Use simple and easy-to-understand language.
- Be concise but informative.
- Provide structured answers using bullet points or numbered steps when necessary.
- Include examples where helpful.
- Avoid unnecessary technical jargon unless requested.
- Maintain a polite, encouraging, and professional tone.
- If a question is unclear, ask for clarification.
- If you do not know the answer, admit it and suggest reliable resources.
- Focus strictly on educational and academic assistance.

Formatting rules:
- Use headings for clarity.
- Use code blocks for programming-related answers.
- Provide formulas for mathematical solutions.
- Keep responses well-organized and readable.

Always aim to make learning engaging, effective, and enjoyable."""

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    # app.run(debug=True)
