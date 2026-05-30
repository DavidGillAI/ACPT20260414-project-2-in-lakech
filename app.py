from __future__ import annotations

from datetime import datetime
import html
from pathlib import Path
import re

import streamlit as st

from src.content_type_workflows import (
    CreativeDesignIdeasWorkflow,
    InstagramContentWorkflow,
    LaunchCopyWorkflow,
    ProductDescriptionsWorkflow,
)
from src.ingestion import ensure_knowledge_base_structure
from src.prompt_engineering import PromptInputBundle


APP_TITLE = "In Lak'ech MVP"
KB_ROOT = Path("knowledge_base")
LOGO_PATH = Path("InLakech_logo_cropped.png")

WORKFLOW_OPTIONS = {
    "Social media caption": InstagramContentWorkflow,
    "Launch copy": LaunchCopyWorkflow,
    "Product description": ProductDescriptionsWorkflow,
    "Creative/design ideas": CreativeDesignIdeasWorkflow,
}

GUIDED_INPUT_OPTIONS = {
    "tone": ["Reflective", "Cinematic", "Editorial", "Conversational", "Minimal", "Warm", "Bold", "Professional"],
    "platform": ["Instagram", "Personal Blog", "LinkedIn", "Email Newsletter", "Product Page", "YouTube Description"],
    "cta": [
        "Ask a reflective question",
        "Invite comments",
        "Encourage sharing",
        "Direct users to a website",
        "Invite sign-ups",
        "No CTA",
    ],
    "campaign_objective": [
        "Build awareness",
        "Launch a product",
        "Explain a concept",
        "Drive engagement",
        "Build community",
        "Tell a founder story",
        "Generate design ideas",
    ],
    "target_audience": [
        "Independent creatives",
        "ADHD creatives",
        "Filmmakers",
        "Writers",
        "Ethical brands",
        "Small business owners",
        "Existing followers",
    ],
    "word_count": ["50", "100", "150", "250", "500"],
}


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #efe7dc;
            --muted: rgba(239, 231, 220, 0.72);
            --accent: #d7b15d;
            --panel: rgba(25, 16, 54, 0.72);
            --panel-border: rgba(215, 177, 93, 0.22);
            --shadow: 0 24px 80px rgba(5, 6, 18, 0.45);
        }

        .stApp {
            background:
                radial-gradient(circle at 20% 14%, rgba(145, 82, 255, 0.24), transparent 28%),
                radial-gradient(circle at 84% 78%, rgba(215, 177, 93, 0.10), transparent 24%),
                linear-gradient(145deg, #1b103f 0%, #281253 44%, #33166a 100%);
            color: var(--ink);
        }

        .stApp, .stApp p, .stApp span, .stApp label, .stApp div, .stApp li {
            color: var(--ink);
        }

        .stApp small, .stApp .stCaptionContainer, .stApp [data-testid="stCaption"] {
            color: var(--muted) !important;
        }

        .stApp .block-container {
            padding-top: 3rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        .inak-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 1rem;
            margin-bottom: 2rem;
            padding-bottom: 0.85rem;
            border-bottom: 1px solid rgba(215, 177, 93, 0.18);
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            letter-spacing: 0.02em;
        }

        .inak-header .brand {
            font-size: 1.05rem;
            font-weight: 700;
        }

        .inak-header .meta {
            font-family: "Courier New", Courier, monospace;
            font-size: 0.72rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.16em;
        }

        .inak-eyebrow {
            font-family: "Courier New", Courier, monospace;
            font-size: 0.72rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 1rem;
        }

        .inak-title {
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2.6rem, 5vw, 4.5rem);
            line-height: 0.98;
            letter-spacing: -0.03em;
            color: var(--ink);
            margin: 0 0 1.5rem 0;
            max-width: 10.5ch;
        }

        .inak-subtitle {
            font-family: Arial, Helvetica, sans-serif;
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.7;
            max-width: 58rem;
            margin-bottom: 1.5rem;
        }

        .inak-quote {
            border-left: 3px solid var(--accent);
            padding-left: 1.15rem;
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-style: italic;
            font-size: 1.08rem;
            line-height: 1.55;
            max-width: 16rem;
        }

        .inak-hero-description {
            font-family: Arial, Helvetica, sans-serif;
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.7;
            margin: 0 0 1.5rem 0;
        }

        section[data-testid="stSidebar"] {
            background: rgba(16, 10, 35, 0.42);
        }

        .panel {
            background: var(--panel);
            border: 1px solid var(--panel-border);
            border-radius: 18px;
            padding: 1.2rem 1.15rem 1rem;
            box-shadow: var(--shadow);
            backdrop-filter: blur(18px);
        }

        .panel h2, .panel h3, .panel h4 {
            font-family: Georgia, "Times New Roman", serif;
            color: var(--ink);
            letter-spacing: 0.01em;
        }

        .panel label, .panel p, .panel div, .panel span {
            color: var(--ink);
        }

        .panel small, .panel .stCaptionContainer, .panel [data-testid="stCaption"] {
            color: var(--muted) !important;
        }

        .stMarkdown, .stMarkdown p, .stMarkdown div {
            color: var(--ink) !important;
        }

        .stMarkdown code {
            color: #f4eddc !important;
            background: rgba(11, 9, 27, 0.45) !important;
            border-radius: 6px;
            padding: 0.1rem 0.25rem;
        }

        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div,
        .stRadio, .stFileUploader {
            background: rgba(11, 9, 27, 0.42) !important;
            color: var(--ink) !important;
            border-color: rgba(215, 177, 93, 0.18) !important;
        }

        .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label,
        .stFileUploader label, .stSlider label {
            color: var(--ink) !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em;
        }

        .stTextInput p, .stTextArea p, .stSelectbox p, .stRadio p, .stFileUploader p,
        .stTextInput small, .stTextArea small, .stSelectbox small, .stRadio small, .stFileUploader small {
            color: var(--muted) !important;
        }

        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] input,
        .stRadio label div,
        .stFileUploader span,
        .stFileUploader button,
        .stFileUploader p {
            color: var(--ink) !important;
        }

        .stTextInput input, .stTextArea textarea {
            border-radius: 12px !important;
        }

        .stTextInput input::placeholder, .stTextArea textarea::placeholder {
            color: rgba(239, 231, 220, 0.42) !important;
        }

        .stButton > button,
        .stDownloadButton > button {
            background: linear-gradient(135deg, rgba(215, 177, 93, 0.95), rgba(175, 137, 42, 0.92)) !important;
            color: #1a102e !important;
            border: 0 !important;
            border-radius: 999px !important;
            font-family: Arial, Helvetica, sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em !important;
            padding: 0.6rem 1.1rem !important;
            box-shadow: 0 14px 28px rgba(0, 0, 0, 0.24);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            filter: brightness(1.03);
            transform: translateY(-1px);
        }

        .stButton > button span, .stButton > button p,
        .stDownloadButton > button span, .stDownloadButton > button p {
            color: #1a102e !important;
        }

        .stFileUploader button {
            background: rgba(239, 231, 220, 0.92) !important;
            color: #1a102e !important;
            border: 1px solid rgba(215, 177, 93, 0.35) !important;
            border-radius: 999px !important;
            font-weight: 700 !important;
        }

        .stFileUploader button span,
        .stFileUploader button p {
            color: #1a102e !important;
        }

        div[data-testid="stAlertSuccess"] {
            background: rgba(24, 74, 53, 0.40) !important;
            border: 1px solid rgba(169, 221, 192, 0.26) !important;
            color: var(--ink) !important;
        }

        div[data-testid="stAlertSuccess"] p,
        div[data-testid="stAlertSuccess"] span,
        div[data-testid="stAlertSuccess"] div {
            color: var(--ink) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(14, 11, 34, 0.20);
            border-color: rgba(215, 177, 93, 0.18);
        }

        hr {
            border-color: rgba(215, 177, 93, 0.18) !important;
        }

        .output-card {
            background: rgba(11, 9, 27, 0.52);
            border: 1px solid rgba(215, 177, 93, 0.20);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow);
        }

        .output-meta {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            font-family: "Courier New", Courier, monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 0.85rem;
        }

        .output-text {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 1rem;
            line-height: 1.75;
            color: var(--ink);
            white-space: pre-wrap;
        }

        .stRadio > label {
            color: var(--ink) !important;
        }

        .stFileUploader label, .stFileUploader > div {
            color: var(--ink) !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: rgba(11, 9, 27, 0.38) !important;
            border-color: rgba(215, 177, 93, 0.18) !important;
            color: var(--ink) !important;
        }

        .stFileChipName {
            color: #1a102e !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            -webkit-text-fill-color: #1a102e !important;
        }

        .stFileChipName + div {
            color: rgba(26, 16, 46, 0.7) !important;
            opacity: 1 !important;
            -webkit-text-fill-color: rgba(26, 16, 46, 0.7) !important;
        }

        [data-testid="stFileUploaderDropzone"] p,
        [data-testid="stFileUploaderDropzone"] span {
            color: var(--ink) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sanitize_filename(name: str, default_stem: str) -> str:
    stem = Path(name).stem or default_stem
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    return f"{stem or default_stem}.md"


def _write_markdown_document(target_folder: str, file_name: str, content: str) -> Path:
    paths = ensure_knowledge_base_structure(KB_ROOT)
    folder_path = paths[target_folder]
    safe_name = _sanitize_filename(file_name, "uploaded_document")
    target_path = folder_path / safe_name

    if target_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        target_path = folder_path / f"{Path(safe_name).stem}_{timestamp}.md"

    target_path.write_text(content, encoding="utf-8")
    return target_path


def _build_prompt_inputs() -> PromptInputBundle:
    return PromptInputBundle(
        tone=st.session_state.get("tone") or None,
        platform=st.session_state.get("platform") or None,
        cta=st.session_state.get("cta") or None,
        campaign_objective=st.session_state.get("campaign_objective") or None,
        target_audience=st.session_state.get("target_audience") or None,
        word_count=st.session_state.get("word_count") or None,
        example_content=st.session_state.get("example_content") or None,
        detailed_instructions=st.session_state.get("detailed_instructions") or None,
    )


def _render_guided_input(field_label: str, state_key: str) -> None:
    options = GUIDED_INPUT_OPTIONS[state_key]
    choice_key = f"{state_key}_choice"
    custom_key = f"{state_key}_custom"
    current_value = st.session_state.get(state_key) or ""

    if choice_key not in st.session_state:
        st.session_state[choice_key] = current_value if current_value in options else ("Custom..." if current_value else options[0])
    if st.session_state[choice_key] == "Custom..." and custom_key not in st.session_state and current_value and current_value not in options:
        st.session_state[custom_key] = current_value

    choice = st.selectbox(field_label, options + ["Custom..."], key=choice_key)
    if choice == "Custom...":
        custom_value = st.text_input(
            f"Custom {field_label}",
            key=custom_key,
            placeholder=f"Enter custom {field_label.lower()}...",
        )
        st.session_state[state_key] = custom_value.strip()
    else:
        st.session_state[state_key] = choice


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    _inject_styles()

    hero_left, _, _ = st.columns([1.05, 1.9, 1.2])
    with hero_left:
        st.image(str(LOGO_PATH), width=220)
        st.markdown(
            '<div style="width:220px;text-align:center;font-family:Georgia, \'Times New Roman\', serif;font-style:italic;color:var(--ink);margin:-0.35rem 0 1.2rem 0;">&ldquo;I am the other you&rdquo;</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="inak-hero-description">A minimal, human-guided demo for brand-aligned text generation using uploaded brand-specific content and examples.</div>',
        unsafe_allow_html=True,
    )

    ensure_knowledge_base_structure(KB_ROOT)

    left, center, right = st.columns([0.9, 1.3, 2.2])

    with left:
        with st.container(border=True):
            st.subheader("Knowledge Base Input")
            target_folder = st.radio(
                "Save uploaded Markdown to:",
                ["primary", "secondary"],
                horizontal=True,
            )

            uploaded_files = st.file_uploader(
                "Upload Markdown documents",
                type=["md", "markdown"],
                accept_multiple_files=True,
            )
            if uploaded_files and st.button("Save uploaded files"):
                saved_paths = []
                for uploaded in uploaded_files:
                    content = uploaded.getvalue().decode("utf-8-sig")
                    saved_paths.append(_write_markdown_document(target_folder, uploaded.name, content))
                st.success(f"Saved {len(saved_paths)} document(s) to {target_folder}.")
                for path in saved_paths:
                    st.caption(str(path))

            st.markdown(
                '<div style="font-size:0.82rem;color:rgba(239, 231, 220, 0.62);margin-bottom:0.35rem;">No .md file? Paste your content below.</div>',
                unsafe_allow_html=True,
            )
            pasted_content = st.text_area(
                "Paste Markdown content",
                height=220,
                placeholder="Paste content here...",
                label_visibility="collapsed",
            )
            if st.button("Save pasted Markdown") and pasted_content.strip():
                saved_path = _write_markdown_document(target_folder, "pasted_notes.md", pasted_content.strip())
                st.success(f"Saved Markdown to {saved_path}")

    with center:
        with st.container(border=True):
            st.subheader("Generation Inputs")
            output_type = st.selectbox("Output type", list(WORKFLOW_OPTIONS.keys()))

            _render_guided_input("Tone", "tone")
            _render_guided_input("Platform", "platform")
            _render_guided_input("CTA", "cta")
            _render_guided_input("Campaign objective", "campaign_objective")
            _render_guided_input("Target audience", "target_audience")
            _render_guided_input("Word count", "word_count")
            st.text_area("Example content", key="example_content", height=120)
            st.text_area("Detailed instructions", key="detailed_instructions", height=120)

            model = st.text_input("Model override (optional)", value="")

            if st.button("Generate content"):
                workflow_cls = WORKFLOW_OPTIONS[output_type]
                workflow = workflow_cls()
                user_inputs = _build_prompt_inputs()

                try:
                    result = workflow.run(
                        user_inputs,
                        knowledge_base_root=str(KB_ROOT),
                        model=model.strip() or None,
                    )
                    st.session_state["latest_generation_result"] = result
                    st.success("Generation complete")
                except Exception as exc:  # pragma: no cover - UI error handling
                    st.error(f"Generation failed: {exc}")

    with right:
        with st.container(border=True):
            st.subheader("Latest Output")
            latest_result = st.session_state.get("latest_generation_result")
            if latest_result is None:
                st.caption("Generated output will appear here after you run the workflow.")
            else:
                st.markdown(
                    f"""
                    <div class="output-card">
                        <div class="output-meta">
                            <span>Review status: {html.escape(str(latest_result.review_record.status))}</span>
                            <span>Model used: {html.escape(str(latest_result.generation_result.generation.model))}</span>
                        </div>
                        <div class="output-text">{html.escape(latest_result.generation_result.generation.text)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.download_button(
                    "Download output as .txt",
                    data=latest_result.generation_result.generation.text,
                    file_name="generated_output.txt",
                    mime="text/plain",
                )

if __name__ == "__main__":
    main()
