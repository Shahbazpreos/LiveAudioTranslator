import soundcard as sc
import numpy as np

from faster_whisper import WhisperModel

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
# HIDE SOUNDCARD DISCONTINUITY WARNINGS
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
# LOAD WHISPER
# ============================================================

print("\nLoading Whisper model...")

model = WhisperModel(
    WHISPER_MODEL,
    device="cpu",
    compute_type="int8"
)

print("Whisper loaded.")


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

                # --------------------------------------------
                # Keep latency low.
                #
                # If Whisper cannot keep up, discard the
                # oldest queued chunk and keep the newest one.
                # --------------------------------------------

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
# TRANSCRIPTION
# ============================================================

def transcribe_audio():

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

        print("Transcribing...")

        start = time.perf_counter()

        segments, info = model.transcribe(
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


        text = " ".join(
            text_parts
        ).strip()


        elapsed = (
            time.perf_counter()
            - start
        )


        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        if text:

            print(
                f"English: {text}"
            )

            print(
                f"Whisper time: "
                f"{elapsed:.2f}s\n"
            )

        else:

            print(
                f"No speech detected "
                f"({elapsed:.2f}s)\n"
            )


# ============================================================
# MAIN
# ============================================================

print("\n========================================")
print(" LIVE WINDOWS AUDIO TRANSCRIPTION")
print("========================================")

print(
    f"Whisper : {WHISPER_MODEL}"
)

print(
    f"Rate    : {SAMPLE_RATE}"
)

print(
    f"Window  : {WINDOW_SECONDS}s"
)

print(
    f"Queue   : {QUEUE_SIZE}"
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

    transcribe_audio()


except KeyboardInterrupt:

    print("\nStopping...")

    stop_event.set()


capture_thread.join(
    timeout=2
)

print("Done.")