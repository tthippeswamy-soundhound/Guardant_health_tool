import os
import json
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from transcriber import transcribe_audio
from evaluator import evaluate_transcript
from csv_writer import append_to_csv

app = FastAPI(
    title="Guardant Health Audio Evaluator",
    description="Evaluate audio calls between users and Amelia (Guardant Health voice agent)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_FORMATS = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".ogg", ".flac"}
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "prompt_config.json")


@app.get("/")
def root():
    return {"message": "Guardant Health Audio Evaluator API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/config/prompt")
def get_prompt_config():
    """Return the current prompt configuration."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.put("/config/prompt")
def update_prompt_config(body: dict):
    """Update the prompt configuration (system_prompt, main_prompt, field_descriptions)."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    if "system_prompt" in body:
        config["system_prompt"] = body["system_prompt"]
    if "main_prompt" in body:
        if "{transcript}" not in body["main_prompt"]:
            raise HTTPException(status_code=400, detail="main_prompt must contain the {transcript} placeholder")
        config["main_prompt"] = body["main_prompt"]
    if "field_descriptions" in body:
        config["field_descriptions"].update(body["field_descriptions"])
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    return {"status": "saved", "config": config}


@app.get("/results/csv")
def get_csv_data():
    """Return all evaluation results from the CSV as JSON."""
    csv_path = os.path.join("output", "evaluations.csv")
    if not os.path.isfile(csv_path):
        return {"rows": []}
    import csv
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return {"rows": rows}


@app.post("/evaluate")
async def evaluate_audio(file: UploadFile = File(...)):
    """
    Upload an audio file of a call between a user and Amelia.
    Returns structured evaluation and saves results to CSV.

    Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg, flac
    """
    # Validate file extension
    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    # Save upload to temp file
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    try:
        # Step 1: Transcribe
        transcript = transcribe_audio(tmp_path)

        # Step 2: Evaluate transcript
        result = evaluate_transcript(transcript)
        result.audio_filename = file.filename or "unknown"

        # Step 3: Save to CSV
        csv_path = append_to_csv(result)

        return JSONResponse(content={
            "status": "success",
            "csv_saved_to": csv_path,
            "evaluation": result.model_dump()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=str(e))


    finally:
        os.unlink(tmp_path)


@app.post("/evaluate/transcript")
async def evaluate_text_transcript(body: dict):
    """
    Evaluate a text transcript directly (no audio file needed).
    Body: { "transcript": "...", "filename": "optional_name.txt" }
    """
    transcript = body.get("transcript", "").strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="'transcript' field is required and cannot be empty")

    result = evaluate_transcript(transcript)
    result.audio_filename = body.get("filename", "text_input")

    csv_path = append_to_csv(result)

    return JSONResponse(content={
        "status": "success",
        "csv_saved_to": csv_path,
        "evaluation": result.model_dump()
    })
