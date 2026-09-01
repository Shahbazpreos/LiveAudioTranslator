import soundcard as sc
import numpy as np

from faster_whisper import WhisperModel
from transformers import MarianMTModel, MarianTokenizer

import threading
import queue
import time
import warnings


# ============================================================
# SETTINGS
# ============================================================

SAMPLE_RATE = 16000
WINDOW_SECONDS = 4
AUDIO_THRESHOLD = 0.002

WHISPER_MODEL = "tiny.en"

QUEUE_SIZE = 2


# ============================================================
# TRANSLATION MODELS
# ============================================================

URDU_MODEL = "Helsinki-NLP/opus-mt-en-ur"
CHINESE_MODEL = "Helsinki-NLP/opus-mt-en-zh"


# ============================================================
# HIDE SOUNDCARD WARNINGS
# ============================================================

warnings.filterwarnings(
    "ignore",
    message="data discontinuity in recording"
)


# ============================================================
# GLOBALS
# ============================================================

audio_queue = queue.Queue(
    maxsize=QUEUE_SIZE
)

stop_event = threading.Event()


# ============================================================
# LANGUAGE SELECTION
# ============================================================

print("\n========================================")
print(" LIVE AUDIO TRANSLATOR - WINDOWS")
print("========================================")

print("\n1. 🇵🇰 Urdu")
print("2. 🇨🇳 Chinese")

choice = input(
    "\nSelect language (1 or 2): "
).strip()


if choice == "2":

    TARGET_LANGUAGE = "Chinese"
    TRANSLATION_MODEL = CHINESE_MODEL
    OUTPUT_PREFIX = "🇨🇳 Chinese:"

else:

    TARGET_LANGUAGE = "Urdu"
    TRANSLATION_MODEL = URDU_MODEL
    OUTPUT_PREFIX = "🇵🇰 Urdu:"


# ============================================================
# LOAD WHISPER
# ============================================================

print("\nLoading Whisper model...")

whisper = WhisperModel(
    WHISPER_MODEL,
    device="cpu",
    compute_type="int8"
)

print("Whisper loaded.")


# ============================================================
# LOAD TRANSLATOR
# ============================================================

print(
    f"\nLoading {TARGET_LANGUAGE} translator..."
)

tokenizer = MarianTokenizer.from_pretrained(
    TRANSLATION_MODEL
)

translator = MarianMTModel.from_pretrained(
    TRANSLATION_MODEL
)

translator.eval()

print(
    f"{TARGET_LANGUAGE} translator loaded."
)


# ============================================================
# WINDOWS LOOPBACK
# ============================================================

speaker = sc.default_speaker()

print("\nWindows output device:")
print(speaker.name)

loopback = sc.get_microphone(
    id=str(speaker.id),
    include_loopback=True
)

print("\nLoopback capture device:")
print(loopback.name)


# ============================================================
# TRANSLATE TEXT
# ============================================================

def translate_text(text):

    inputs = tokenizer(
        [text],
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )

    translated = translator.generate(
        **inputs,
        num_beams=1,
        do_sample=False,
        max_length=192
    )

    result = tokenizer.decode(
        translated[0],
        skip_special_tokens=True
    )

    return result.strip()


# ============================================================
# CAPTURE THREAD
# ============================================================

def capture_audio():

    frames_per_chunk = (
        SAMPLE_RATE * WINDOW_SECONDS
    )

    try:

        with loopback.recorder(
            samplerate=SAMPLE_RATE,
            channels=1
        ) as recorder:

            while not stop_event.is_set():

                audio = recorder.record(
                    numframes=frames_per_chunk
                )

                audio = np.asarray(
                    audio,
                    dtype=np.float32
                )

                audio = audio.reshape(-1)


                # Keep latency low.
                # Drop oldest queued audio if processing falls behind.

                if audio_queue.full():

                    try:
                        audio_queue.get_nowait()

                    except queue.Empty:
                        pass


                try:

                    audio_queue.put_nowait(
                        audio
                    )

                except queue.Full:
                    pass


    except Exception as error:

        print(
            f"\nAudio capture error: {error}"
        )

        stop_event.set()


# ============================================================
# PROCESS AUDIO
# ============================================================

def process_audio():

    while not stop_event.is_set():

        try:

            audio = audio_queue.get(
                timeout=0.5
            )

        except queue.Empty:

            continue


        # ----------------------------------------------------
        # AUDIO LEVEL
        # ----------------------------------------------------

        peak = float(
            np.max(
                np.abs(audio)
            )
        )

        rms = float(
            np.sqrt(
                np.mean(audio ** 2)
            )
        )

        print(
            f"Audio level | "
            f"peak={peak:.4f} "
            f"rms={rms:.4f}"
        )


        # ----------------------------------------------------
        # SILENCE
        # ----------------------------------------------------

        if rms < AUDIO_THRESHOLD:

            print("Silence\n")
            continue


        # ----------------------------------------------------
        # WHISPER
        # ----------------------------------------------------

        print("🔄 Transcribing...")

        speech_start = time.perf_counter()

        segments, info = whisper.transcribe(
            audio,

            language="en",

            beam_size=1,

            vad_filter=True,

            vad_parameters={
                "min_silence_duration_ms": 300
            },

            condition_on_previous_text=False,

            temperature=0.0,

            word_timestamps=False,

            no_speech_threshold=0.5,

            log_prob_threshold=-1.0
        )


        text_parts = []

        for segment in segments:

            text = segment.text.strip()

            if text:

                text_parts.append(
                    text
                )


        english_text = " ".join(
            text_parts
        ).strip()


        speech_time = (
            time.perf_counter()
            - speech_start
        )


        if not english_text:

            print(
                f"No speech detected "
                f"({speech_time:.2f}s)\n"
            )

            continue


        # ----------------------------------------------------
        # TRANSLATION
        # ----------------------------------------------------

        print(
            f"🇬🇧 English: {english_text}"
        )

        print("🌐 Translating...")

        translation_start = time.perf_counter()

        translated_text = translate_text(
            english_text
        )

        translation_time = (
            time.perf_counter()
            - translation_start
        )


        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        print(
            f"{OUTPUT_PREFIX} "
            f"{translated_text}"
        )

        total_time = (
            speech_time
            + translation_time
        )

        print(
            f"⚡ Speech: "
            f"{speech_time:.2f}s | "
            f"Translation: "
            f"{translation_time:.2f}s | "
            f"Total processing: "
            f"{total_time:.2f}s\n"
        )


# ============================================================
# START
# ============================================================

print("\n========================================")
print(" FAST LIVE WINDOWS TRANSLATOR")
print("========================================")

print(
    f"Whisper     : {WHISPER_MODEL}"
)

print(
    f"Language    : {TARGET_LANGUAGE}"
)

print(
    f"Sample rate : {SAMPLE_RATE}"
)

print(
    f"Window      : {WINDOW_SECONDS}s"
)

print(
    f"Queue       : {QUEUE_SIZE}"
)

print("========================================")

print("\nPlay English audio on Windows.")
print("Press Ctrl+C to stop.\n")


capture_thread = threading.Thread(
    target=capture_audio,
    daemon=True
)

capture_thread.start()


try:

    process_audio()


except KeyboardInterrupt:

    print("\nStopping...")

    stop_event.set()


capture_thread.join(
    timeout=2
)

print("Done.")