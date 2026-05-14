# Guardant Health Audio Evaluator

A FastAPI service that evaluates audio calls between users and Amelia (Guardant Health voice agent).

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file:
   ```
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. Run the server:
   ```
   uvicorn main:app --reload --port 8000
   ```

4. Open API docs: http://localhost:8000/docs

## Endpoints

### `POST /evaluate`
Upload an audio file for evaluation.

- **Input**: Multipart form with `file` field (mp3, wav, m4a, ogg, flac, webm, mp4, mpeg, mpga)
- **Output**: JSON with full structured evaluation
- **Side effect**: Appends results to `output/evaluations.csv`

### `POST /evaluate/transcript`
Evaluate a text transcript directly (no audio needed).

- **Input**: JSON body `{ "transcript": "...", "filename": "optional" }`
- **Output**: Same structured evaluation

### `GET /health`
Health check.

## Output Fields

Each evaluation produces these fields (saved to CSV):

| Field | Type | Description |
|-------|------|-------------|
| audio_filename | text | Name of uploaded file |
| call_type | Human/Voicemail/Prescreening | Type of call |
| call_outcome | Success/Failure | Overall outcome |
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
| voicemail_failure_reason | text | Reason VM failed |
| prescreening_connected | Yes/No | Reached prescreening |
| prescreening_successful | Yes/No | Prescreening handled successfully |
| user_requested_spanish | Yes/No | User asked for Spanish |
| silence_detected | Yes/No | >10 seconds of silence |
| no_audio_available | Yes/No | Blank recording |
| amelia_not_replying_to_hello | Yes/No | Amelia failed to respond to hello |
| amelia_stayed_on_call_during_silence | Yes/No | Amelia stayed on during long silence |
| amelia_pronunciation_correct | Yes/No | Correct pronunciation throughout |
| amelia_pronunciation_notes | text | Pronunciation issues |
| user_amelia_vm_amelia_overlap | Yes/No | Overlap confusion |
| additional_comments | text | Other observations |
| transcript | text | Full call transcript |
