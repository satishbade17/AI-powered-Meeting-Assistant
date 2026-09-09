# 🎙️ AI Meeting Assistant

An AI-powered meeting analysis application that converts meeting recordings or YouTube videos into structured, searchable meeting intelligence.

The application can transcribe conversations, generate a meeting title and summary, extract action items, identify key decisions, find open questions, and provide an interactive RAG-based chat interface for asking questions about the meeting.

---

## ✨ Features

- 🎥 **YouTube & Local File Support**
  - Paste a YouTube URL
  - Upload audio/video meeting recordings
  - Supports MP3, WAV, M4A, MP4, WEBM, MOV and AVI

- 🎵 **Audio Processing**
  - Downloads YouTube audio using `yt-dlp`
  - Converts audio/video to WAV using FFmpeg
  - Splits long recordings into manageable chunks

- 🗣️ **AI Transcription**
  - English transcription using local OpenAI Whisper
  - Hinglish transcription/translation using Sarvam AI
  - Sarvam audio is divided into 25-second pieces for the synchronous API

- 🧠 **Meeting Intelligence**
  - Automatic meeting title generation
  - AI-generated meeting summary
  - Action item extraction
  - Key decision extraction
  - Open question/follow-up extraction

- 🔎 **RAG-based Meeting Q&A**
  - Transcript is split into chunks
  - Embeddings are generated using Hugging Face
  - ChromaDB stores the vector representations
  - Relevant transcript context is retrieved for user questions
  - Groq LLM generates the final answer

- 💬 **Interactive AI Chat**
  - Ask questions about the analyzed meeting
  - Maintains chat history during the Streamlit session

- 🖥️ **Streamlit Dashboard**
  - Dashboard for uploading/analyzing meetings
  - Meeting Results page
  - AI Chat page
  - Progress indicators and analysis status

---

## 🏗️ System Architecture

```text
                  ┌──────────────────────┐
                  │   YouTube URL /      │
                  │   Local Audio/Video  │
                  └──────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     yt-dlp      │
                    │ YouTube Download │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     FFmpeg      │
                    │ Audio Conversion │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Audio Chunking  │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌──────────────┐          ┌──────────────┐
        │    Whisper   │          │   Sarvam AI  │
        │    English   │          │   Hinglish   │
        └──────┬───────┘          └──────┬───────┘
               │                         │
               └────────────┬────────────┘
                            ▼
                     ┌─────────────┐
                     │ Transcript  │
                     └──────┬──────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
       ┌──────────┐   ┌───────────┐  ┌────────────┐
       │  Title   │   │  Summary  │  │ Extraction │
       └──────────┘   └───────────┘  └─────┬──────┘
                                          │
                                  ┌───────┼────────┐
                                  ▼       ▼        ▼
                               Actions Decisions Questions

                            Transcript
                                │
                                ▼
                       ┌────────────────┐
                       │ Text Splitting │
                       └───────┬────────┘
                               ▼
                     ┌──────────────────┐
                     │ Hugging Face     │
                     │ Embeddings       │
                     └────────┬─────────┘
                              ▼
                         ┌─────────┐
                         │ChromaDB │
                         └────┬────┘
                              │
                         User Question
                              │
                              ▼
                       ┌──────────────┐
                       │ RAG Retrieval│
                       └──────┬───────┘
                              ▼
                         ┌─────────┐
                         │  Groq   │
                         │   LLM    │
                         └────┬────┘
                              ▼
                         AI Answer
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | Web interface |
| yt-dlp | YouTube audio download |
| FFmpeg | Audio/video conversion |
| Pydub | Audio processing and chunking |
| OpenAI Whisper | Local English speech-to-text |
| Sarvam AI | Hinglish speech-to-text/translation |
| Groq | LLM inference |
| LangChain | LLM chains and RAG workflow |
| Hugging Face | Transcript embeddings |
| ChromaDB | Vector database |
| Requests | Sarvam API communication |
| python-dotenv | Environment variable management |

---

## 📁 Project Structure

```text
videoAgent/
│
├── main.py
├── README.md
├── requirements.txt
├── .env
│
├── core/
│   ├── __init__.py
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── extractor.py
│   ├── rag_engine.py
│   └── vector_store.py
│
├── utils/
│   ├── __init__.py
│   └── audio_processor.py
│
├── downloads/
│   └── downloaded/converted audio files
│
├── uploads/
│   └── uploaded meeting files
│
└── vector_db/
    └── ChromaDB data
```

---

## ⚙️ Requirements

Recommended:

- Python 3.10+
- Windows/Linux
- FFmpeg
- Internet connection for YouTube downloads, Groq and Sarvam
- Sufficient RAM/storage for the Whisper model and embeddings

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd videoAgent
```

### 2. Create the virtual environment

Using `uv`:

```powershell
uv venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
uv pip install -r requirements.txt
```

Or install the project dependencies with your preferred Python package manager.

---

## 🔧 FFmpeg Setup

FFmpeg is required by the audio-processing pipeline and OpenAI Whisper.

Verify:

```powershell
ffmpeg -version
ffprobe -version
```

If FFmpeg is not available through the Windows PATH, configure the FFmpeg directory in the audio-processing/transcription code.

The application can explicitly add the FFmpeg `bin` directory to Python's PATH so Whisper can locate `ffmpeg.exe`.

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
SARVAM_API_KEY=your_sarvam_api_key

WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

### API keys

You need:

- **Groq API key** for title generation, summaries, extraction and RAG answers
- **Sarvam API key** only when using Hinglish transcription

Never commit `.env` to GitHub.

Add this to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
downloads/
uploads/
vector_db/
*.pyc
```

---

## ▶️ Run the Application

Start Streamlit:

```powershell
uv run streamlit run main.py
```

Then open the local Streamlit URL shown in the terminal, normally:

```text
http://localhost:8501
```

---

## 🔄 Application Workflow

### Step 1 — Add a meeting

Choose either:

```text
YouTube URL
        OR
Local audio/video file
```

### Step 2 — Process audio

The application:

1. Detects the input source
2. Downloads YouTube audio if required
3. Converts the input to WAV
4. Converts audio to mono/16 kHz
5. Splits long recordings into chunks

### Step 3 — Transcribe

For English:

```text
Audio → Whisper → Transcript
```

For Hinglish:

```text
Audio
  ↓
25-second pieces
  ↓
Sarvam AI
  ↓
English transcript
```

### Step 4 — Generate meeting intelligence

The transcript is sent to the Groq-powered LangChain pipelines to generate:

- Meeting title
- Summary
- Action items
- Key decisions
- Open questions

### Step 5 — Build RAG knowledge base

The transcript is:

```text
Transcript
   ↓
Text splitting
   ↓
Embeddings
   ↓
ChromaDB
```

### Step 6 — Ask questions

When the user asks a question:

```text
Question
   ↓
Vector similarity search
   ↓
Relevant transcript chunks
   ↓
Groq LLM
   ↓
Answer
```

This allows the user to ask questions specifically about the analyzed meeting.

---

## 🧠 RAG Implementation

The vector store uses:

```text
Embedding Model:
all-MiniLM-L6-v2
```

Transcript chunks are created using:

```text
Chunk size: 500
Chunk overlap: 50
```

The vector database is stored locally in:

```text
vector_db/
```

The retriever uses similarity search and retrieves the most relevant transcript chunks.

---

## 🤖 Groq LLM

The application uses Groq for the LLM layer.

Current model:

```text
openai/gpt-oss-120b
```

It is used for:

- Meeting title generation
- Summarization
- Action item extraction
- Decision extraction
- Question extraction
- RAG-based answers

---

## 🖥️ User Interface

The Streamlit application contains three main areas:

### 🏠 Dashboard

- Meeting input
- YouTube URL
- Local file uploader
- Language selection
- Analyze Meeting button
- Processing progress

### 📄 Meeting Results

Displays:

- Meeting title
- Transcript statistics
- Summary
- Action items
- Key decisions
- Open questions
- Full transcript
- Download options

### 💬 AI Chat

Provides:

- Meeting-specific Q&A
- RAG-based answers
- Chat history
- Transcript-grounded responses

---

## 🌐 Supported Languages

### English

Uses:

```text
OpenAI Whisper
```

### Hinglish

Uses:

```text
Sarvam AI
```

The application can therefore support meetings where participants communicate using a mixture of Hindi and English.

---

## 📌 Example Use Case

A 40-minute Python development meeting can be processed into:

```text
Meeting Title
    ↓
Python Project Development Discussion

Summary
    ↓
AI-generated meeting summary

Action Items
    ↓
1. Develop data processing module
2. Prepare API documentation
3. Implement unit tests

Key Decisions
    ↓
1. Use FastAPI for backend
2. Use Streamlit for interface
3. Use PyTest for testing

Open Questions
    ↓
1. Which database should be used?
2. What is the deployment strategy?
3. Is authentication required?

AI Chat
    ↓
"What were the main decisions?"
"What are my assigned tasks?"
"What testing approach was discussed?"
```

---

## 🔒 Security

- Store API keys in `.env`
- Never upload API keys to GitHub
- Add `.env` to `.gitignore`
- Do not hard-code API keys in Python files
- Remove sensitive meeting recordings before publishing the repository

---

## 🐛 Troubleshooting

### FFmpeg not found

Check:

```powershell
ffmpeg -version
```

If it fails, install/configure FFmpeg and ensure its `bin` directory is available to Python.

### Whisper cannot find FFmpeg

Check from the project environment:

```powershell
uv run python -c "import shutil; print(shutil.which('ffmpeg')); print(shutil.which('ffprobe'))"
```

Both should return valid executable paths.

### Groq API key error

Check:

```powershell
uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(bool(os.getenv('GROQ_API_KEY')))"
```

Expected:

```text
True
```

### Groq model not found

Make sure all old model references have been replaced with:

```text
openai/gpt-oss-120b
```

Search the project:

```powershell
Get-ChildItem -Path . -Recurse -Filter *.py | Select-String "llama-3.3-70b-versatile"
```

There should be no remaining references.

### Sarvam API error

Check:

```env
SARVAM_API_KEY=your_key
```

Also make sure the selected language is `hinglish`.

### CPU Whisper warning

You may see:

```text
FP16 is not supported on CPU; using FP32 instead
```

This is expected when Whisper runs on a CPU and is not an application failure.

---

## 📊 Project Pipeline Summary

```text
Input
  │
  ├── YouTube
  │
  └── Local File
        │
        ▼
   Audio Processing
        │
        ▼
      FFmpeg
        │
        ▼
   Audio Chunking
        │
        ▼
 ┌──────┴───────┐
 │              │
Whisper       Sarvam
English       Hinglish
 │              │
 └──────┬───────┘
        ▼
    Transcript
        │
        ├───────────────┐
        ▼               ▼
   Groq Analysis      RAG
        │               │
        ├─ Title        ├─ Embeddings
        ├─ Summary      ├─ ChromaDB
        ├─ Actions      └─ Retrieval
        ├─ Decisions          │
        └─ Questions          ▼
                         Groq Answer
                              │
                              ▼
                         AI Chat
```

---

## 🎯 Learning Outcomes

This project demonstrates practical implementation of:

- Python application development
- Speech-to-text processing
- Audio/video processing
- Local AI model integration
- API integration
- Prompt engineering
- LangChain LCEL pipelines
- Large Language Models
- Retrieval-Augmented Generation (RAG)
- Vector databases
- Embeddings
- Streamlit application development
- Environment variable management
- AI-powered information extraction

---

## 🔮 Future Improvements

Possible future enhancements:

- 👥 Speaker diarization
- ⏱️ Timestamped transcript
- 📄 PDF meeting reports
- 📊 Meeting analytics dashboard
- 🎯 Speaker-wise action items
- 🔍 Better semantic search
- 🌍 More Indian language support
- ☁️ Cloud deployment
- 🔐 User authentication
- 💾 Persistent meeting history
- 📤 Export to PDF/Word
- 📈 Meeting sentiment and topic analysis

---

## 👩‍💻 Project

**AI Meeting Assistant**

Built with Python, Streamlit, Whisper, Sarvam AI, Groq, LangChain, Hugging Face and ChromaDB.

---

## ⭐ If you found this project useful

Consider giving the repository a ⭐ and sharing feedback or suggestions.
