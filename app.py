import os
import uuid
import PyPDF2
from flask import Flask, render_template, request, jsonify, redirect, url_for
from google import genai

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()


def qa_from_context(context: str, question: str) -> str:
    try:
        prompt = f"""
You are a helpful assistant that answers only from the document content.

Document:
{context}

Question:
{question}

Rules:
- Answer only using the document.
- If the answer is not in the document, say you could not find it.
- Keep the answer short and clear.
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip() if response.text else "No answer returned."
    except Exception as e:
        return f"Error: {str(e)}"


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
        safe_name = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        file.save(filepath)

        if filepath.lower().endswith(".pdf"):
            context = extract_text_from_pdf(filepath)
        else:
            context = extract_text_from_txt(filepath)

        if not context.strip():
            context = "No text could be extracted from the uploaded file."

        return render_template(
            "chat.html",
            filename=file.filename,
            context=context[:20000]
        )

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