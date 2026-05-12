# Document Q&A App

A simple AI‑based web app where users can:

- Upload a PDF or text file
- Ask questions about the document
- Get AI‑generated answers based only on the uploaded content

## Tech stack

- Backend: Python + Flask
- PDF/text extraction: PyPDF2
- Answer generation: OpenAI API (configurable)

## Setup

1. Clone this repo:
   ```bash
   git clone <your-repo-url>
   cd doc-qa-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key (Linux/macOS):
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
   Or on Windows (Command Prompt):
   ```cmd
   set OPENAI_API_KEY=sk-...
   ```

4. Run the app:
   ```bash
   python app.py
   ```

5. Open your browser at `http://127.0.0.1:5000`.

## How to use

1. Upload a PDF or `.txt` file.
2. The app redirects you to the chat page.
3. Type questions (e.g., "Summarize this", "What is the main idea?").
4. The AI answers using the document text.

## Notes

- Uploaded files are stored temporarily in `uploads/`.
- For production, add file‑size limits, cleanup scripts, and secure config.