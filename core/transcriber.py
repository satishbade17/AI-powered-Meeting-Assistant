import os
import shutil
import whisper
import requests
from pydub import AudioSegment


# ============================================================
# FFMPEG CONFIGURATION
# ============================================================

FFMPEG_DIR = (
    r"C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0.1-full_build\bin"
)

FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
FFPROBE_PATH = os.path.join(FFMPEG_DIR, "ffprobe.exe")

# Make FFmpeg visible to Python / Whisper
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

# Tell pydub exactly where FFmpeg is
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH

print("Whisper FFmpeg:", shutil.which("ffmpeg"))
print("Whisper FFprobe:", shutil.which("ffprobe"))


# ============================================================
# SARVAM CONFIGURATION
# ============================================================

# Sarvam synchronous API accepts audio <= 30 seconds.
# We use 25 seconds to keep a safety margin.
SARVAM_PIECE_SECONDS = 25

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

SARVAM_STT_TRANSLATE_URL = (
    "https://api.sarvam.ai/speech-to-text-translate"
)

SARVAM_MODEL = os.getenv(
    "SARVAM_STT_MODEL",
    "saaras:v2.5"
)


# ============================================================
# WHISPER MODEL
# ============================================================

_model = None


def load_model():
    """Load Whisper model only once."""

    global _model

    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")

        _model = whisper.load_model(WHISPER_MODEL)

        print("Whisper model loaded.")

    return _model


# ============================================================
# WHISPER TRANSCRIPTION
# ============================================================

def transcribe_chunk_whisper(chunk_path: str) -> str:
    """Transcribe one audio chunk using local Whisper."""

    model = load_model()

    print(f"Whisper processing: {chunk_path}")

    result = model.transcribe(
        chunk_path,
        task="transcribe"
    )

    return result["text"].strip()


# ============================================================
# SARVAM API
# ============================================================

def _send_to_sarvam(piece_path: str) -> str:
    """Send one <=30 second WAV file to Sarvam."""

    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }

    with open(piece_path, "rb") as f:

        files = {
            "file": (
                os.path.basename(piece_path),
                f,
                "audio/wav"
            )
        }

        data = {
            "model": SARVAM_MODEL,
            "with_diarization": "false"
        }

        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120
        )

    if not response.ok:

        print(
            f"\n❌ Sarvam returned "
            f"{response.status_code}"
        )

        print(
            f"Response body: "
            f"{response.text}\n"
        )

        response.raise_for_status()

    return response.json().get(
        "transcript",
        ""
    ).strip()


# ============================================================
# SARVAM TRANSCRIPTION
# ============================================================

def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API accepts <=30 seconds.

    Each larger chunk is divided into
    25-second pieces.
    """

    if not SARVAM_API_KEY:

        raise RuntimeError(
            "SARVAM_API_KEY is not set "
            "in environment / .env"
        )

    audio = AudioSegment.from_wav(
        chunk_path
    )

    piece_ms = (
        SARVAM_PIECE_SECONDS * 1000
    )

    full_text = ""

    total_pieces = (
        (len(audio) + piece_ms - 1)
        // piece_ms
    )

    for i, start in enumerate(
        range(
            0,
            len(audio),
            piece_ms
        )
    ):

        piece = audio[
            start:start + piece_ms
        ]

        piece_path = (
            f"{chunk_path}_sv_{i}.wav"
        )

        piece.export(
            piece_path,
            format="wav"
        )

        try:

            print(
                f"  → Sarvam piece "
                f"{i + 1}/{total_pieces} ..."
            )

            text = _send_to_sarvam(
                piece_path
            )

            if text:
                full_text += text + " "

        finally:

            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()


# ============================================================
# TRANSCRIPTION ROUTER
# ============================================================

def transcribe_chunk(
    chunk_path: str,
    language: str = "english"
) -> str:

    """
    Select transcription engine.

    english  -> Whisper
    hindi -> Sarvam
    """

    if language.lower() == "hindi":

        return transcribe_chunk_sarvam(
            chunk_path
        )

    return transcribe_chunk_whisper(
        chunk_path
    )


# ============================================================
# TRANSCRIBE ALL CHUNKS
# ============================================================

def transcribe_all(
    chunks: list,
    language: str = "english"
) -> str:

    full_transcript = ""

    engine = (
        "Sarvam AI"
        if language.lower() == "hindi"
        else "Whisper"
    )

    print(
        f"Using {engine} for transcription."
    )

    for i, chunk in enumerate(chunks):

        print(
            f"Transcribing chunk "
            f"{i + 1}/{len(chunks)}..."
        )

        text = transcribe_chunk(
            chunk,
            language=language
        )

        if text:
            full_transcript += (
                text + " "
            )

    print("Transcription complete.")

    return full_transcript.strip()