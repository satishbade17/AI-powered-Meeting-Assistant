import os
import shutil
import yt_dlp

from pydub import AudioSegment


# ============================================================
# DIRECTORIES
# ============================================================

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ============================================================
# FFMPEG CONFIGURATION
# ============================================================

# Your FFmpeg installation directory
FFMPEG_DIR = (
    r"C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0.1-full_build\bin"
)

FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
FFPROBE_PATH = os.path.join(FFMPEG_DIR, "ffprobe.exe")


def check_ffmpeg():
    """
    Check whether FFmpeg and ffprobe are available.
    """

    # First check explicitly configured path
    if os.path.exists(FFMPEG_PATH) and os.path.exists(FFPROBE_PATH):

        print("✅ FFmpeg found:")
        print(f"   {FFMPEG_PATH}")

        print("✅ ffprobe found:")
        print(f"   {FFPROBE_PATH}")

        return True

    # Otherwise check Windows PATH
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")

    if ffmpeg and ffprobe:

        print("✅ FFmpeg found in PATH:")
        print(f"   {ffmpeg}")

        print("✅ ffprobe found in PATH:")
        print(f"   {ffprobe}")

        return True

    print("❌ FFmpeg or ffprobe not found.")

    print("\nPlease check:")
    print(FFMPEG_PATH)
    print(FFPROBE_PATH)

    return False


# ============================================================
# YOUTUBE AUDIO DOWNLOAD
# ============================================================

def download_youtube_audio(url: str) -> str:

    if not check_ffmpeg():

        raise RuntimeError(
            "FFmpeg and ffprobe are required for YouTube audio "
            "download. Please check the FFmpeg installation path."
        )

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {

        "format": "bestaudio/best",

        "outtmpl": output_path,

        # IMPORTANT
        "ffmpeg_location": FFMPEG_DIR,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        "quiet": False,

        "noplaylist": True,
    }

    print("⬇️ Downloading YouTube audio...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)

    # yt-dlp originally gives .webm/.m4a etc.
    # FFmpeg postprocessor creates .wav
    base = os.path.splitext(filename)[0]

    wav_path = base + ".wav"

    if not os.path.exists(wav_path):

        raise FileNotFoundError(
            f"Audio download completed but WAV file was not found:\n"
            f"{wav_path}"
        )

    print(f"✅ Audio downloaded: {wav_path}")

    return wav_path


# ============================================================
# LOCAL FILE → WAV
# ============================================================

def convert_to_wav(input_path: str) -> str:

    if not check_ffmpeg():

        raise RuntimeError(
            "FFmpeg and ffprobe are required for audio conversion."
        )

    # Tell pydub exactly where FFmpeg is
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffprobe = FFPROBE_PATH

    print("🔄 Converting file to WAV...")

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(
        input_path
    )

    # Whisper works well with mono 16 kHz audio
    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(
        output_path,
        format="wav"
    )

    print(f"✅ WAV created: {output_path}")

    return output_path


# ============================================================
# CHUNK AUDIO
# ============================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10
) -> list:

    print("✂️ Splitting audio into chunks...")

    audio = AudioSegment.from_wav(
        wav_path
    )

    chunk_ms = (
        chunk_minutes
        * 60
        * 1000
    )

    chunks = []

    for i, start in enumerate(
        range(
            0,
            len(audio),
            chunk_ms
        )
    ):

        chunk = audio[
            start:start + chunk_ms
        ]

        chunk_path = (
            f"{wav_path}_chunk_{i}.wav"
        )

        chunk.export(
            chunk_path,
            format="wav"
        )

        chunks.append(
            chunk_path
        )

    return chunks


# ============================================================
# MAIN AUDIO PROCESSOR
# ============================================================

def process_input(source: str) -> list:

    # Make sure FFmpeg is available before doing anything
    check_ffmpeg()

    if (
        source.startswith("http://")
        or source.startswith("https://")
    ):

        print(
            "Detected YouTube URL. "
            "Downloading audio..."
        )

        wav_path = download_youtube_audio(
            source
        )

    else:

        print(
            "Detected local file. "
            "Converting to WAV..."
        )

        wav_path = convert_to_wav(
            source
        )

    print("Chunking audio...")

    chunks = chunk_audio(
        wav_path
    )

    print(
        f"Audio ready — "
        f"{len(chunks)} chunk(s) created."
    )

    return chunks