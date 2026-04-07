import os
import time
import requests
import streamlit as st
import json
from io import BytesIO
from groq import Groq
from dotenv import load_dotenv
from streamlit_lottie import st_lottie
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

load_dotenv()

# ─────────────────────────────────────────────────────────────────── #
#  PAGE CONFIG                                                         #
# ─────────────────────────────────────────────────────────────────── #

st.set_page_config(
    page_title="AI Legal Notice Generator",
    page_icon="⚖️",
    layout="centered",
)

# ─────────────────────────────────────────────────────────────────── #
#  DARK GLASSMORPHISM CSS                                              #
# ─────────────────────────────────────────────────────────────────── #

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

/* ── Reset & background ──────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1b3e 45%, #0a0a1a 100%) !important;
    min-height: 100vh;
}
[data-testid="stHeader"],
[data-testid="stToolbar"] { background: transparent !important; }
#MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden; }

/* ── Base text ───────────────────────────────────────────────────── */
body, p, div, span, label {
    color: #c9d6e8 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Glassmorphism card mixin ────────────────────────────────────── */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 20px;
    padding: 32px;
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 24px;
}

/* ── Hero title ─────────────────────────────────────────────────── */
.hero-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 10px 0;
    line-height: 1.15;
    letter-spacing: -0.5px;
}
.hero-sub {
    color: #7d8fa8 !important;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 0;
    letter-spacing: 0.2px;
}

/* ── Typewriter cursor ───────────────────────────────────────────── */
.tw-cursor {
    display: inline-block;
    width: 2px;
    height: 2.4rem;
    background: linear-gradient(180deg, #a78bfa, #60a5fa);
    border-radius: 2px;
    margin-left: 3px;
    vertical-align: middle;
    animation: blink 0.75s step-end infinite;
}
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }

/* ── Section label ───────────────────────────────────────────────── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #6b7faa !important;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(107,127,170,0.4), transparent);
}

/* ── Inputs ──────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #1e2a45 !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 12px !important;
    color: #f0f4ff !important;
    -webkit-text-fill-color: #f0f4ff !important;
    caret-color: #a78bfa !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.94rem !important;
    padding: 11px 15px !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
    outline: none !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(148,163,184,0.6) !important;
    box-shadow: 0 0 0 2px rgba(148,163,184,0.15) !important;
    background: #1a2540 !important;
    color: #f0f4ff !important;
    -webkit-text-fill-color: #f0f4ff !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #4a5a7a !important;
    -webkit-text-fill-color: #4a5a7a !important;
    opacity: 1 !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: #94a3b8 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}
/* kill Streamlit's native red focus ring on the wrapper div */
[data-testid="stTextInput"] > div:focus-within,
[data-testid="stTextArea"] > div:focus-within {
    border-color: rgba(148,163,184,0.4) !important;
    box-shadow: none !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within {
    border-color: rgba(148,163,184,0.4) !important;
    box-shadow: none !important;
}

/* ── Primary submit button ───────────────────────────────────────── */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #7c3aed 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 13px 28px !important;
    font-size: 0.97rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.45) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    width: 100% !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.60) !important;
}
[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0) scale(0.99) !important;
}

/* ── Regular buttons ─────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: rgba(124,58,237,0.15) !important;
    border: 1px solid rgba(124,58,237,0.35) !important;
    color: #a78bfa !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    transition: all 0.18s ease !important;
}
[data-testid="stButton"] > button:hover {
    background: rgba(124,58,237,0.30) !important;
    border-color: rgba(124,58,237,0.65) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(124,58,237,0.30) !important;
}

/* ── Download buttons ────────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #94a3b8 !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    transition: all 0.18s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(96,165,250,0.12) !important;
    border-color: rgba(96,165,250,0.45) !important;
    color: #60a5fa !important;
    transform: translateY(-1px) !important;
}

/* ── Metric cards ────────────────────────────────────────────────── */
.metric-glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 18px 22px;
    text-align: center;
}
.metric-label {
    font-size: 0.70rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #4a5e80 !important;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 1rem;
    font-weight: 700;
    color: #c9d6e8 !important;
}

/* ── Legal notice document box (paper style) ─────────────────────── */
.legal-document {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-family: Georgia, 'Times New Roman', Times, serif !important;
    font-size: 0.97rem;
    line-height: 1.85;
    padding: 36px 40px;
    border-left: 4px solid #1e3a8a;
    border-radius: 0 12px 12px 0;
    box-shadow: 0 8px 40px rgba(0,0,0,0.50);
    margin-bottom: 8px;
}
.legal-document * { color: #000000 !important; }
.legal-document .ld-header {
    text-align: center;
    font-size: 0.82rem;
    letter-spacing: 1.5px;
    color: #374151 !important;
    margin-bottom: 4px;
}
.legal-document .ld-subject {
    text-align: center;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 24px;
}
.legal-document .ld-salutation { margin-bottom: 20px; }
.legal-document .ld-para       { margin-bottom: 14px; }
.legal-document .ld-demands    { font-weight: 700; margin-bottom: 14px; }
.legal-document .ld-conclusion { margin-bottom: 0; }

/* ── Missing vars ────────────────────────────────────────────────── */
.missing-box {
    background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,191,36,0.25);
    border-left: 4px solid #f59e0b;
    border-radius: 12px;
    padding: 18px 22px;
    color: #fcd34d !important;
    font-size: 0.93rem;
}
.missing-box ul { margin: 10px 0 0 0; padding-left: 20px; }
.missing-box li { margin-bottom: 4px; color: #fbbf24 !important; }

/* ── Disclaimer ──────────────────────────────────────────────────── */
.disclaimer-dark {
    background: rgba(220, 38, 38, 0.08);
    border: 1px solid rgba(220, 38, 38, 0.30);
    border-left: 4px solid #dc2626;
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 0.80rem;
    color: #fca5a5 !important;
    line-height: 1.65;
}
.disclaimer-dark strong {
    color: #f87171 !important;
}

/* ── Loading message card ────────────────────────────────────────── */
.loading-card {
    background: rgba(124,58,237,0.10);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    color: #a78bfa !important;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.2px;
}

/* ── Success / warning overrides ────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ── Divider ─────────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Code block ──────────────────────────────────────────────────── */
[data-testid="stCode"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}

/* ── Text area (edit box) ────────────────────────────────────────── */
.stTextArea [data-baseweb="textarea"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────── #
#  SESSION STATE                                                       #
# ─────────────────────────────────────────────────────────────────── #

if "llm_response"    not in st.session_state: st.session_state.llm_response    = None
if "last_inputs"     not in st.session_state: st.session_state.last_inputs     = {}
if "typewriter_done" not in st.session_state: st.session_state.typewriter_done = False

# ─────────────────────────────────────────────────────────────────── #
#  BACKEND HELPERS  (unchanged)                                        #
# ─────────────────────────────────────────────────────────────────── #

@st.cache_data
def load_system_prompt() -> str:
    with open("legal_notice_system.md", "r", encoding="utf-8") as f:
        return f.read()


@st.cache_data(show_spinner=False)
def load_lottie(url: str) -> dict | None:
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def call_groq(prompt: str, model: str) -> str | None:
    try:
        api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Service temporarily unavailable. ({model}): {e}")
        return None


def validate_json(response_text: str) -> dict | None:
    if not response_text:
        return None
    try:
        parsed = json.loads(response_text)
        if all(k in parsed for k in ["analysis", "notice_draft", "disclaimer"]):
            return parsed
        return None
    except (json.JSONDecodeError, ValueError):
        return None


def run_ai(sender_name: str, recipient_name: str, recipient_address: str, issue_description: str) -> None:
    st.session_state.llm_response = None

    system_prompt = load_system_prompt()
    user_input = (
        f"Sender Name: {sender_name}\n"
        f"Recipient Name: {recipient_name}\n"
        f"Recipient Address: {recipient_address}\n"
        f"Issue Description: {issue_description}\n\n"
        "Return ONLY valid JSON. No explanation."
    )
    full_prompt = f"{system_prompt}\n\n---\n\nUser Input:\n{user_input}"

    PRIMARY_MODEL  = "llama-3.1-8b-instant"
    FALLBACK_MODEL = "llama-3.3-70b-versatile"

    loading_steps = [
        ("🔍", "Analyzing your case..."),
        ("📂", "Classifying legal category..."),
        ("✍️", "Drafting legal notice..."),
        ("🔎", "Reviewing for completeness..."),
    ]
    slot = st.empty()
    for icon, msg in loading_steps:
        slot.markdown(
            f'<div class="loading-card">{icon}&nbsp; {msg}</div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.55)

    raw    = call_groq(full_prompt, PRIMARY_MODEL)
    result = validate_json(raw)

    if result is None:
        slot.markdown(
            '<div class="loading-card">🔄&nbsp; Switching to advanced model...</div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.4)
        raw    = call_groq(full_prompt, FALLBACK_MODEL)
        result = validate_json(raw)

    slot.empty()

    if result is not None:
        st.session_state.llm_response = result
    else:
        st.error("AI response failed. Please try again.")


def build_notice_text(notice: dict, disclaimer: str) -> str:
    return (
        f"{notice.get('subject', '')}\n"
        f"{notice.get('header', '')}\n\n"
        f"{notice.get('salutation', '')}\n\n"
        + "\n\n".join(notice.get("body_paragraphs", []))
        + f"\n\n{notice.get('demands', '')}\n\n"
        f"{notice.get('conclusion', '')}\n\n"
        f"---\nDISCLAIMER: {disclaimer}"
    )


def generate_pdf(notice_text: str, disclaimer: str) -> bytes | None:
    if not notice_text.strip():
        return None
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=2.5*cm, rightMargin=2.5*cm,
            topMargin=2.5*cm,  bottomMargin=2.5*cm,
        )
        s_subj = ParagraphStyle("subj", fontName="Times-Bold",   fontSize=12, alignment=TA_CENTER, spaceAfter=6)
        s_hdr  = ParagraphStyle("hdr",  fontName="Times-Roman",  fontSize=10, alignment=TA_CENTER, spaceAfter=4)
        s_body = ParagraphStyle("body", fontName="Times-Roman",  fontSize=11, alignment=TA_JUSTIFY, leading=16, spaceAfter=8)
        s_disc = ParagraphStyle("disc", fontName="Times-Italic", fontSize=9,  alignment=TA_JUSTIFY, leading=13)

        story = []
        lines = notice_text.splitlines()
        if lines:
            story.append(Paragraph(lines[0], s_subj)); story.append(Spacer(1, 0.2*cm))
        if len(lines) > 1:
            story.append(Paragraph(lines[1], s_hdr));  story.append(Spacer(1, 0.4*cm))
        for line in lines[2:]:
            if line.startswith("---"):
                story.append(Spacer(1, 0.6*cm))
            elif line.strip():
                story.append(Paragraph(line.replace("\n", "<br/>"), s_body))
            else:
                story.append(Spacer(1, 0.25*cm))
        story.append(Spacer(1, 0.8*cm))
        story.append(Paragraph(f"<i>Disclaimer: {disclaimer}</i>", s_disc))
        doc.build(story)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"PDF generation failed: {e}")
        return None

# ─────────────────────────────────────────────────────────────────── #
#  LOTTIE ASSET                                                        #
# ─────────────────────────────────────────────────────────────────── #

LOTTIE_URL = "https://assets2.lottiefiles.com/packages/lf20_t9gkkhz4.json"
lottie_anim = load_lottie(LOTTIE_URL)

# ─────────────────────────────────────────────────────────────────── #
#  HERO HEADER                                                         #
# ─────────────────────────────────────────────────────────────────── #

TITLE_TEXT = "AI Legal Notice Generator"
TITLE_SVG  = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" '
    'width="36" height="36" style="vertical-align:middle;margin-right:10px;'
    'filter:drop-shadow(0 0 6px rgba(167,139,250,0.5));">'
    '<path d="M12.9985 2L12.9979 3.278L17.9985 4.94591L21.631 3.73509L22.2634 5.63246L19.2319 6.643'
    'L22.3272 15.1549C21.2353 16.2921 19.6996 17 17.9985 17C16.2975 17 14.7618 16.2921 13.6699 15.1549'
    'L16.7639 6.643L12.9979 5.387V19H16.9985V21H6.99854V19H10.9979V5.387L7.23192 6.643'
    'L10.3272 15.1549C9.23528 16.2921 7.69957 17 5.99854 17C4.2975 17 2.76179 16.2921 1.66992 15.1549'
    'L4.76392 6.643L1.73363 5.63246L2.36608 3.73509L5.99854 4.94591L10.9979 3.278L10.9985 2H12.9985Z'
    'M17.9985 9.10267L16.5809 13H19.4159L17.9985 9.10267ZM5.99854 9.10267L4.58092 13H7.41592L5.99854 9.10267Z"/>'
    '</svg>'
)

# Lottie + title side by side
col_hero_txt, col_hero_anim = st.columns([3, 1.2], gap="small")

with col_hero_txt:
    title_slot = st.empty()
    if not st.session_state.typewriter_done:
        displayed = ""
        for char in TITLE_TEXT:
            displayed += char
            title_slot.markdown(
                f'<h1 class="hero-title" style="display:flex;align-items:center;">'
                f'{TITLE_SVG}{displayed}<span class="tw-cursor"></span></h1>',
                unsafe_allow_html=True,
            )
            time.sleep(0.05)
        st.session_state.typewriter_done = True

    title_slot.markdown(
        f'<h1 class="hero-title" style="display:flex;align-items:center;">{TITLE_SVG}{TITLE_TEXT}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-sub">Generate structured Indian legal notices — powered by AI.</p>',
        unsafe_allow_html=True,
    )

with col_hero_anim:
    if lottie_anim:
        st_lottie(lottie_anim, speed=0.6, loop=True, height=120, key="hero_lottie")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────── #
#  INPUT FORM                                                          #
# ─────────────────────────────────────────────────────────────────── #

st.markdown(
    '<div class="section-label">📝 &nbsp;Case Details</div>',
    unsafe_allow_html=True,
)

with st.form("notice_form"):
    sender_name       = st.text_input("Sender Name *",      placeholder="e.g. Rahul Sharma")
    recipient_name    = st.text_input("Recipient Name *",   placeholder="e.g. ABC Pvt. Ltd.")
    recipient_address = st.text_input("Recipient Address",  placeholder="e.g. 123, MG Road, Mumbai – 400001")
    issue_description = st.text_area(
        "Describe your issue * (include dates, amounts, what happened)",
        placeholder="e.g. My employer has not paid my salary of ₹45,000 for January, February, and March 2025...",
        height=160,
    )
    submitted = st.form_submit_button("⚖️  Generate Legal Notice", use_container_width=True)

if submitted:
    if not sender_name.strip() or not recipient_name.strip() or not issue_description.strip():
        st.error("⚠️  Please fill all required fields (marked with *).")
    else:
        st.session_state.last_inputs = {
            "sender_name": sender_name,
            "recipient_name": recipient_name,
            "recipient_address": recipient_address,
            "issue_description": issue_description,
        }
        run_ai(sender_name, recipient_name, recipient_address, issue_description)

# ─────────────────────────────────────────────────────────────────── #
#  RESULTS                                                             #
# ─────────────────────────────────────────────────────────────────── #

if st.session_state.llm_response is not None:
    response   = st.session_state.llm_response
    analysis   = response.get("analysis", {})
    notice     = response.get("notice_draft", {})
    disclaimer = response.get("disclaimer", "")
    status     = analysis.get("completeness_status", "N/A")
    category   = analysis.get("category", "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Analysis cards ─────────────────────────────────────────────
    st.markdown(
        '<div class="section-label">📊 &nbsp;Analysis</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2, gap="small")
    with col_a:
        st.markdown(
            f'<div class="metric-glass">'
            f'<div class="metric-label">Category</div>'
            f'<div class="metric-value">{category.replace("_", " ")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        if status == "Complete":
            color, icon = "#facc15", "✅"
        elif status == "Incomplete":
            color, icon = "#facc15", "⚠️"
        else:
            color, icon = "#facc15", "ℹ️"
        st.markdown(
            f'<div class="metric-glass">'
            f'<div class="metric-label">Status</div>'
            f'<div class="metric-value" style="color:{color};">{icon} {status}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if status == "Complete":
        st.success("✅  All required information is present. Legal notice generated below.")

    elif status == "Incomplete":
        missing = analysis.get("missing_variables", [])
        items_html = "".join(f"<li>{item}</li>" for item in missing)
        st.markdown(
            f'<div class="missing-box">'
            f'<strong>⚠️ Missing Information</strong> — please provide these details and try again.'
            f'<ul>{items_html}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Notice preview ─────────────────────────────────────────────
    if status == "Complete" and notice:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-label">📄 &nbsp;Legal Notice Preview</div>',
            unsafe_allow_html=True,
        )

        salutation_html      = notice.get("salutation", "").replace("\n", "<br>")
        body_paragraphs_html = "".join(
            f'<p class="ld-para">{p}</p>'
            for p in notice.get("body_paragraphs", [])
        )
        doc_html = (
            '<div class="legal-document">'
            f'<p class="ld-header">{notice.get("header", "")}</p>'
            f'<p class="ld-subject">{notice.get("subject", "")}</p>'
            f'<p class="ld-salutation">{salutation_html}</p>'
            f'{body_paragraphs_html}'
            f'<p class="ld-demands">{notice.get("demands", "")}</p>'
            f'<p class="ld-conclusion">{notice.get("conclusion", "")}</p>'
            '</div>'
        )
        st.markdown(doc_html, unsafe_allow_html=True)

        # ── Edit before download ───────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-label">✏️ &nbsp;Edit Before Download</div>',
            unsafe_allow_html=True,
        )
        base_text     = build_notice_text(notice, disclaimer)
        edited_notice = st.text_area(
            "Edit your legal notice",
            value=base_text,
            height=380,
            label_visibility="collapsed",
        )

        # ── Copy ──────────────────────────────────────────────────
        st.markdown(
            '<div class="section-label" style="margin-top:20px;">📋 &nbsp;Copy Notice</div>',
            unsafe_allow_html=True,
        )
        st.code(edited_notice, language=None)
        st.button("📋  Copy Notice", help="Select all text above (Ctrl+A) then Ctrl+C")

        # ── Downloads ─────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-label">⬇️ &nbsp;Download</div>',
            unsafe_allow_html=True,
        )
        col_txt, col_pdf = st.columns(2, gap="small")
        with col_txt:
            st.download_button(
                "📄  Download .txt",
                data=edited_notice,
                file_name="legal_notice.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col_pdf:
            pdf_bytes = generate_pdf(edited_notice, disclaimer)
            if pdf_bytes:
                st.download_button(
                    "📑  Download PDF",
                    data=pdf_bytes,
                    file_name="legal_notice.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    # ── Regenerate ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄  Regenerate Notice", use_container_width=True):
        inp = st.session_state.last_inputs
        if inp:
            run_ai(
                inp.get("sender_name", ""),
                inp.get("recipient_name", ""),
                inp.get("recipient_address", ""),
                inp.get("issue_description", ""),
            )
            st.rerun()

    # ── Disclaimer ─────────────────────────────────────────────────
    if disclaimer:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="disclaimer-dark">⚠️ <strong style="color:#6b7280;">Disclaimer:</strong> {disclaimer}</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br><br>", unsafe_allow_html=True)
