
from flask import Flask, request, jsonify, render_template_string
from document_processor import load_documents, search_documents
import requests

app = Flask(__name__)

# Load university documents
documents = load_documents()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Chula Student Assistant</title>
</head>
<body>
    <h1>Chula Student Assistant</h1>
    <p>Ask questions about Chulalongkorn University.</p>

    <form id="chat-form">
        <input id="question" placeholder="Ask a question..." required>
        <button type="submit">Send</button>
    </form>

    <div id="answer"></div>

    <script>
        document.getElementById("chat-form").onsubmit = async function(e) {
            e.preventDefault();
            const question = document.getElementById("question").value;

            const response = await fetch("/ask", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({question})
            });

            const data = await response.json();
            document.getElementById("answer").innerText = data.answer;
        };
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "")
    context = search_documents(question, documents)

    prompt = f"""
    Answer the question using the university information below.
    If the information is not available, say so.

    University information:
    {context}

    Question: {question}
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        answer = response.json()["response"]
    except requests.RequestException:
        answer = "Could not connect to Ollama. Please check that Ollama is running."

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
