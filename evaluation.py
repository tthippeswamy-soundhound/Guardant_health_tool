from pydantic import BaseModel, Field
from typing import Optional


class EvaluationResult(BaseModel):
    # Audio file metadata
    audio_filename: str = Field(default="", description="Name of the uploaded audio file")
    transcript: str = Field(default="", description="Full transcript of the call")

    # Human interaction fields
    user_hangup: str = Field(default="No", description="Yes/No - if the user hangs up the call")
    user_hangup_reason: str = Field(default="", description="Who hung up (Amelia or human) and reason")
    call_ended: str = Field(default="No", description="Yes/No - if Amelia ends or disconnects the call")
    call_ended_reason: str = Field(default="", description="Reason Amelia ended the call")
    human_picked_up: str = Field(default="No", description="Yes/No - if the user received the call")
    human_rpc_confirmed: str = Field(default="No", description="Yes/No - if the user confirmed their identity (right party confirm)")
    number_of_times_amelia_asked_for_rpc: int = Field(default=0, description="Count of times Amelia tried user identification")
    human_related_party_or_unavailable: str = Field(default="No", description="Yes/No - if patient is unavailable or someone else picked up")
    human_hung_up_before_rpc: str = Field(default="No", description="Yes/No - if user hung up immediately or during identification question")
    human_blood_draw_info_given: str = Field(default="No", description="Yes/No - if the user provided information for the blood draw question")
    human_hung_up_before_blood_draw_question: str = Field(default="No", description="Yes/No - if user hung up before/during blood draw question")
    user_requested_additional_assistance: str = Field(default="No", description="Yes/No - if user requested additional help")
    user_additional_assistance_question: str = Field(default="", description="The question the user asked for additional assistance")
    amelia_provided_additional_assistance: str = Field(default="No", description="Yes/No - if Amelia provided the requested assistance")
    amelia_additional_assistance_answer: str = Field(default="", description="The answer Amelia gave for additional assistance")
    escalation_requested: str = Field(default="No", description="Yes/No - if the user requests a representative")
    callback_requested: str = Field(default="No", description="Yes/No - if the user requests a callback")
    amelia_acknowledged_callback_escalate_request: str = Field(default="No", description="Yes/No - if Amelia responded to callback/escalation request")

    # Voicemail / IVR fields
    voicemail_connected: str = Field(default="No", description="Yes/No - if the call reached a voicemail machine")
    ivr_connected: str = Field(default="No", description="Yes/No - if the call reached an IVR")
    voicemail_successful: str = Field(default="No", description="Yes/No - if voicemail was left successfully")
    voicemail_failure_reason: str = Field(default="", description="Reason for voicemail failure: spoke before beep, VM not setup, Mailbox full, etc.")
    prescreening_connected: str = Field(default="No", description="Yes/No - if the call went for prescreening")
    prescreening_successful: str = Field(default="No", description="Yes/No - if Amelia handled prescreening successfully")

    # Audio quality fields
    user_requested_spanish: str = Field(default="No", description="Yes/No - if the user asks for Spanish instructions")
    silence_detected: str = Field(default="No", description="Yes/No - more than 10 seconds of silence detected")
    no_audio_available: str = Field(default="No", description="Yes/No - if the recording is a blank call")

    # Misc / quality fields
    amelia_not_replying_to_hello: str = Field(default="No", description="Yes/No - if Amelia failed to greet or respond to user hello")
    amelia_stayed_on_call_during_silence: str = Field(default="No", description="Yes/No - if Amelia stayed on call for extended silence")
    amelia_pronunciation_correct: str = Field(default="Yes", description="Yes/No - if Amelia pronounced her name and Guardant Health correctly")
    amelia_pronunciation_notes: str = Field(default="", description="Notes on pronunciation issues if any")
    user_amelia_vm_amelia_overlap: str = Field(default="No", description="Yes/No - if there is overlap between user Amelia and VM Amelia")
    additional_comments: str = Field(default="", description="Any additional observations not covered by other fields")

    # Call classification (from CSV prompt)
    call_type: str = Field(default="", description="Human, Voicemail, or Prescreening")
    call_outcome: str = Field(default="", description="Success or Failure with brief reason")
    patient_name: str = Field(default="", description="Confirmed patient name from the call")
    blood_draw_completed: str = Field(default="No", description="Yes/No - if patient confirmed blood draw completion")
