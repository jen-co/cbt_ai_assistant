# CBT AI Assistant (Full‑Stack)

A Cognitive Behavioral Therapy assistant that analyzes user input for cognitive distortions and provides context‑aware guidance. The project includes a Python backend API and a lightweight JavaScript frontend.

## Features

- **Cognitive Distortion Analysis**: Identifies common cognitive distortions in user questions
- **Context‑Aware Responses**: Can use stored data to tailor analysis
- **File Upload & OCR**: Backend utilities for handling uploads and text extraction
- **RESTful API**: Clean endpoints intended for frontend and external clients
- **Simple Frontend**: HTML/JS interface for submit/visualize results

## Project Structure

```
cbt_ai_assistant/
  backend/
    __init__.py
    app.py                  # API server (Flask)
    cbt_llm_service.py      # LLM/RAG and analysis logic
    config.py               # Configuration and environment variables
    file_storage_service.py # File save/load helpers
    models.py               # Request/response data models
    ocr_service.py          # OCR utilities
    prompts.py              # Prompt templates for analysis
    requirements.txt        # Python dependencies
    data/
      cognitive_distortions.json
    test_api.py
    test_rag_service.py
  frontend/
    index.html              # Main UI for analysis
    index.js                # Calls analyse API
    upload.html             # Optional UI for uploads (if using OCR)
    upload.js               # Calls upload/OCR endpoints
    config.js               # API base URL configuration
    style.css               # Basic styling
  README.md
```

## Prerequisites

- Python 3.9+
- pip
- [Ollama](https://ollama.com) 

## Backend: Setup & Run

1) Create and activate a virtual environment (recommended)

```bash
# From project root
python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r backend/requirements.txt
```

3) Configure environment (optional)

You can configure via environment variables or defaults in `backend/config.py`.

Common variables:

- `API_HOST` (default: `0.0.0.0`)
- `API_PORT` (default: `5000`)
- `DEBUG` (default: `False`)
- `CORS_ORIGINS` (default: `*`)
- LLM/OCR related variables as defined in `backend/config.py` (e.g., base URLs, model names)

 Ensure your local Ollama model is available (example):

```bash
ollama pull gemma3:4b
```

4) Start the API server

```bash
# From project root
python -m backend.app
```

The server runs at `http://localhost:5000` by default.

### API Endpoints

- Analyse a question

```http
POST /analyse
Content-Type: application/json

{
  "question": "Your question or issue here...",
  "use_context": false  // optional; defaults to false. true enables contextual retrieval (RAG)
}
```

Response depends on `use_context`:

- When `use_context` = true (context-enabled):

```json
{
  "result": {
    "cognitive_disortions_issue": [
      { "name": "Catastrophising", "explanation": "...", "questions": ["..."] }
    ],
    "cognitive_disortions_context": [
      { "name": "Critical Self", "explanation": "...", "questions": null }
    ],
    "comparison": "Summary comparing issue and retrieved context ..."
  },
  "source_content": "Concatenated context used in the analysis ...",
  "success": true,
  "message": null
}
```

- When `use_context` = false (no retrieval):

```json
{
  "result": {
    "cognitive_disortions_issue": [
      { "name": "Catastrophising", "explanation": "...", "questions": ["..."] }
    ]
  },
  "source_content": null,
  "success": true,
  "message": null
}
```

- Get cognitive distortions reference data

```http
GET /cognitive-distortions
```

Returns the contents of `backend/data/cognitive_distortions.json`.

- Save form submission entry (matches frontend schema)

```http
POST /save-entry
Content-Type: application/json

{
  "situationThoughts": "Work presentation: I'm worried I'll forget what to say.",
  "cognitiveDistortions": ["Catastrophising", "Mind reading"],
  "challengeAnswers": {
    "Catastrophising": [
      "It's unlikely everything will go wrong.",
      "I have a plan and slides if I forget."
    ],
    "Mind reading": [
      "I can't know what others think.",
      "Focus on delivering clearly."
    ]
  }
}
```

Response:

```json
{
  "success": true,
  "message": "Entry saved successfully",
  "entry_count": 1
}
```

The entry is saved to `backend/data/cr_entries.json` and automatically includes a server‑side `timestamp`. Additionally, the `situationThoughts` text is appended to `backend/data/full_journal_text.txt` for future context‑aware analysis.

- Upload images for OCR (optional flow)

```http
POST /upload-images
Content-Type: multipart/form-data

# form fields
images: <file[]>
```

Returns JSON with saved file names/paths.

- Process uploaded images with OCR 

```http
POST /process-images
```

Returns JSON with extracted text and length.

- Save extracted or edited text 

```http
POST /save-text
Content-Type: application/json

{
  "text": "..."
}
```

Notes:
- `use_context` on `/analyse` controls whether previously saved/derived context is used when analyzing the provided question.
- `/save-entry` enforces the frontend schema: `situationThoughts` (required), `cognitiveDistortions` (array), `challengeAnswers` (object) and adds `timestamp`.

### Testing the API

```bash
python backend/test_api.py
```

### curl examples

- Windows PowerShell/CMD

```bash
# With context
type nul > nul & curl -X POST http://localhost:5000/analyse -H "Content-Type: application/json" -d "{\"question\": \"I am feeling very anxious about my upcoming presentation.\", \"use_context\": true}"

# Without context
curl -X POST http://localhost:5000/analyse -H "Content-Type: application/json" -d "{\"question\": \"I am feeling very anxious about my upcoming presentation.\", \"use_context\": false}"

# Save entry (frontend schema)
curl -X POST http://localhost:5000/save-entry -H "Content-Type: application/json" -d "{\"situationThoughts\": \"Work presentation: I am worried I'll forget what to say.\", \"cognitiveDistortions\": [\"Catastrophising\", \"Mind reading\"], \"challengeAnswers\": {\"Catastrophising\": [\"It's unlikely everything will go wrong.\", \"I have a plan and slides if I forget.\"], \"Mind reading\": [\"I can't know what others think.\", \"Focus on delivering clearly.\"]}}"
```

- Git Bash/WSL/Linux/macOS

```bash
# With context
curl -X POST http://localhost:5000/analyse \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I am feeling very anxious about my upcoming presentation.",
    "use_context": true
  }'

# Without context
curl -X POST http://localhost:5000/analyse \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I am feeling very anxious about my upcoming presentation.",
    "use_context": false
  }'

# Save entry (frontend schema)
curl -X POST http://localhost:5000/save-entry \
  -H "Content-Type: application/json" \
  -d '{
    "situationThoughts": "Work presentation: I'\''m worried I'\''ll forget what to say.",
    "cognitiveDistortions": ["Catastrophising", "Mind reading"],
    "challengeAnswers": {
      "Catastrophising": [
        "It'\''s unlikely everything will go wrong.",
        "I have a plan and slides if I forget."
      ],
      "Mind reading": [
        "I can'\''t know what others think.",
        "Focus on delivering clearly."
      ]
    }
  }'
```

## Frontend: Setup & Run

The frontend is a static site; no build step is required.

1) Configure API base URL

Set `API_BASE_URL` (or equivalent) in `frontend/config.js` to point to your backend, e.g.:

```js
// frontend/config.js
const API_BASE_URL = "http://localhost:5000";
```

2) Serve the frontend

You can open the HTML files directly in a browser, or serve with a simple static server to avoid CORS/local file issues:

```bash
# Option A: Using Python http.server (from project root)
cd frontend
python -m http.server 8080
# Visit http://localhost:8080

# Option B: Using npx serve (Node required)
# npx --yes serve frontend -l 8080
```

3) Use the UI

- Open `index.html` to submit a question for analysis
- Open `upload.html` to upload journal pages for OCR 

## Data

- `backend/data/cognitive_distortions.json` contains reference data for cognitive distortions used by the analysis pipeline.
- `backend/data/cr_entries.json` stores form submissions with timestamps.
- If uploads are used, the backend may create an uploads directory at runtime (see `file_storage_service.py`).

## Development Notes

- Key modules
  - `app.py`: Flask routes and error handling
  - `models.py`: Pydantic models for request/response validation
  - `config.py`: Centralized configuration
  - `cbt_llm_service.py`: LLM/RAG and core analysis logic
  - `ocr_service.py`: OCR helpers (optional)
  - `file_storage_service.py`: File persistence helpers
  - `prompts.py`: Prompt composition for analysis

- Logging: The backend uses standard Python logging; enable `DEBUG=true` for verbose logs.

- Tests: See `test_api.py` and `test_rag_service.py` for examples.

## Troubleshooting

- Backend won't start: Ensure dependencies are installed and your Python venv is activated
- Cannot connect to LLM: Start Ollama (or external provider) and verify model availability
- CORS errors: Update `CORS_ORIGINS` or serve the frontend over `http://localhost`
- File upload issues: Check that backend upload routes are enabled and writable paths are configured



