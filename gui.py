import tkinter as tk
from tkinter import ttk

import soundcard as sc
import numpy as np

from faster_whisper import WhisperModel
from transformers import MarianMTModel, MarianTokenizer

import torch

import threading
import queue
import time
import warnings
import sys
import os

import pystray
from PIL import Image, ImageDraw

from pynput import keyboard

import arabic_reshaper
from bidi.algorithm import get_display


# ============================================================
# COLORS
# ============================================================

BG = "#111318"
CARD = "#1A1D24"
CARD_2 = "#20242D"

TEXT = "#F2F4F8"
SUBTEXT = "#9AA3B2"

ACCENT = "#4F8CFF"
ACCENT_HOVER = "#6A9EFF"

GREEN = "#35D07F"
RED = "#FF5C5C"
ORANGE = "#FFB84D"

BORDER = "#2A2F3A"


# ============================================================
# RESOURCE PATH
# ============================================================

def resource_path(relative_path):

    if getattr(sys, "frozen", False):

        base_path = sys._MEIPASS

    else:

        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base_path,
        relative_path
    )


# ============================================================
# SETTINGS
# ============================================================

SAMPLE_RATE = 16000
WINDOW_SECONDS = 4
AUDIO_THRESHOLD = 0.002

WHISPER_MODEL = resource_path(
    os.path.join(
        "models",
        "whisper-tiny-en"
    )
)

URDU_MODEL = resource_path(
    os.path.join(
        "models",
        "marian-en-ur"
    )
)

CHINESE_MODEL = resource_path(
    os.path.join(
        "models",
        "marian-en-zh"
    )
)

QUEUE_SIZE = 2

GLOBAL_HOTKEY = "<ctrl>+<alt>+<space>"


# ============================================================
# WARNINGS
# ============================================================

warnings.filterwarnings(
    "ignore",
    message="data discontinuity in recording"
)


# ============================================================
# URDU FORMATTER
# ============================================================

def format_urdu(text):

    try:

        reshaped = arabic_reshaper.reshape(text)

        return get_display(reshaped)

    except Exception:

        return text


# ============================================================
# APPLICATION
# ============================================================

class LiveAudioTranslatorGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("Live Audio Translator")

        self.root.geometry("860x700")
        self.root.minsize(650, 520)

        self.root.configure(bg=BG)

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.running = False
        self.loading = False
        self.compact = False

        self.stop_event = threading.Event()

        self.audio_queue = queue.Queue(
            maxsize=QUEUE_SIZE
        )

        self.capture_thread = None
        self.processing_thread = None

        self.whisper_model = None

        self.translation_model = None
        self.translation_tokenizer = None

        self.loaded_language = None

        self.loopback = None

        self.tray_icon = None

        # ----------------------------------------------------
        # LANGUAGE
        # ----------------------------------------------------

        self.language_var = tk.StringVar(
            value="🇵🇰  Urdu"
        )

        # ----------------------------------------------------
        # BUILD UI
        # ----------------------------------------------------

        self.configure_styles()

        self.build_header()
        self.build_controls()
        self.build_status()
        self.build_translation_area()
        self.build_footer()

        # ----------------------------------------------------
        # WINDOW CLOSE
        # ----------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.hide_to_tray
        )

        # ----------------------------------------------------
        # GLOBAL HOTKEY
        # ----------------------------------------------------

        self.start_hotkey()

        # ----------------------------------------------------
        # SYSTEM TRAY
        # ----------------------------------------------------

        self.start_tray()


    # ========================================================
    # STYLES
    # ========================================================

    def configure_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Language.TCombobox",
            fieldbackground=CARD_2,
            background=CARD_2,
            foreground=TEXT,
            arrowcolor=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER
        )

        style.map(
            "Language.TCombobox",

            fieldbackground=[
                ("readonly", CARD_2)
            ],

            foreground=[
                ("readonly", TEXT)
            ],

            selectbackground=[
                ("readonly", CARD_2)
            ],

            selectforeground=[
                ("readonly", TEXT)
            ]
        )


    # ========================================================
    # HEADER
    # ========================================================

    def build_header(self):

        self.header_frame = tk.Frame(
            self.root,
            bg=BG
        )

        self.header_frame.pack(
            fill="x",
            padx=30,
            pady=(24, 10)
        )

        title = tk.Label(
            self.header_frame,
            text="Live Audio Translator",
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        )

        title.pack(
            anchor="w"
        )

        subtitle = tk.Label(
            self.header_frame,
            text="Translate Windows system audio in real time",
            bg=BG,
            fg=SUBTEXT,
            font=(
                "Segoe UI",
                10
            )
        )

        subtitle.pack(
            anchor="w",
            pady=(4, 0)
        )


    # ========================================================
    # CONTROLS
    # ========================================================

    def build_controls(self):

        self.controls_card = tk.Frame(
            self.root,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        self.controls_card.pack(
            fill="x",
            padx=30,
            pady=10
        )

        inner = tk.Frame(
            self.controls_card,
            bg=CARD
        )

        inner.pack(
            fill="x",
            padx=20,
            pady=18
        )

        language_label = tk.Label(
            inner,
            text="Translate to",
            bg=CARD,
            fg=SUBTEXT,
            font=(
                "Segoe UI",
                9
            )
        )

        language_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.language_box = ttk.Combobox(
            inner,
            textvariable=self.language_var,
            state="readonly",
            values=[
                "🇵🇰  Urdu",
                "🇨🇳  Chinese"
            ],
            width=20,
            style="Language.TCombobox"
        )

        self.language_box.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(5, 0)
        )

        self.language_box.bind(
            "<<ComboboxSelected>>",
            self.language_changed
        )

        self.start_button = tk.Button(
            inner,
            text="Start Translation",
            command=self.toggle_translation,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            padx=20,
            pady=10,
            cursor="hand2"
        )

        self.start_button.grid(
            row=1,
            column=1,
            padx=(20, 0),
            pady=(5, 0)
        )

        self.compact_button = tk.Button(
            inner,
            text="Compact",
            command=self.toggle_compact,
            bg=CARD_2,
            fg=TEXT,
            activebackground=BORDER,
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            font=(
                "Segoe UI",
                9
            ),
            padx=14,
            pady=10,
            cursor="hand2"
        )

        self.compact_button.grid(
            row=1,
            column=2,
            padx=(10, 0),
            pady=(5, 0)
        )

        self.top_var = tk.BooleanVar(
            value=False
        )

        self.top_check = tk.Checkbutton(
            inner,
            text="Always on top",
            variable=self.top_var,
            command=self.toggle_always_on_top,
            bg=CARD,
            fg=SUBTEXT,
            selectcolor=CARD_2,
            activebackground=CARD,
            activeforeground=TEXT,
            font=(
                "Segoe UI",
                9
            )
        )

        self.top_check.grid(
            row=1,
            column=3,
            padx=(15, 0),
            pady=(5, 0)
        )

        inner.grid_columnconfigure(
            0,
            weight=1
        )


    # ========================================================
    # STATUS
    # ========================================================

    def build_status(self):

        self.status_frame = tk.Frame(
            self.root,
            bg=BG
        )

        self.status_frame.pack(
            fill="x",
            padx=30,
            pady=(5, 8)
        )

        self.status_dot = tk.Label(
            self.status_frame,
            text="●",
            bg=BG,
            fg=RED,
            font=(
                "Segoe UI",
                13
            )
        )

        self.status_dot.pack(
            side="left"
        )

        self.status_title = tk.Label(
            self.status_frame,
            text="STOPPED",
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        )

        self.status_title.pack(
            side="left",
            padx=(6, 0)
        )

        self.status_message = tk.Label(
            self.status_frame,
            text="Translation is not running",
            bg=BG,
            fg=SUBTEXT,
            font=(
                "Segoe UI",
                9
            )
        )

        self.status_message.pack(
            side="left",
            padx=(10, 0)
        )


    # ========================================================
    # TRANSLATION
    # ========================================================

    def build_translation_area(self):

        self.translation_card = tk.Frame(
            self.root,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        self.translation_card.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        label = tk.Label(
            self.translation_card,
            text="Live Translation",
            bg=CARD,
            fg=SUBTEXT,
            font=(
                "Segoe UI",
                9
            )
        )

        label.pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        self.translation_text = tk.Text(
            self.translation_card,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            wrap="word",
            font=(
                "Segoe UI",
                18
            ),
            padx=15,
            pady=15
        )

        self.translation_text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 15)
        )

        self.translation_text.insert(
            "1.0",
            "Translation will appear here..."
        )

        self.translation_text.configure(
            state="disabled"
        )

        self.translation_text.tag_configure(
            "rtl",
            justify="right",
            font=(
                "Noto Naskh Arabic",
                20
            )
        )

        self.translation_text.tag_configure(
            "ltr",
            justify="left",
            font=(
                "Segoe UI",
                18
            )
        )


    # ========================================================
    # FOOTER
    # ========================================================

    def build_footer(self):

        self.footer = tk.Frame(
            self.root,
            bg=BG
        )

        self.footer.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        developer = tk.Label(
            self.footer,
            text="Dev: Shabbi 😊",
            bg=BG,
            fg=SUBTEXT,
            font=(
                "Segoe UI",
                9
            )
        )

        developer.pack(
            side="left"
        )

        hotkey = tk.Label(
            self.footer,
            text="Ctrl + Alt + Space",
            bg=BG,
            fg=SUBTEXT,
            font=(
                "Segoe UI",
                9
            )
        )

        hotkey.pack(
            side="right"
        )


    # ========================================================
    # STATUS UPDATE
    # ========================================================

    def set_status(
        self,
        title,
        color,
        message
    ):

        self.root.after(
            0,
            lambda: self._set_status_ui(
                title,
                color,
                message
            )
        )


    def _set_status_ui(
        self,
        title,
        color,
        message
    ):

        self.status_dot.config(
            fg=color
        )

        self.status_title.config(
            text=title
        )

        self.status_message.config(
            text=message
        )


    # ========================================================
    # TRANSLATION DISPLAY
    # ========================================================

    def set_translation_text(
        self,
        text,
        rtl=False
    ):

        self.root.after(
            0,
            lambda: self._set_translation_ui(
                text,
                rtl
            )
        )


    def _set_translation_ui(
        self,
        text,
        rtl
    ):

        self.translation_text.configure(
            state="normal"
        )

        self.translation_text.delete(
            "1.0",
            "end"
        )

        self.translation_text.tag_remove(
            "rtl",
            "1.0",
            "end"
        )

        self.translation_text.tag_remove(
            "ltr",
            "1.0",
            "end"
        )

        self.translation_text.insert(
            "1.0",
            text
        )

        if rtl:

            self.translation_text.tag_add(
                "rtl",
                "1.0",
                "end"
            )

        else:

            self.translation_text.tag_add(
                "ltr",
                "1.0",
                "end"
            )

        self.translation_text.configure(
            state="disabled"
        )


    # ========================================================
    # MODEL LOADING
    # ========================================================

    def ensure_models_loaded(
        self,
        language
    ):

        if self.whisper_model is None:

            self.set_status(
                "STARTING",
                ORANGE,
                "Loading Whisper model"
            )

            self.whisper_model = WhisperModel(
                WHISPER_MODEL,
                device="cpu",
                compute_type="int8"
            )

        if self.loaded_language == language:

            return

        self.set_status(
            "STARTING",
            ORANGE,
            f"Loading {language} translator"
        )

        if language == "Urdu":

            model_name = URDU_MODEL

        else:

            model_name = CHINESE_MODEL

        self.translation_tokenizer = (
            MarianTokenizer.from_pretrained(
                model_name,
                local_files_only=True
            )
        )

        self.translation_model = (
            MarianMTModel.from_pretrained(
                model_name,
                local_files_only=True
            )
        )

        self.translation_model.eval()

        self.loaded_language = language


    # ========================================================
    # START / STOP
    # ========================================================

    def toggle_translation(self):

        if self.running:

            self.stop_translation()

        else:

            self.start_translation()


    def start_translation(self):

        if self.running or self.loading:

            return

        self.loading = True

        self.start_button.config(
            text="Starting...",
            state="disabled"
        )

        self.set_status(
            "STARTING",
            ORANGE,
            "Preparing translator"
        )

        thread = threading.Thread(
            target=self._start_translation_worker,
            daemon=True
        )

        thread.start()


    def _start_translation_worker(self):

        try:

            language = self.get_selected_language()

            self.ensure_models_loaded(
                language
            )

            speaker = sc.default_speaker()

            self.loopback = sc.get_microphone(
                id=str(speaker.id),
                include_loopback=True
            )

            while not self.audio_queue.empty():

                try:
                    self.audio_queue.get_nowait()

                except queue.Empty:
                    break

            self.stop_event.clear()

            self.running = True
            self.loading = False

            self.root.after(
                0,
                self.on_started
            )

            self.capture_thread = threading.Thread(
                target=self.capture_audio,
                daemon=True
            )

            self.processing_thread = threading.Thread(
                target=self.process_audio,
                daemon=True
            )

            self.capture_thread.start()
            self.processing_thread.start()

        except Exception as error:

            self.running = False
            self.loading = False

            self.set_status(
                "ERROR",
                RED,
                str(error)
            )

            self.root.after(
                0,
                lambda: self.start_button.config(
                    text="Start Translation",
                    state="normal"
                )
            )


    def on_started(self):

        self.start_button.config(
            text="Stop Translation",
            bg=RED,
            activebackground=RED,
            state="normal"
        )

        self.set_status(
            "LISTENING",
            GREEN,
            "Listening to Windows system audio"
        )


    def stop_translation(self):

        if not self.running and not self.loading:

            return

        self.stop_event.set()

        self.running = False
        self.loading = False

        self.start_button.config(
            text="Start Translation",
            bg=ACCENT,
            activebackground=ACCENT_HOVER,
            state="normal"
        )

        self.set_status(
            "STOPPED",
            RED,
            "Translation is not running"
        )


    # ========================================================
    # AUDIO CAPTURE
    # ========================================================

    def capture_audio(self):

        frames_per_chunk = (
            SAMPLE_RATE * WINDOW_SECONDS
        )

        try:

            with self.loopback.recorder(
                samplerate=SAMPLE_RATE,
                channels=1
            ) as recorder:

                while not self.stop_event.is_set():

                    audio = recorder.record(
                        numframes=frames_per_chunk
                    )

                    audio = np.asarray(
                        audio,
                        dtype=np.float32
                    )

                    audio = audio.reshape(-1)

                    if self.audio_queue.full():

                        try:
                            self.audio_queue.get_nowait()

                        except queue.Empty:
                            pass

                    try:

                        self.audio_queue.put_nowait(
                            audio
                        )

                    except queue.Full:
                        pass

        except Exception as error:

            if not self.stop_event.is_set():

                self.set_status(
                    "ERROR",
                    RED,
                    f"Audio capture error: {error}"
                )

                self.stop_event.set()

                self.running = False


    # ========================================================
    # PROCESS AUDIO
    # ========================================================

    def process_audio(self):

        while not self.stop_event.is_set():

            try:

                audio = self.audio_queue.get(
                    timeout=0.5
                )

            except queue.Empty:

                continue

            try:

                rms = float(
                    np.sqrt(
                        np.mean(
                            audio ** 2
                        )
                    )
                )

                if rms < AUDIO_THRESHOLD:

                    self.set_status(
                        "LISTENING",
                        GREEN,
                        "Listening to Windows system audio"
                    )

                    continue

                self.set_status(
                    "TRANSLATING",
                    ORANGE,
                    "Recognizing speech"
                )

                segments, info = (
                    self.whisper_model.transcribe(
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
                )

                parts = []

                for segment in segments:

                    text = segment.text.strip()

                    if text:

                        parts.append(
                            text
                        )

                english_text = " ".join(
                    parts
                ).strip()

                if not english_text:

                    self.set_status(
                        "LISTENING",
                        GREEN,
                        "Listening to Windows system audio"
                    )

                    continue

                self.set_status(
                    "TRANSLATING",
                    ORANGE,
                    "Translating speech"
                )

                translated_text = self.translate_text(
                    english_text
                )

                language = self.get_selected_language()

                if language == "Urdu":

                    translated_text = format_urdu(
                        translated_text
                    )

                    self.set_translation_text(
                        translated_text,
                        rtl=True
                    )

                else:

                    self.set_translation_text(
                        translated_text,
                        rtl=False
                    )

                self.set_status(
                    "LISTENING",
                    GREEN,
                    "Listening to Windows system audio"
                )

            except Exception as error:

                self.set_status(
                    "ERROR",
                    RED,
                    f"Processing error: {error}"
                )

                self.stop_event.set()
                self.running = False

                break


    # ========================================================
    # TRANSLATE
    # ========================================================

    def translate_text(
        self,
        text
    ):

        inputs = self.translation_tokenizer(
            [text],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )

        with torch.no_grad():

            translated = (
                self.translation_model.generate(
                    **inputs,
                    num_beams=1,
                    do_sample=False,
                    max_length=192
                )
            )

        result = (
            self.translation_tokenizer.decode(
                translated[0],
                skip_special_tokens=True
            )
        )

        return result.strip()


    # ========================================================
    # LANGUAGE
    # ========================================================

    def get_selected_language(self):

        selected = self.language_var.get()

        if "Chinese" in selected:

            return "Chinese"

        return "Urdu"


    def language_changed(
        self,
        event=None
    ):

        if not self.running:

            return

        self.stop_translation()

        self.root.after(
            500,
            self.start_translation
        )


    # ========================================================
    # COMPACT MODE
    # ========================================================

    def toggle_compact(self):

        self.compact = not self.compact

        if self.compact:

            self.root.geometry(
                "620x430"
            )

            self.header_frame.pack_forget()
            self.footer.pack_forget()

            self.compact_button.config(
                text="Full"
            )

        else:

            self.root.geometry(
                "860x700"
            )

            self.header_frame.pack(
                fill="x",
                padx=30,
                pady=(24, 10),
                before=self.controls_card
            )

            self.footer.pack(
                fill="x",
                padx=30,
                pady=(0, 15)
            )

            self.compact_button.config(
                text="Compact"
            )


    # ========================================================
    # ALWAYS ON TOP
    # ========================================================

    def toggle_always_on_top(self):

        self.root.attributes(
            "-topmost",
            self.top_var.get()
        )


    # ========================================================
    # HOTKEY
    # ========================================================

    def start_hotkey(self):

        try:

            self.hotkey_listener = (
                keyboard.GlobalHotKeys(
                    {
                        GLOBAL_HOTKEY:
                            self.hotkey_pressed
                    }
                )
            )

            self.hotkey_listener.start()

        except Exception as error:

            print(
                f"Hotkey error: {error}"
            )


    def hotkey_pressed(self):

        self.root.after(
            0,
            self.toggle_window_visibility
        )


    def toggle_window_visibility(self):

        if self.root.state() == "withdrawn":

            self.show_window()

        else:

            self.root.withdraw()


    # ========================================================
    # TRAY
    # ========================================================

    def create_tray_image(self):

        image = Image.new(
            "RGB",
            (64, 64),
            BG
        )

        draw = ImageDraw.Draw(
            image
        )

        draw.ellipse(
            (8, 8, 56, 56),
            fill=ACCENT
        )

        draw.rectangle(
            (29, 18, 35, 46),
            fill="white"
        )

        draw.rectangle(
            (20, 29, 44, 35),
            fill="white"
        )

        return image


    def start_tray(self):

        menu = pystray.Menu(

            pystray.MenuItem(
                "Show Translator",
                lambda icon, item:
                    self.root.after(
                        0,
                        self.show_window
                    )
            ),

            pystray.MenuItem(
                "Hide Translator",
                lambda icon, item:
                    self.root.after(
                        0,
                        self.root.withdraw
                    )
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Start Translation",
                lambda icon, item:
                    self.root.after(
                        0,
                        self.start_translation
                    )
            ),

            pystray.MenuItem(
                "Stop Translation",
                lambda icon, item:
                    self.root.after(
                        0,
                        self.stop_translation
                    )
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Exit",
                lambda icon, item:
                    self.root.after(
                        0,
                        self.exit_application
                    )
            )
        )

        self.tray_icon = pystray.Icon(
            "LiveAudioTranslator",
            self.create_tray_image(),
            "Live Audio Translator",
            menu
        )

        tray_thread = threading.Thread(
            target=self.tray_icon.run,
            daemon=True
        )

        tray_thread.start()


    def hide_to_tray(self):

        self.root.withdraw()


    def show_window(self):

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()


    # ========================================================
    # EXIT
    # ========================================================

    def exit_application(self):

        self.stop_event.set()

        self.running = False

        try:

            if hasattr(
                self,
                "hotkey_listener"
            ):

                self.hotkey_listener.stop()

        except Exception:

            pass

        try:

            if self.tray_icon:

                self.tray_icon.stop()

        except Exception:

            pass

        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = LiveAudioTranslatorGUI(
        root
    )

    root.mainloop()