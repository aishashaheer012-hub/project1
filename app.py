import os
import PyPDF2
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Use OpenAI for AI answers (you can change this later)
USE_OPENAI = True

if USE_OPENAI:
    import openai
    # Best: set this via environment variable, not in code
    openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text


def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()


def qa_from_context(context: str, question: str) -> str:
    if USE_OPENAI:
        try:
            resp = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Answer based only on the document text."},
                    {"role": "user", "content": f"Document:\n{context}\n\nQ: {question}\nA:"},
                ],
                max_tokens=512,
                temperature=0.2,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        # Fake “mock” answer if you don’t have OpenAI
        return f"(Mock mode) Your question was: {question}"


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))

    if file and file.filename.lower().endswith((".pdf", ".txt")):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        if filepath.lower().endswith(".pdf"):
            context = extract_text_from_pdf(filepath)
        elif filepath.lower().endswith(".txt"):
            context = extract_text_from_txt(filepath)

        # Show first ~10k chars of context in the template (for demo)
        return render_template("chat.html", filename=file.filename, context=context[:10000] + "...")

    return "Only PDF and TXT files allowed.", 400


@app.route("/ask", methods=["POST"])
def ask_question():
    context = request.form.get("context", "")
    question = request.form.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please type a question."})

    answer = qa_from_context(context, question)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)