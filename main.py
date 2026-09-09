import os
import streamlit as st
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain, ask_question


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "processing" not in st.session_state:
    st.session_state.processing = False


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

.stApp {
    background: #f5f7fb;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] * {
    color: #f9fafb;
}

.sidebar-logo {
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 5px;
}

.sidebar-subtitle {
    color: #9ca3af !important;
    font-size: 13px;
    margin-bottom: 30px;
}

.sidebar-section {
    color: #9ca3af !important;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 25px;
    margin-bottom: 10px;
}


/* ==========================================================
   TOP HEADER
   ========================================================== */

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.brand {
    font-size: 28px;
    font-weight: 800;
    color: #111827;
}

.brand span {
    color: #6366f1;
}

.status {
    background: #ecfdf3;
    color: #027a48;
    border: 1px solid #abefc6;
    padding: 8px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}


/* ==========================================================
   HERO
   ========================================================== */

.hero {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #1e1b4b 55%,
        #312e81 100%
    );

    border-radius: 24px;
    padding: 40px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 38px;
    font-weight: 800;
    margin: 0;
}

.hero p {
    color: #c7d2fe;
    font-size: 16px;
    margin-top: 10px;
    max-width: 650px;
}


/* ==========================================================
   INPUT CARD
   ========================================================== */

.input-card {
    background: white;
    border: 1px solid #e4e7ec;
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 25px;
}

.input-title {
    font-size: 20px;
    font-weight: 750;
    color: #111827;
    margin-bottom: 5px;
}

.input-description {
    color: #667085;
    font-size: 14px;
}


/* ==========================================================
   SECTION TITLE
   ========================================================== */

.section-title {
    font-size: 22px;
    font-weight: 750;
    color: #111827;
    margin-top: 30px;
    margin-bottom: 15px;
}


/* ==========================================================
   METRIC CARDS
   ========================================================== */

.metric-card {
    background: white;
    border: 1px solid #e4e7ec;
    border-radius: 16px;
    padding: 20px;
    min-height: 105px;
}

.metric-icon {
    font-size: 22px;
}

.metric-label {
    color: #667085;
    font-size: 13px;
    margin-top: 8px;
}

.metric-value {
    font-size: 25px;
    font-weight: 750;
    color: #111827;
}


/* ==========================================================
   RESULT CARDS
   ========================================================== */

.result-card {
    background: white;
    border: 1px solid #e4e7ec;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 20px;
}

.result-card h3 {
    color: #111827;
    margin-top: 0;
}

.result-card p {
    color: #475467;
    line-height: 1.7;
}


/* ==========================================================
   CHAT
   ========================================================== */

.chat-container {
    background: white;
    border: 1px solid #e4e7ec;
    border-radius: 20px;
    padding: 20px;
}

.chat-user {
    background: #eef2ff;
    padding: 13px 16px;
    border-radius: 14px;
    margin: 10px 0;
    color: #312e81;
}

.chat-ai {
    background: #f9fafb;
    border: 1px solid #eaecf0;
    padding: 13px 16px;
    border-radius: 14px;
    margin: 10px 0;
    color: #344054;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {
    border-radius: 12px;
    min-height: 45px;
    font-weight: 700;
}


/* ==========================================================
   FILE UPLOADER
   ========================================================== */

[data-testid="stFileUploader"] {
    border-radius: 15px;
}


/* ==========================================================
   TABS
   ========================================================== */

button[data-baseweb="tab"] {
    font-weight: 650;
}


/* ==========================================================
   HIDE STREAMLIT DEFAULT FOOTER
   ========================================================== */

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">🎙️ Meeting AI</div>
        <div class="sidebar-subtitle">
            Intelligent meeting analysis
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Workspace</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📄 Meeting Results",
            "💬 AI Chat",
        ],
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="sidebar-section">AI Pipeline</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            background:#1f2937;
            padding:15px;
            border-radius:12px;
            font-size:13px;
            line-height:1.9;
        ">
        🎵 Audio Processing<br>
        🗣️ Whisper / Sarvam<br>
        🧠 Groq LLM<br>
        🔎 ChromaDB RAG
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Language</div>',
        unsafe_allow_html=True,
    )

    language = st.selectbox(
        "Meeting language",
        ["english", "hindi"],
        label_visibility="collapsed",
    )


# ============================================================
# TOP BAR
# ============================================================

# ============================================================
# TOP BAR
# ============================================================

st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            🎙️ AI <span>Meeting Assistant</span>
        </div>
        <div class="status">
            ● AI System Ready
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        """
        <div class="hero">
            <h1>Turn meetings into actionable insights.</h1>
            <p>
                Upload a meeting recording or paste a YouTube URL.
                Our AI will transcribe, summarize and analyze the
                conversation — then let you ask questions about it.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="input-card">

        <div class="input-title">
            🎥 Add your meeting
        </div>

        <div class="input-description">
            Choose a YouTube video or upload an audio/video recording.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    input_col1, input_col2 = st.columns([1, 1])

    with input_col1:

        st.markdown("### 🔗 YouTube")

        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="Paste YouTube meeting URL...",
            label_visibility="collapsed",
        )

    with input_col2:

        st.markdown("### 📁 Local file")

        uploaded_file = st.file_uploader(
            "Upload meeting",
            type=[
                "mp3",
                "wav",
                "m4a",
                "mp4",
                "webm",
                "mov",
                "avi",
            ],
            label_visibility="collapsed",
        )

    st.markdown("")

    analyze = st.button(
        "🚀  Analyze Meeting",
        type="primary",
        use_container_width=True,
    )

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    if analyze:

        if not youtube_url and uploaded_file is None:

            st.warning(
                "Please paste a YouTube URL or upload a meeting file."
            )

            st.stop()

        try:

            progress = st.progress(0)
            status = st.empty()

            # -----------------------------------------------
            # SOURCE
            # -----------------------------------------------

            if youtube_url:

                source = youtube_url

            else:

                upload_dir = "uploads"

                os.makedirs(
                    upload_dir,
                    exist_ok=True,
                )

                source = os.path.join(
                    upload_dir,
                    uploaded_file.name,
                )

                with open(source, "wb") as file:

                    file.write(
                        uploaded_file.getbuffer()
                    )

            # -----------------------------------------------
            # AUDIO
            # -----------------------------------------------

            status.info("🎵 Processing meeting audio...")
            progress.progress(15)

            chunks = process_input(source)

            # -----------------------------------------------
            # TRANSCRIPTION
            # -----------------------------------------------

            status.info("🗣️ Transcribing conversation...")
            progress.progress(35)

            transcript = transcribe_all(
                chunks,
                language,
            )

            # -----------------------------------------------
            # TITLE
            # -----------------------------------------------

            status.info("🏷️ Generating meeting title...")
            progress.progress(50)

            title = generate_title(transcript)

            # -----------------------------------------------
            # SUMMARY
            # -----------------------------------------------

            status.info("📝 Creating AI summary...")
            progress.progress(65)

            summary = summarize(transcript)

            # -----------------------------------------------
            # EXTRACTION
            # -----------------------------------------------

            status.info("✅ Extracting action items...")
            action_items = extract_action_items(
                transcript
            )

            progress.progress(75)

            status.info("🔑 Extracting decisions...")
            decisions = extract_key_decisions(
                transcript
            )

            progress.progress(82)

            status.info("❓ Finding open questions...")
            questions = extract_questions(
                transcript
            )

            progress.progress(90)

            # -----------------------------------------------
            # RAG
            # -----------------------------------------------

            status.info("🧠 Building meeting knowledge base...")

            rag_chain = build_rag_chain(
                transcript
            )

            progress.progress(100)

            # -----------------------------------------------
            # SAVE
            # -----------------------------------------------

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }

            st.session_state.chat_history = []

            status.success(
                "✅ Meeting analysis completed!"
            )

            st.balloons()

        except Exception as e:

            st.error(
                "❌ Something went wrong while processing the meeting."
            )

            st.exception(e)


# ============================================================
# RESULTS
# ============================================================

result = st.session_state.result


if page == "📄 Meeting Results":

    if result is None:

        st.info(
            "No meeting has been analyzed yet. "
            "Go to Dashboard and analyze a meeting."
        )

    else:

        st.markdown(
            f"""
            <div class="hero">
                <h1>📌 {result["title"]}</h1>
                <p>
                    AI-generated meeting intelligence
                    powered by your transcript.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ====================================================
        # METRICS
        # ====================================================

        transcript = result["transcript"]

        words = len(transcript.split())

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">📝</div>
                    <div class="metric-label">Transcript</div>
                    <div class="metric-value">
                        {words:,} words
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-icon">🤖</div>
                    <div class="metric-label">AI Model</div>
                    <div class="metric-value">
                        Groq
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-icon">🔎</div>
                    <div class="metric-label">Knowledge</div>
                    <div class="metric-value">
                        RAG
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col4:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-icon">🌐</div>
                    <div class="metric-label">Language</div>
                    <div class="metric-value">
                        AI
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-title">Meeting Intelligence</div>',
            unsafe_allow_html=True,
        )

        # ====================================================
        # TABS
        # ====================================================

        tabs = st.tabs(
            [
                "📝 Summary",
                "✅ Action Items",
                "🔑 Decisions",
                "❓ Questions",
                "📄 Transcript",
            ]
        )

        with tabs[0]:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown(
                result["summary"]
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            st.download_button(
                "⬇️ Download Summary",
                result["summary"],
                "meeting_summary.txt",
                use_container_width=True,
            )

        with tabs[1]:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown(
                result["action_items"]
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            st.download_button(
                "⬇️ Download Action Items",
                result["action_items"],
                "action_items.txt",
                use_container_width=True,
            )

        with tabs[2]:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown(
                result["key_decisions"]
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        with tabs[3]:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )

            st.markdown(
                result["open_questions"]
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        with tabs[4]:

            st.text_area(
                "Full transcript",
                result["transcript"],
                height=600,
                label_visibility="collapsed",
            )

            st.download_button(
                "⬇️ Download Transcript",
                result["transcript"],
                "meeting_transcript.txt",
                use_container_width=True,
            )


# ============================================================
# AI CHAT
# ============================================================

if page == "💬 AI Chat":

    st.markdown(
        """
        <div class="hero">
            <h1>💬 Ask your meeting</h1>
            <p>
                Ask questions and get answers based on the
                meeting transcript using RAG.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result is None:

        st.info(
            "Analyze a meeting first to activate AI Chat."
        )

    else:

        # ----------------------------------------------------
        # CHAT HISTORY
        # ----------------------------------------------------

        for message in st.session_state.chat_history:

            if message["role"] == "user":

                st.markdown(
                    f"""
                    <div class="chat-user">
                        <b>👤 You</b><br><br>
                        {message["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    f"""
                    <div class="chat-ai">
                        <b>🤖 Meeting AI</b><br><br>
                        {message["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ----------------------------------------------------
        # QUESTION
        # ----------------------------------------------------

        question = st.chat_input(
            "Ask anything about the meeting..."
        )

        if question:

            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            with st.spinner(
                "🔎 Searching meeting knowledge..."
            ):

                try:

                    answer = ask_question(
                        result["rag_chain"],
                        question,
                    )

                except Exception as e:

                    answer = (
                        f"Sorry, I couldn't answer that.\n\n"
                        f"Error: {e}"
                    )

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            st.rerun()