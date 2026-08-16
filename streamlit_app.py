# import streamlit as st
# import requests

# API_BASE = "http://127.0.0.1:8000"

# st.set_page_config(page_title="PolicyPilot", page_icon="📄", layout="centered")
# st.title("📄 PolicyPilot — Insurance Policy Assistant")

# # ----------------------------------------------------------------------
# # Sidebar: PDF upload
# # ----------------------------------------------------------------------
# with st.sidebar:
#     st.header("Upload Policy PDF")
#     uploaded_file = st.file_uploader("Choose a policy PDF", type=["pdf"])

#     if uploaded_file is not None:
#         if st.button("Upload & Process"):
#             with st.spinner("Uploading and re-building the knowledge base... this can take a minute"):
#                 try:
#                     files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
#                     resp = requests.post(f"{API_BASE}/api/upload", files=files, timeout=300)
#                     if resp.status_code == 200:
#                         st.success(f"✅ {uploaded_file.name} processed successfully!")
#                         st.session_state.messages = []  # reset chat for the new policy
#                     else:
#                         st.error(f"Upload failed: {resp.text}")
#                 except requests.exceptions.RequestException as e:
#                     st.error(f"Could not reach the backend: {e}")

#     st.divider()
#     if st.button("📋 Generate Auto-Summary"):
#         with st.spinner("Analyzing policy and generating summary..."):
#             try:
#                 resp = requests.get(f"{API_BASE}/api/summary", timeout=300)
#                 if resp.status_code == 200:
#                     st.session_state.summary = resp.json()
#                 else:
#                     st.error(f"Summary failed: {resp.text}")
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Could not reach the backend: {e}")

# # ----------------------------------------------------------------------
# # Summary view (shown if generated)
# # ----------------------------------------------------------------------
# if "summary" in st.session_state:
#     with st.expander(f"📋 Policy Summary (Type detected: {st.session_state.summary.get('policy_type_detected', 'Unknown')})", expanded=True):
#         for item in st.session_state.summary.get("summary", []):
#             st.markdown(f"**{item['label']}**")
#             st.markdown(item["answer"])
#             st.caption(f"Sources: {item.get('sources', [])}")
#             st.divider()

# # ----------------------------------------------------------------------
# # Chat interface
# # ----------------------------------------------------------------------
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# if question := st.chat_input("Ask a question about your policy..."):
#     st.session_state.messages.append({"role": "user", "content": question})
#     with st.chat_message("user"):
#         st.markdown(question)

#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             try:
#                 resp = requests.post(
#                     f"{API_BASE}/api/ask",
#                     json={"question": question},
#                     timeout=120,
#                 )
#                 if resp.status_code == 200:
#                     body = resp.json()
#                     data = body.get("data", body)
#                     answer = data[0] if isinstance(data, (list, tuple)) else str(data)
#                     sources = data[1] if isinstance(data, (list, tuple)) and len(data) > 1 else []
#                 else:
#                     answer = f"⚠️ Error: {resp.text}"
#                     sources = []
#             except requests.exceptions.RequestException as e:
#                 answer = f"⚠️ Could not reach the backend: {e}"
#                 sources = []

#             st.markdown(answer)
#             if sources:
#                 st.caption(f"📎 Sources: {sources}")

#     st.session_state.messages.append({"role": "assistant", "content": answer})

# import streamlit as st
# import requests

# # -----------------------------------------------------------------
# # Page Config & Layout
# # -----------------------------------------------------------------
# st.set_page_config(
#     page_title="PolicyPilot AI - Insurance Legal Assistant",
#     page_icon="🛡️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS for Professional Styling
# st.markdown("""
#     <style>
#     .main-header {
#         font-size: 2.2rem;
#         color: #1E3A8A;
#         font-weight: 700;
#         margin-bottom: 0px;
#     }
#     .sub-text {
#         color: #4B5563;
#         font-size: 1.1rem;
#         margin-bottom: 20px;
#     }
#     .chat-container {
#         padding: 10px;
#     }
#     .stAlert {
#         border-radius: 8px;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Backend API Configuration
# BACKEND_URL = "http://127.0.0.1:8000"

# # -----------------------------------------------------------------
# # Sidebar: File Uploader & Navigation
# # -----------------------------------------------------------------
# with st.sidebar:
#     st.image("https://img.icons8.com/color/96/contract.png", width=70)
#     st.markdown("### PolicyPilot Control Panel")
#     st.markdown("Upload your insurance policy PDF or switch between views.")
    
#     st.divider()

#     # 1. PDF Upload Section
#     st.subheader("📁 Upload Policy PDF")
#     uploaded_file = st.file_uploader("Choose a policy PDF", type=["pdf"])
    
#     if uploaded_file is not None:
#         if st.button("🚀 Process & Index PDF", use_container_width=True):
#             with st.spinner("Processing PDF and rebuilding vector database... (This may take a moment)"):
#                 try:
#                     files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
#                     response = requests.post(f"{BACKEND_URL}/api/upload", files=files)
                    
#                     if response.status_code == 200:
#                         st.success(f"✅ '{uploaded_file.name}' indexed successfully!")
#                         # Clear chat history on new policy upload
#                         st.session_state.messages = []
#                         st.session_state.summary_data = None
#                     else:
#                         err_detail = response.json().get("detail", "Unknown error")
#                         st.error(f"❌ Error: {err_detail}")
#                 except requests.exceptions.ConnectionError:
#                     st.error("❌ Backend server not running! Start FastAPI via uvicorn.")

#     st.divider()

#     # 2. Navigation Mode
#     st.subheader("🧭 Navigation")
#     app_mode = st.radio(
#         "Choose Mode:",
#         ["💬 Chat Assistant", "📊 Executive Summary"],
#         label_visibility="collapsed"
#     )
    
#     st.divider()
#     st.markdown("**System Status:** 🟢 Connected" if 'requests' else "🔴 Offline")

# # -----------------------------------------------------------------
# # Main Screen Header
# # -----------------------------------------------------------------
# st.markdown('<p class="main-header">🛡️ PolicyPilot AI</p>', unsafe_allow_html=True)
# st.markdown('<p class="sub-text">Your intelligent legal companion for precise insurance policy analysis and clause extraction.</p>', unsafe_allow_html=True)

# # =================================================================
# # MODE 1: CHAT ASSISTANT
# # =================================================================
# if app_mode == "💬 Chat Assistant":
#     # Initialize chat history
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     # Display prior chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
#             # Render sources if available
#             if "sources" in message and message["sources"]:
#                 with st.expander("📌 Reference Sources"):
#                     for src in message["sources"]:
#                         file_name, page_num = src[0], src[1]
#                         st.markdown(f"- **File:** `{file_name}` | **Page:** `{page_num}`")

#     # User Input Box
#     if prompt := st.chat_input("Ask a question about the policy (e.g., What is the waiting period for pre-existing diseases?)"):
#         # Append user message
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         # Call FastAPI Backend (/api/ask)
#         with st.chat_message("assistant"):
#             with st.spinner("Analyzing policy clauses..."):
#                 try:
#                     response = requests.post(
#                         f"{BACKEND_URL}/api/ask",
#                         json={"question": prompt},
#                         headers={"accept": "application/json", "Content-Type": "application/json"}
#                     )
                    
#                     if response.status_code == 200:
#                         res_data = response.json()
#                         data_payload = res_data.get("data", ["", []])
                        
#                         # Unpack [answer_text, sources_list]
#                         if isinstance(data_payload, list) and len(data_payload) >= 2:
#                             answer_text = data_payload[0]
#                             sources_list = data_payload[1]
#                         else:
#                             answer_text = str(data_payload)
#                             sources_list = []
                            
#                         st.markdown(answer_text)
                        
#                         # Display sources cleanly if present
#                         if sources_list:
#                             with st.expander("📌 Reference Sources"):
#                                 for src in sources_list:
#                                     file_name, page_num = src[0], src[1]
#                                     st.markdown(f"- **File:** `{file_name}` | **Page:** `{page_num}`")
                        
#                         # Save to session state
#                         st.session_state.messages.append({
#                             "role": "assistant",
#                             "content": answer_text,
#                             "sources": sources_list
#                         })
#                     else:
#                         err_msg = f"⚠️ Server error (Status code: {response.status_code})"
#                         st.error(err_msg)
#                         st.session_state.messages.append({"role": "assistant", "content": err_msg, "sources": []})
                        
#                 except requests.exceptions.ConnectionError:
#                     err_msg = "❌ Could not connect to FastAPI backend. Ensure uvicorn is running on port 8000."
#                     st.error(err_msg)
#                     st.session_state.messages.append({"role": "assistant", "content": err_msg, "sources": []})

# # =================================================================
# # MODE 2: EXECUTIVE SUMMARY
# # =================================================================
# elif app_mode == "📊 Executive Summary":
#     st.markdown("### 📋 Automated Policy Executive Summary")
#     st.markdown("Get a comprehensive breakdown of key policy parameters automatically extracted and analyzed across categories.")

#     if "summary_data" not in st.session_state:
#         st.session_state.summary_data = None
#         st.session_state.detected_type = None

#     col1, col2 = st.columns([2, 5])
#     with col1:
#         fetch_button = st.button("🔄 Generate / Refresh Summary", use_container_width=True)

#     if fetch_button or st.session_state.summary_data is not None:
#         if fetch_button:
#             with st.spinner("Classifying policy type and extracting summary insights... (This takes 10-20 seconds)"):
#                 try:
#                     res = requests.get(f"{BACKEND_URL}/api/summary")
#                     if res.status_code == 200:
#                         res_json = res.json()
#                         st.session_state.summary_data = res_json.get("summary", [])
#                         st.session_state.detected_type = res_json.get("policy_type_detected", "Unknown")
#                     else:
#                         st.error(f"Failed to load summary. Status code: {res.status_code}")
#                 except requests.exceptions.ConnectionError:
#                     st.error("❌ Could not connect to backend server.")

#         # Display Summary Results if available
#         if st.session_state.summary_data:
#             st.info(f"🏷️ **Detected Policy Category:** `{st.session_state.detected_type}`")
#             st.divider()

#             for idx, item in enumerate(st.session_state.summary_data):
#                 with st.container():
#                     st.markdown(f"#### 🔹 {item['label']}")
#                     st.markdown(f"*Question:* `{item['question']}`")
#                     st.markdown(item['answer'])
                    
#                     if item['sources']:
#                         source_str = " | ".join([f"`{s[0]} (p. {s[1]})`" for s in item['sources']])
#                         st.markdown(f"*Sources:* {source_str}")
                    
#                     st.markdown("---")

"""
PolicyPilot Streamlit Frontend
================================
Run the backend first:  uvicorn api:app --reload
Then run this:           streamlit run streamlit_app.py

Dependencies beyond the backend's:
    pip install streamlit requests pymupdf fpdf2 groq --break-system-packages

Notes:
- PyMuPDF (import name: fitz) is used to render PDF pages as images for the
  side-by-side viewer and the clickable-citation feature. If it's not
  installed, those two features degrade gracefully (a message is shown
  instead of crashing the whole app).
- fpdf2 is used for "export chat as PDF". Same graceful-degradation approach.
- Voice input uses Groq's hosted Whisper model for transcription — reuses
  the same GROQ_API_KEY the backend already uses.
- This assumes the backend's docs/ folder (where uploaded PDFs are saved)
  is at ./docs relative to wherever you run `streamlit run` from. If your
  backend runs from a different working directory, update DOCS_DIR below.
"""

import os
import re
import io

import streamlit as st
import requests

# ----------------------------------------------------------------------
# Optional dependencies — degrade gracefully if missing instead of crashing
# ----------------------------------------------------------------------
try:
    import pymupdf as fitz  # PyMuPDF — 'fitz' import name is deprecated
    HAS_PDF_VIEWER = True
except ImportError:
    HAS_PDF_VIEWER = False

try:
    from fpdf import FPDF
    HAS_PDF_EXPORT = True
except ImportError:
    HAS_PDF_EXPORT = False

try:
    from groq import Groq as GroqClient
    HAS_VOICE = bool(os.environ.get("GROQ_API_KEY"))
except ImportError:
    HAS_VOICE = False

API_BASE = "http://127.0.0.1:8000"
DOCS_DIR = "docs"  # must match the backend's DOCS_DIR

st.set_page_config(page_title="PolicyPilot", page_icon="📄", layout="wide")

# ----------------------------------------------------------------------
# Session state defaults
# ----------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_pdf_name" not in st.session_state:
    st.session_state.current_pdf_name = None
if "viewer_page" not in st.session_state:
    st.session_state.viewer_page = 1
if "compare_a" not in st.session_state:
    st.session_state.compare_a = []  # list of {question, answer, label}
if "compare_b" not in st.session_state:
    st.session_state.compare_b = []


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def render_pdf_page(pdf_path: str, page_num: int, zoom: float = 1.8):
    """Renders a single PDF page as PNG bytes. Returns (bytes, page_count)
    or (None, 0) on any failure."""
    if not HAS_PDF_VIEWER or not os.path.exists(pdf_path):
        return None, 0
    try:
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > doc.page_count:
            page_num = 1
        page = doc.load_page(page_num - 1)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        page_count = doc.page_count
        doc.close()
        return img_bytes, page_count
    except Exception:
        return None, 0


def extract_cited_pages(answer_text: str) -> list:
    """Pulls out all [Page: N] citations from an answer, deduped, in order."""
    matches = re.findall(r"\[Page:\s*(\d+)\]", answer_text)
    seen = []
    for m in matches:
        n = int(m)
        if n not in seen:
            seen.append(n)
    return seen


def looks_unconfirmed(answer_text: str) -> bool:
    """Detects the 'not explicitly mentioned / general industry standard'
    fallback pattern (Rule 3), to show a confidence badge."""
    lowered = answer_text.lower()
    return (
        "not explicitly mentioned" in lowered
        or "general industry standard" in lowered
    )


def had_number_redaction(answer_text: str) -> bool:
    """Detects if the backend's number-verification safety net redacted a
    hallucinated figure — surface this to the user instead of hiding it."""
    return "could not be verified" in answer_text.lower()


FOLLOWUP_MAP = {
    "room rent": ["What is the ICU/ICCU charge limit?", "Are there sub-limits for Gold/Senior Citizen plans?"],
    "icu": ["What is the room rent limit under this policy?"],
    "waiting period": ["What is the waiting period for cataract surgery?", "Is there a 30-day initial waiting period?"],
    "pre-existing": ["What is the waiting period for pre-existing diseases?"],
    "maternity": ["Does this policy cover infertility treatment or IVF?"],
    "exclusion": ["What are the permanent exclusions in this policy?"],
    "excluded": ["What are the permanent exclusions in this policy?"],
    "cancellation": ["What is the free look period?"],
    "cancel": ["What is the free look period?"],
    "renewal": ["What is the grace period for renewal?"],
    "renewing": ["What is the grace period for renewal?"],
    "idv": ["What if my car is stolen?", "What is the No Claim Bonus?"],
    "ncb": ["What is the IDV of my vehicle?"],
    "stolen": ["What is the IDV of my vehicle?"],
}


def get_followups(question: str, answer: str) -> list:
    combined = (question + " " + answer).lower()
    suggestions = []
    for keyword, followups in FOLLOWUP_MAP.items():
        if keyword in combined:
            for f in followups:
                if f.lower() not in question.lower() and f not in suggestions:
                    suggestions.append(f)
    return suggestions[:3]


def _wrap_long_tokens(text: str, max_len: int = 50) -> str:
    """
    FIX: fpdf2's multi_cell() throws 'Not enough horizontal space to render
    a single character' when a single unbroken 'word' (no spaces — e.g. a
    long URL, or markdown like '**Direct' if formatting collapses spaces)
    is wider than the page. fpdf2 can wrap at spaces but can't split a word
    on its own. Force-insert spaces into any overly-long token so it can
    always be wrapped.
    """
    def wrap_word(word: str) -> str:
        if len(word) <= max_len:
            return word
        return " ".join(word[i:i + max_len] for i in range(0, len(word), max_len))

    return " ".join(wrap_word(w) for w in text.split(" "))


def export_chat_as_pdf(messages: list) -> bytes:
    if not HAS_PDF_EXPORT:
        return b""
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(0, 10, "PolicyPilot - Chat Export")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 11)
        for msg in messages:
            role = "You" if msg["role"] == "user" else "PolicyPilot"
            pdf.set_font("Helvetica", "B", 11)
            safe_role = role.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, _wrap_long_tokens(safe_role))
            pdf.set_font("Helvetica", "", 11)
            # fpdf2's core fonts are Latin-1 only — degrade non-Latin1 chars
            # (like the rupee symbol) rather than crash the export.
            safe_text = msg["content"].encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 6, _wrap_long_tokens(safe_text))
            pdf.ln(3)
        output = pdf.output(dest="S")
        if isinstance(output, str):
            return output.encode("latin-1", "replace")
        return bytes(output)
    except Exception as e:
        st.sidebar.error(f"⚠️ Chat export failed: {e}")
        return b""


def call_ask_api(question: str):
    try:
        resp = requests.post(f"{API_BASE}/api/ask", json={"question": question}, timeout=120)
    except requests.exceptions.RequestException as e:
        return f"⚠️ Could not reach the backend: {e}", []
    if resp.status_code != 200:
        return f"⚠️ Error ({resp.status_code}): {resp.text[:300]}", []
    try:
        body = resp.json()
        data = body.get("data", body)
        answer = data[0] if isinstance(data, (list, tuple)) else str(data)
        sources = data[1] if isinstance(data, (list, tuple)) and len(data) > 1 else []
        return answer, sources
    except Exception as e:
        return f"⚠️ Could not parse response: {e}", []


def handle_question(question: str):
    """Shared logic for text-typed and voice-transcribed questions."""
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Analyzing policy clauses..."):
        answer, sources = call_ask_api(question)
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

    cited_pages = extract_cited_pages(answer)
    if cited_pages:
        st.session_state.viewer_page = cited_pages[0]


# ----------------------------------------------------------------------
# Sidebar: upload + summary
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("📁 Policy Document")
    uploaded_file = st.file_uploader("Upload a policy PDF", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Upload & Process", use_container_width=True):
            with st.spinner("Uploading and rebuilding knowledge base..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    resp = requests.post(f"{API_BASE}/api/upload", files=files, timeout=300)
                    if resp.status_code == 200:
                        st.success(f"✅ {uploaded_file.name} processed!")
                        st.session_state.messages = []
                        st.session_state.current_pdf_name = uploaded_file.name
                        st.session_state.viewer_page = 1
                    else:
                        st.error(f"Upload failed: {resp.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not reach backend: {e}")

    if st.session_state.current_pdf_name:
        st.caption(f"Active policy: **{st.session_state.current_pdf_name}**")

    st.divider()

    if st.button("📋 Generate Auto-Summary", use_container_width=True):
        with st.spinner("Analyzing policy and generating summary..."):
            try:
                resp = requests.get(f"{API_BASE}/api/summary", timeout=300)
                if resp.status_code == 200:
                    st.session_state.summary = resp.json()
                else:
                    st.error(f"Summary failed: {resp.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach backend: {e}")

    st.divider()

    if HAS_PDF_EXPORT and st.session_state.messages:
        try:
            pdf_bytes = export_chat_as_pdf(st.session_state.messages)
            if pdf_bytes:
                st.download_button(
                    "⬇️ Export Chat as PDF",
                    data=pdf_bytes,
                    file_name="policypilot_chat.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        except Exception as e:
            st.error(f"Chat export unavailable right now: {e}")
    elif not HAS_PDF_EXPORT:
        st.caption("Install `fpdf2` to enable chat export: `pip install fpdf2`")

    if not HAS_PDF_VIEWER:
        st.caption("⚠️ Install `pymupdf` to enable the PDF viewer panel.")


# ----------------------------------------------------------------------
# Top-level tabs
# ----------------------------------------------------------------------
tab_chat, tab_compare, tab_admin = st.tabs(["💬 Chat", "⚖️ Compare Policies", "🛠️ Admin / Tests"])

# ========================================================================
# TAB 1: Chat (main interface)
# ========================================================================
with tab_chat:
    st.title("📄 PolicyPilot")

    if "summary" in st.session_state:
        with st.expander(
            f"📋 Policy Summary (Type: {st.session_state.summary.get('policy_type_detected', 'Unknown')})",
            expanded=False,
        ):
            for item in st.session_state.summary.get("summary", []):
                st.markdown(f"**{item['label']}**")
                st.markdown(item["answer"])
                st.divider()

    col_chat, col_pdf = st.columns([3, 2])

    # ---- LEFT: chat ----
    with col_chat:
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                if msg["role"] == "assistant":
                    # Confidence badge
                    if looks_unconfirmed(msg["content"]):
                        st.warning("⚠️ Not confirmed in your policy — this is a general industry standard, not a guarantee from your document.")

                    # Number-hallucination-redaction disclaimer
                    if had_number_redaction(msg["content"]):
                        st.error("🔢 One or more figures could not be verified against your document and were redacted for safety. Please check the source page directly.")

                    # Clickable citations
                    cited_pages = extract_cited_pages(msg["content"])
                    if cited_pages and HAS_PDF_VIEWER:
                        cols = st.columns(len(cited_pages))
                        for j, page_num in enumerate(cited_pages):
                            if cols[j].button(f"📄 View Page {page_num}", key=f"cite_{i}_{page_num}"):
                                st.session_state.viewer_page = page_num
                                st.rerun()

                    # Follow-up suggestions (only for the LAST assistant message)
                    if i == len(st.session_state.messages) - 1:
                        prev_question = st.session_state.messages[i - 1]["content"] if i > 0 else ""
                        followups = get_followups(prev_question, msg["content"])
                        if followups:
                            st.caption("Related questions:")
                            fcols = st.columns(len(followups))
                            for k, fq in enumerate(followups):
                                if fcols[k].button(fq, key=f"followup_{i}_{k}"):
                                    handle_question(fq)
                                    st.rerun()

        # Voice input
        if HAS_VOICE:
            audio_value = st.audio_input("🎤 Or ask by voice")
            if audio_value is not None and st.session_state.get("last_audio_id") != id(audio_value):
                st.session_state.last_audio_id = id(audio_value)
                with st.spinner("Transcribing..."):
                    try:
                        client = GroqClient(api_key=os.environ.get("GROQ_API_KEY"))
                        transcription = client.audio.transcriptions.create(
                            file=("audio.wav", audio_value.getvalue()),
                            model="whisper-large-v3",
                        )
                        voice_question = transcription.text.strip()
                        if voice_question:
                            st.success(f"Heard: \"{voice_question}\"")
                            handle_question(voice_question)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Voice transcription failed: {e}")
        elif not HAS_VOICE:
            st.caption("🎤 Voice input needs `pip install groq` and GROQ_API_KEY set.")

        # Text input
        if question := st.chat_input("Ask a question about your policy..."):
            handle_question(question)
            st.rerun()

    # ---- RIGHT: PDF viewer ----
    with col_pdf:
        st.subheader("📖 Source Document")
        if not HAS_PDF_VIEWER:
            st.info("Install `pymupdf` (`pip install pymupdf`) to view PDF pages here.")
        elif not st.session_state.current_pdf_name:
            st.info("Upload a policy to see it here.")
        else:
            pdf_path = os.path.join(DOCS_DIR, st.session_state.current_pdf_name)
            img_bytes, page_count = render_pdf_page(pdf_path, st.session_state.viewer_page)
            if img_bytes:
                nav_cols = st.columns([1, 2, 1])
                if nav_cols[0].button("⬅️", use_container_width=True) and st.session_state.viewer_page > 1:
                    st.session_state.viewer_page -= 1
                    st.rerun()
                nav_cols[1].markdown(
                    f"<div style='text-align:center'>Page {st.session_state.viewer_page} / {page_count}</div>",
                    unsafe_allow_html=True,
                )
                if nav_cols[2].button("➡️", use_container_width=True) and st.session_state.viewer_page < page_count:
                    st.session_state.viewer_page += 1
                    st.rerun()
                st.image(img_bytes, use_container_width=True)
            else:
                st.warning("Could not render this PDF page. Check DOCS_DIR path matches the backend's docs/ folder.")

# ========================================================================
# TAB 2: Compare Policies
# ========================================================================
with tab_compare:
    st.title("⚖️ Compare Policies")
    st.info(
        "⚠️ **Backend limitation:** the server keeps only ONE policy's data active "
        "at a time (uploading a new PDF replaces the old one). To compare two "
        "policies: upload Policy A → ask & save your questions below → upload "
        "Policy B → ask & save the SAME questions → then view the comparison table."
    )

    compare_col_a, compare_col_b = st.columns(2)

    with compare_col_a:
        st.subheader("Policy A")
        label_a = st.text_input("Label for Policy A", value="Policy A", key="label_a")
        q_a = st.text_input("Question to ask & save", key="q_a")
        if st.button("Ask & Save to A", key="save_a") and q_a:
            with st.spinner("Asking..."):
                answer, _ = call_ask_api(q_a)
            st.session_state.compare_a.append({"question": q_a, "answer": answer, "label": label_a})
            st.success("Saved to Policy A")

    with compare_col_b:
        st.subheader("Policy B")
        label_b = st.text_input("Label for Policy B", value="Policy B", key="label_b")
        q_b = st.text_input("Question to ask & save", key="q_b")
        if st.button("Ask & Save to B", key="save_b") and q_b:
            with st.spinner("Asking..."):
                answer, _ = call_ask_api(q_b)
            st.session_state.compare_b.append({"question": q_b, "answer": answer, "label": label_b})
            st.success("Saved to Policy B")

    st.divider()
    st.subheader("Comparison Table")

    if st.session_state.compare_a or st.session_state.compare_b:
        all_questions = list({item["question"] for item in st.session_state.compare_a} |
                              {item["question"] for item in st.session_state.compare_b})
        for q in all_questions:
            st.markdown(f"**Q: {q}**")
            c1, c2 = st.columns(2)
            a_match = next((x for x in st.session_state.compare_a if x["question"] == q), None)
            b_match = next((x for x in st.session_state.compare_b if x["question"] == q), None)
            with c1:
                st.caption(a_match["label"] if a_match else "Policy A")
                st.markdown(a_match["answer"] if a_match else "_not asked yet_")
            with c2:
                st.caption(b_match["label"] if b_match else "Policy B")
                st.markdown(b_match["answer"] if b_match else "_not asked yet_")
            st.divider()

        if st.button("🗑️ Clear comparison data"):
            st.session_state.compare_a = []
            st.session_state.compare_b = []
            st.rerun()
    else:
        st.caption("No saved comparisons yet.")

# ========================================================================
# TAB 3: Admin / Regression Tests
# ========================================================================
with tab_admin:
    st.title("🛠️ Admin — Regression Tests")
    st.caption("Runs the known-good question/answer checks against whatever policy is currently active on the backend.")

    ADMIN_TEST_CASES = [
        {"name": "PED waiting period", "question": "What is the waiting period for pre-existing diseases (PED) under this policy?", "must_contain": ["48 months"]},
        {"name": "Cataract waiting period", "question": "What is the waiting period for cataract surgery?", "must_contain": ["24 months"]},
        {"name": "Room rent + ICU limits", "question": "What is the room rent limit and ICU charges limit under this policy?", "must_contain": ["1%", "2%", "per day"]},
        {"name": "Hernia/Hysterectomy sub-limit", "question": "What is the sub-limit for hernia and hysterectomy surgery?", "must_contain": ["25%", "1,00,000"]},
        {"name": "Maternity exclusion", "question": "Is maternity covered in this policy?", "must_contain": ["excl18"]},
        {"name": "Infertility/IVF exclusion", "question": "Does this policy cover infertility treatment or IVF?", "must_contain": ["excl17"]},
        {"name": "Missing scenario (outside India)", "question": "Does this policy cover treatment taken outside India?", "must_contain": ["not explicitly mentioned"]},
        {"name": "Road ambulance limit", "question": "What is the maximum amount covered for road ambulance charges?", "must_contain": ["2,500"]},
        {"name": "Free look + cancellation", "question": "What is the free look period, and what happens if I cancel the policy after 4 months?", "must_contain": ["15 days", "25%"]},
        {"name": "Renewal topic purity", "question": "What is the process for renewing this policy?", "must_contain": ["30 days"]},
    ]

    if st.button("▶️ Run All Tests", type="primary"):
        results = []
        progress = st.progress(0, text="Starting tests...")
        for idx, case in enumerate(ADMIN_TEST_CASES):
            progress.progress(idx / len(ADMIN_TEST_CASES), text=f"Running: {case['name']}")
            answer, _ = call_ask_api(case["question"])
            answer_lower = answer.lower()
            missing = [kw for kw in case["must_contain"] if kw.lower() not in answer_lower]
            results.append({
                "Test": case["name"],
                "Status": "✅ PASS" if not missing else "❌ FAIL",
                "Missing": ", ".join(missing) if missing else "-",
                "Answer (preview)": answer[:150] + ("..." if len(answer) > 150 else ""),
            })
        progress.progress(1.0, text="Done")
        st.session_state.admin_results = results

    if "admin_results" in st.session_state:
        results = st.session_state.admin_results
        passed = sum(1 for r in results if "PASS" in r["Status"])
        total = len(results)
        m1, m2, m3 = st.columns(3)
        m1.metric("Passed", passed)
        m2.metric("Failed", total - passed)
        m3.metric("Total", total)
        st.dataframe(results, use_container_width=True)