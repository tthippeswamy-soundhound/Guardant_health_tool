import os
import json
from openai import OpenAI
from evaluation import EvaluationResult

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "prompt_config.json")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_transcript(transcript: str) -> EvaluationResult:
    """Use structured output parsing to analyze the transcript and extract evaluation fields."""
    try:
        config = load_config()
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        prompt = config["main_prompt"].format(transcript=transcript)

        response = client.responses.parse(
            model="gpt-5.4-mini",
            input=[
                {"role": "system", "content": config["system_prompt"]},
                {"role": "user", "content": prompt},
            ],
            text_format=EvaluationResult,
        )

        result = response.output_parsed
        result.transcript = transcript

        return result
    except Exception as e:
        raise RuntimeError(f"Error during evaluation: {str(e)}")
