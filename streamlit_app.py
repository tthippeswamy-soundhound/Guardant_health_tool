import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Guardant Health Call Evaluator",
    page_icon="🏥",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.image("https://www.guardanthealth.com/wp-content/themes/guardant/images/logo.svg",
                 use_column_width=True, output_format="auto")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🎙️ Evaluate Call", "⚙️ Prompt Settings", "📊 Dashboard"])

# ── Helper ─────────────────────────────────────────────────────────────────────
def api_ok():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Evaluate Call
# ══════════════════════════════════════════════════════════════════════════════
if page == "🎙️ Evaluate Call":
    st.title("🎙️ Evaluate a Call Recording")

    if not api_ok():
        st.error("⚠️ Backend API is not reachable at `http://localhost:8000`. Please start the FastAPI server.")
        st.stop()

    tab_audio, tab_text = st.tabs(["Upload Audio File", "Paste Transcript"])

    # ── Audio Upload Tab ───────────────────────────────────────────────────────
    with tab_audio:
        st.markdown("Upload an audio recording of a call between a patient and Amelia.")
        audio_file = st.file_uploader(
            "Choose an audio file",
            type=["mp3", "mp4", "wav", "m4a", "ogg", "flac", "webm", "mpeg", "mpga"],
            help="Supported: mp3, mp4, wav, m4a, ogg, flac, webm"
        )

        if audio_file:
            st.audio(audio_file)
            if st.button("🚀 Evaluate Audio", type="primary", key="eval_audio"):
                with st.spinner("Transcribing and evaluating... this may take a minute ⏳"):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/evaluate",
                            files={"file": (audio_file.name, audio_file.getvalue(), audio_file.type)},
                            timeout=180,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success(f"✅ Evaluation complete! Saved to `{data['csv_saved_to']}`")
                            st.session_state["last_result"] = data["evaluation"]
                        else:
                            st.error(f"❌ Error {resp.status_code}: {resp.json().get('detail', resp.text)}")
                    except Exception as e:
                        st.error(f"❌ Request failed: {e}")

    # ── Transcript Tab ─────────────────────────────────────────────────────────
    with tab_text:
        st.markdown("Paste a call transcript directly for evaluation (no audio needed).")
        transcript_text = st.text_area("Transcript", height=250, placeholder="Amelia: Hello, this is Amelia from Guardant Health...")
        fname = st.text_input("Optional filename tag", value="manual_input")
        if st.button("🚀 Evaluate Transcript", type="primary", key="eval_text"):
            if not transcript_text.strip():
                st.warning("Please enter a transcript first.")
            else:
                with st.spinner("Evaluating transcript..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/evaluate/transcript",
                            json={"transcript": transcript_text, "filename": fname},
                            timeout=120,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success(f"✅ Evaluation complete! Saved to `{data['csv_saved_to']}`")
                            st.session_state["last_result"] = data["evaluation"]
                        else:
                            st.error(f"❌ Error {resp.status_code}: {resp.json().get('detail', resp.text)}")
                    except Exception as e:
                        st.error(f"❌ Request failed: {e}")

    # ── Results Display ────────────────────────────────────────────────────────
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        st.divider()
        st.subheader("📋 Evaluation Results")

        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Call Type", result.get("call_type", "—"))
        outcome = result.get("call_outcome", "—")
        col2.metric("Outcome", "✅ Success" if "Success" in outcome else "❌ Failure")
        col3.metric("Patient", result.get("patient_name") or "Unknown")
        col4.metric("Blood Draw Done", result.get("blood_draw_completed", "No"))

        # Grouped field sections
        sections = {
            "👤 Human Interaction": [
                "human_picked_up", "human_rpc_confirmed", "number_of_times_amelia_asked_for_rpc",
                "human_related_party_or_unavailable", "human_hung_up_before_rpc",
                "human_blood_draw_info_given", "human_hung_up_before_blood_draw_question",
                "escalation_requested", "callback_requested",
                "amelia_acknowledged_callback_escalate_request",
            ],
            "📞 Call End": [
                "user_hangup", "user_hangup_reason", "call_ended", "call_ended_reason",
            ],
            "🆘 Additional Assistance": [
                "user_requested_additional_assistance", "user_additional_assistance_question",
                "amelia_provided_additional_assistance", "amelia_additional_assistance_answer",
            ],
            "📨 Voicemail / IVR": [
                "voicemail_connected", "ivr_connected", "voicemail_successful",
                "voicemail_failure_reason", "prescreening_connected", "prescreening_successful",
            ],
            "🔇 Audio Quality": [
                "user_requested_spanish", "silence_detected", "no_audio_available",
            ],
            "🔍 Amelia Quality": [
                "amelia_not_replying_to_hello", "amelia_stayed_on_call_during_silence",
                "amelia_pronunciation_correct", "amelia_pronunciation_notes",
                "user_amelia_vm_amelia_overlap",
            ],
            "💬 Comments": ["additional_comments"],
        }

        for section_title, fields in sections.items():
            with st.expander(section_title, expanded=True):
                rows = []
                for f in fields:
                    val = result.get(f, "")
                    label = f.replace("_", " ").title()
                    rows.append({"Field": label, "Value": val if val != "" else "—"})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with st.expander("📝 Full Transcript"):
            st.text(result.get("transcript", "No transcript available."))

        with st.expander("🔧 Raw JSON"):
            st.json(result)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Prompt Settings
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Prompt Settings":
    st.title("⚙️ Prompt Settings")

    if not api_ok():
        st.error("⚠️ Backend API is not reachable. Please start the FastAPI server.")
        st.stop()

    try:
        config = requests.get(f"{API_BASE}/config/prompt", timeout=5).json()
    except Exception as e:
        st.error(f"Failed to load config: {e}")
        st.stop()

    tab_main, tab_fields = st.tabs(["Main Prompt", "Field Descriptions"])

    # ── Main Prompt Tab ────────────────────────────────────────────────────────
    with tab_main:
        st.markdown("""
        Edit the **system prompt** and **main evaluation prompt** sent to GPT.
        > ⚠️ The main prompt **must** contain `{transcript}` — this is replaced with the call transcript at runtime.
        """)

        new_system = st.text_area(
            "System Prompt",
            value=config.get("system_prompt", ""),
            height=100,
            help="Sets the role/persona for the AI evaluator."
        )
        new_main = st.text_area(
            "Main Prompt (must include {transcript})",
            value=config.get("main_prompt", ""),
            height=350,
            help="The full prompt sent to GPT. Use {transcript} as placeholder."
        )

        if st.button("💾 Save Prompt", type="primary"):
            if "{transcript}" not in new_main:
                st.error("❌ main_prompt must contain `{transcript}`")
            else:
                resp = requests.put(
                    f"{API_BASE}/config/prompt",
                    json={"system_prompt": new_system, "main_prompt": new_main},
                    timeout=5,
                )
                if resp.status_code == 200:
                    st.success("✅ Prompt saved successfully!")
                else:
                    st.error(f"❌ {resp.json().get('detail', resp.text)}")

    # ── Field Descriptions Tab ─────────────────────────────────────────────────
    with tab_fields:
        st.markdown("""
        Edit the **description** for each field. These descriptions guide how the AI fills in each value.
        Changes are saved to `prompt_config.json` and used on the next evaluation.
        """)

        field_descs = config.get("field_descriptions", {})
        updated_descs = {}

        # Group fields visually
        groups = {
            "📁 Metadata": ["audio_filename", "transcript"],
            "👤 Human Interaction": [
                "human_picked_up", "human_rpc_confirmed", "number_of_times_amelia_asked_for_rpc",
                "human_related_party_or_unavailable", "human_hung_up_before_rpc",
                "human_blood_draw_info_given", "human_hung_up_before_blood_draw_question",
                "user_requested_additional_assistance", "user_additional_assistance_question",
                "amelia_provided_additional_assistance", "amelia_additional_assistance_answer",
                "escalation_requested", "callback_requested",
                "amelia_acknowledged_callback_escalate_request",
            ],
            "📞 Call End": [
                "user_hangup", "user_hangup_reason", "call_ended", "call_ended_reason",
            ],
            "📨 Voicemail / IVR": [
                "voicemail_connected", "ivr_connected", "voicemail_successful",
                "voicemail_failure_reason", "prescreening_connected", "prescreening_successful",
            ],
            "🔇 Audio Quality": ["user_requested_spanish", "silence_detected", "no_audio_available"],
            "🔍 Amelia Quality": [
                "amelia_not_replying_to_hello", "amelia_stayed_on_call_during_silence",
                "amelia_pronunciation_correct", "amelia_pronunciation_notes",
                "user_amelia_vm_amelia_overlap", "additional_comments",
            ],
            "📊 Classification": ["call_type", "call_outcome", "patient_name", "blood_draw_completed"],
        }

        for group_name, fields in groups.items():
            st.subheader(group_name)
            cols = st.columns(2)
            for i, field in enumerate(fields):
                col = cols[i % 2]
                updated_descs[field] = col.text_input(
                    field,
                    value=field_descs.get(field, ""),
                    key=f"desc_{field}",
                )

        if st.button("💾 Save Field Descriptions", type="primary"):
            resp = requests.put(
                f"{API_BASE}/config/prompt",
                json={"field_descriptions": updated_descs},
                timeout=5,
            )
            if resp.status_code == 200:
                st.success("✅ Field descriptions saved!")
            else:
                st.error(f"❌ {resp.json().get('detail', resp.text)}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Dashboard
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.title("📊 Evaluation Dashboard")

    if not api_ok():
        st.error("⚠️ Backend API is not reachable. Please start the FastAPI server.")
        st.stop()

    try:
        resp = requests.get(f"{API_BASE}/results/csv", timeout=5)
        rows = resp.json().get("rows", [])
    except Exception as e:
        st.error(f"Failed to load results: {e}")
        st.stop()

    if not rows:
        st.info("No evaluation results yet. Upload and evaluate some audio files first.")
        st.stop()

    df = pd.DataFrame(rows)

    # ── KPI Row ────────────────────────────────────────────────────────────────
    total = len(df)
    success = df["call_outcome"].str.startswith("Success").sum() if "call_outcome" in df.columns else 0
    human_calls = (df["call_type"] == "Human").sum() if "call_type" in df.columns else 0
    vm_calls = (df["call_type"] == "Voicemail").sum() if "call_type" in df.columns else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Calls", total)
    k2.metric("Success Rate", f"{int(success/total*100)}%" if total else "—")
    k3.metric("Human Calls", human_calls)
    k4.metric("Voicemail", vm_calls)
    k5.metric("Prescreening", (df["call_type"] == "Prescreening").sum() if "call_type" in df.columns else 0)

    st.divider()

    # ── Charts Row 1 ───────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        if "call_type" in df.columns:
            ct_counts = df["call_type"].value_counts().reset_index()
            ct_counts.columns = ["Call Type", "Count"]
            fig = px.pie(ct_counts, values="Count", names="Call Type",
                         title="Call Type Distribution", hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "call_outcome" in df.columns:
            df["outcome_label"] = df["call_outcome"].apply(
                lambda x: "Success" if str(x).startswith("Success") else "Failure"
            )
            oc_counts = df["outcome_label"].value_counts().reset_index()
            oc_counts.columns = ["Outcome", "Count"]
            fig2 = px.bar(oc_counts, x="Outcome", y="Count", title="Call Outcomes",
                          color="Outcome", color_discrete_map={"Success": "#2ecc71", "Failure": "#e74c3c"})
            st.plotly_chart(fig2, use_container_width=True)

    # ── Charts Row 2 ───────────────────────────────────────────────────────────
    c3, c4 = st.columns(2)

    yes_no_fields = [
        "human_picked_up", "human_rpc_confirmed", "blood_draw_completed",
        "escalation_requested", "callback_requested", "voicemail_connected",
        "silence_detected", "amelia_pronunciation_correct",
    ]
    available = [f for f in yes_no_fields if f in df.columns]

    with c3:
        if available:
            yes_pct = {f: (df[f].str.upper() == "YES").mean() * 100 for f in available}
            bar_df = pd.DataFrame({"Field": list(yes_pct.keys()), "Yes %": list(yes_pct.values())})
            bar_df["Field"] = bar_df["Field"].str.replace("_", " ").str.title()
            fig3 = px.bar(bar_df, x="Yes %", y="Field", orientation="h",
                          title="Key Field — % Yes", color="Yes %",
                          color_continuous_scale="RdYlGn", range_color=[0, 100])
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)

    with c4:
        if "number_of_times_amelia_asked_for_rpc" in df.columns:
            rpc_col = pd.to_numeric(df["number_of_times_amelia_asked_for_rpc"], errors="coerce").dropna()
            if not rpc_col.empty:
                fig4 = px.histogram(rpc_col, nbins=10, title="RPC Attempts Distribution",
                                    labels={"value": "# Times Amelia Asked for RPC"},
                                    color_discrete_sequence=["#3498db"])
                st.plotly_chart(fig4, use_container_width=True)

    # ── Voicemail Failure Breakdown ────────────────────────────────────────────
    if "voicemail_failure_reason" in df.columns:
        vm_fail = df[df["voicemail_failure_reason"].str.strip() != ""]["voicemail_failure_reason"].value_counts()
        if not vm_fail.empty:
            st.subheader("📨 Voicemail Failure Reasons")
            fig5 = px.pie(values=vm_fail.values, names=vm_fail.index,
                          title="Voicemail Failure Breakdown")
            st.plotly_chart(fig5, use_container_width=True)

    # ── Full Data Table ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📋 All Evaluations")

    hide_transcript = st.checkbox("Hide transcript column", value=True)
    display_df = df.drop(columns=["transcript"], errors="ignore") if hide_transcript else df

    st.dataframe(display_df, use_container_width=True, height=400)

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv_bytes, "evaluations_export.csv", "text/csv")
