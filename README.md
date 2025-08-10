Here’s the README content in plain text format (with Markdown syntax preserved) — you can copy and save it as `README.txt`:

````
# Gemini System Prompt Comparison Tool

A Flask-based web application to compare outputs from Google's Gemini API using **two different system prompts**.  
This tool runs each input prompt against both system prompts, captures the outputs, and shows differences side-by-side with highlighted changes.

---

## Features

- Upload **two system prompt `.txt` files**.
- Upload one or more **input `.txt` files**.
- Select Gemini model from dropdown.
- Configure generation parameters:
  - Temperature
  - Top P
  - Top K
- Runs all inputs against both system prompts.
- Compares outputs:
  - Shows "Match" if identical.
  - Shows a diff view highlighting added/removed lines if different.
- Simple HTML interface (no external CSS required).

---

## Requirements

- Python 3.8+
- Google Generative AI Python SDK
- Flask
- python-dotenv
- Werkzeug

Install dependencies:

```bash
pip install flask python-dotenv google-generativeai
````

---

## Setup

1. **Clone the repository** (or copy files locally):

2. **Install dependencies**:

3. **Create `.env` file** in the project root:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

   > Replace `your_api_key_here` with your actual Google Gemini API key.

4. **Ensure folder structure**:

   ```
   project/
   ├── app.py
   ├── templates/
   │   └── index.html
   ├── uploads/  # Will be created automatically
   └── .env
   ```

---

## Usage

1. **Run the app**:

   ```bash
   python app.py
   ```

2. **Open your browser**:

   ```
   http://127.0.0.1:5000
   ```

3. **In the UI**:

   * Enter your Gemini API Key (or set in `.env`).
   * Select a Gemini model.
   * Upload:

     * `System Message 1` (TXT)
     * `System Message 2` (TXT)
     * One or more `Input Message` files (TXT)
   * Adjust parameters (optional).
   * Click **Submit**.

4. **View results**:

   * Outputs for each system prompt are shown.
   * Comparison results:

     * ✅ **Match** — outputs are identical.
     * ⚠ **Mismatch** — differences are highlighted.

---

## How It Works

1. **Two chat sessions** are created per input:

   * Chat 1 uses System Message 1.
   * Chat 2 uses System Message 2.
2. Both chats process the same input message.
3. Outputs are compared:

   * If identical: mark as "Match".
   * If different: generate an HTML diff using `difflib`.
4. Results are displayed in a table.

---

## Notes

* Only `.txt` files are allowed for system and input messages.
* Max upload size: **16 MB** per file.
* This tool is for testing purposes; avoid exposing sensitive API keys.
* Diff highlights:

  * Green: Added lines
  * Red: Removed lines
  * Grey: Change indicators

Do you want me to also make a **ready-to-download `README.txt`** file from this so you don’t have to copy it manually?
```
