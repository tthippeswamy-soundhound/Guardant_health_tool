import csv
import os
from evaluation import EvaluationResult


OUTPUT_CSV = os.path.join("output", "evaluations.csv")

FIELDNAMES = [
    "audio_filename", "call_type", "call_outcome", "patient_name", "blood_draw_completed",
    "human_picked_up", "human_rpc_confirmed", "number_of_times_amelia_asked_for_rpc",
    "human_related_party_or_unavailable", "human_hung_up_before_rpc",
    "human_blood_draw_info_given", "human_hung_up_before_blood_draw_question",
    "user_requested_additional_assistance", "user_additional_assistance_question",
    "amelia_provided_additional_assistance", "amelia_additional_assistance_answer",
    "escalation_requested", "callback_requested", "amelia_acknowledged_callback_escalate_request",
    "user_hangup", "user_hangup_reason", "call_ended", "call_ended_reason",
    "voicemail_connected", "ivr_connected", "voicemail_successful", "voicemail_failure_reason",
    "prescreening_connected", "prescreening_successful",
    "user_requested_spanish", "silence_detected", "no_audio_available",
    "amelia_not_replying_to_hello", "amelia_stayed_on_call_during_silence",
    "amelia_pronunciation_correct", "amelia_pronunciation_notes",
    "user_amelia_vm_amelia_overlap", "additional_comments",
    "transcript"
]


def append_to_csv(result: EvaluationResult) -> str:
    """Append an evaluation result to the CSV file. Creates file with headers if it doesn't exist."""
    os.makedirs("output", exist_ok=True)
    file_exists = os.path.isfile(OUTPUT_CSV)

    with open(OUTPUT_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({field: getattr(result, field, "") for field in FIELDNAMES})

    return OUTPUT_CSV
