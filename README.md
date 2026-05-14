# Guardant Health Audio Evaluator

An AI-powered tool to evaluate audio calls between patients and **Amelia** (Guardant Health's voice agent). Upload a call recording, get a fully structured evaluation across 40+ fields, and explore results via an interactive dashboard.

---

## Architecture

```
Guardant_health_tool/
├── main.py               # FastAPI backend
├── evaluator.py          # GPT-powered transcript analysis
├── transcriber.py        # OpenAI Whisper transcription
├── evaluation.py         # Pydantic output model (all fields)
├── csv_writer.py         # Appends results to output CSV
├── streamlit_app.py      # Streamlit frontend (3 pages)
├── prompt_config.json    # Editable prompt & field descriptions
├── output/
│   └── evaluations.csv   # Auto-created results store
├── requirements.txt
└── .env.example
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and set your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

### 3. Start the backend
```bash
uvicorn main:app --reload --port 8000
```

### 4. Start the frontend (separate terminal)
```bash
streamlit run streamlit_app.py
```

- **Frontend**: http://localhost:8501  
- **API docs**: http://localhost:8000/docs

---

## Frontend Pages

### 🎙️ Evaluate Call
- Upload an audio file (mp3, wav, m4a, ogg, flac, webm, mp4) **or** paste a raw transcript
- Results displayed in grouped sections with summary cards (call type, outcome, patient name, blood draw status)
- Full transcript viewer and raw JSON export

### ⚙️ Prompt Settings
- Edit the **system prompt** and **main evaluation prompt** sent to GPT — changes take effect immediately on the next evaluation
- Edit the **description for every field** — these guide how the AI interprets and fills each value
- All changes are persisted to `prompt_config.json`

### 📊 Dashboard
- KPI cards: total calls, success rate, call type breakdown
- Charts: call type pie, outcome bar, key field % Yes, RPC attempt histogram, voicemail failure breakdown
- Full sortable/filterable data table with CSV download

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/evaluate` | Upload audio file → transcribe → evaluate → save CSV |
| `POST` | `/evaluate/transcript` | Evaluate a raw text transcript directly |
| `GET` | `/config/prompt` | Get current prompt config (system, main, field descriptions) |
| `PUT` | `/config/prompt` | Update prompt config |
| `GET` | `/results/csv` | Return all evaluation results as JSON |
| `GET` | `/health` | Health check |

### `POST /evaluate`
```bash
curl -X POST http://localhost:8000/evaluate \
  -F "file=@call_recording.mp3"
```

### `POST /evaluate/transcript`
```bash
curl -X POST http://localhost:8000/evaluate/transcript \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Amelia: Hello, this is Amelia...", "filename": "test_call"}'
```

### `PUT /config/prompt`
```bash
curl -X PUT http://localhost:8000/config/prompt \
  -H "Content-Type: application/json" \
  -d '{"main_prompt": "Your updated prompt here. Must include {transcript}."}'
```

---

## Output Fields

All evaluations are saved to `output/evaluations.csv` with these fields:

| Field | Type | Description |
|-------|------|-------------|
| audio_filename | text | Name of uploaded file |
| call_type | Human/Voicemail/Prescreening | Type of call |
| call_outcome | Success/Failure + reason | Overall outcome |
| patient_name | text | Confirmed patient name |
| blood_draw_completed | Yes/No | Patient confirmed blood draw |
| human_picked_up | Yes/No | Human answered the call |
| human_rpc_confirmed | Yes/No | Right Party Confirmed |
| number_of_times_amelia_asked_for_rpc | count | RPC attempts |
| human_related_party_or_unavailable | Yes/No | Patient unavailable or wrong person |
| human_hung_up_before_rpc | Yes/No | Hung up before identity check |
| human_blood_draw_info_given | Yes/No | Blood draw info provided |
| human_hung_up_before_blood_draw_question | Yes/No | Hung up before blood draw question |
| user_requested_additional_assistance | Yes/No | User asked extra questions |
| user_additional_assistance_question | text | The extra question asked |
| amelia_provided_additional_assistance | Yes/No | Amelia answered extra questions |
| amelia_additional_assistance_answer | text | Amelia's answer |
| escalation_requested | Yes/No | User requested human rep |
| callback_requested | Yes/No | User requested callback |
| amelia_acknowledged_callback_escalate_request | Yes/No | Amelia acknowledged request |
| user_hangup | Yes/No | User hung up |
| user_hangup_reason | text | Who hung up and why |
| call_ended | Yes/No | Amelia ended call |
| call_ended_reason | text | Why Amelia ended call |
| voicemail_connected | Yes/No | Reached voicemail |
| ivr_connected | Yes/No | Reached IVR |
| voicemail_successful | Yes/No | Voicemail left successfully |
| voicemail_failure_reason | text | Reason VM failed (spoke before beep / VM not setup / Mailbox full / etc.) |
| prescreening_connected | Yes/No | Reached prescreening |
| prescreening_successful | Yes/No | Prescreening handled successfully |
| user_requested_spanish | Yes/No | User asked for Spanish |
| silence_detected | Yes/No | >10 seconds of silence |
| no_audio_available | Yes/No | Blank recording |
| amelia_not_replying_to_hello | Yes/No | Amelia failed to respond to hello |
| amelia_stayed_on_call_during_silence | Yes/No | Amelia stayed on during long silence |
| amelia_pronunciation_correct | Yes/No | Correct pronunciation throughout |
| amelia_pronunciation_notes | text | Pronunciation issues noted |
| user_amelia_vm_amelia_overlap | Yes/No | Overlap/confusion between user Amelia and VM Amelia |
| additional_comments | text | Other observations |
| transcript | text | Full call transcript |

---

## Prompt Customization

All prompts and field descriptions are stored in `prompt_config.json` and can be edited:

- **Via UI**: Go to the ⚙️ Prompt Settings page in the Streamlit app
- **Via API**: `PUT /config/prompt` with any of `system_prompt`, `main_prompt`, or `field_descriptions`
- **Directly**: Edit `prompt_config.json` and restart the server

> ⚠️ `main_prompt` must always contain the `{transcript}` placeholder.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + Uvicorn |
| Transcription | OpenAI Whisper (`whisper-1`) |
| Evaluation | OpenAI GPT (`gpt-5.4-mini`) with structured output |
| Frontend | Streamlit |
| Charts | Plotly |
| Output | CSV (auto-created) |

