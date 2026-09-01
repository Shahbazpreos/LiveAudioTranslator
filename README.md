\# 🎧 Live Audio Translator



\*\*Real-time system audio transcription and translation for Windows 11\*\*



Live Audio Translator is a lightweight desktop application designed to capture audio playing on a Windows computer, transcribe the speech in real time, and translate it into a selected language.



Whether the audio comes from \*\*YouTube, a web browser, a media player, a meeting application, or another desktop program\*\*, Live Audio Translator is designed to listen directly to the system audio stream rather than requiring a microphone.



> \*\*Developer:\*\* Shabbi :)



\---



\## 🚀 Project Overview



The goal of Live Audio Translator is simple:



\*\*System Audio → Speech Recognition → Translation → Live On-Screen Text\*\*



Instead of manually uploading recordings or copying subtitles into a translator, the application aims to provide live translated text while audio is playing on the computer.



The project currently focuses on \*\*Windows 11\*\* and uses Windows audio loopback capture to access system playback audio.



\---



\## ✨ Features



\* 🎧 Captures Windows system audio

\* 🎙️ No microphone required for system-audio translation

\* 📝 Live speech-to-text transcription

\* 🌐 Real-time translation

\* 📴 Offline speech-recognition support

\* 🖥️ Simple desktop graphical interface

\* 🔄 Start/Stop translation controls

\* 📊 Live application status indicator

\* 📜 Separate source and translated text areas

\* 🎯 Designed for Windows 11

\* 📦 Standalone Windows build support

\* 🛠️ Windows installer support



\---



\## 🧠 How It Works



Live Audio Translator follows a simple processing pipeline:



```text

Windows System Audio

&#x20;       │

&#x20;       ▼

Audio Loopback Capture

&#x20;       │

&#x20;       ▼

Speech Recognition

&#x20;       │

&#x20;       ▼

Source-Language Text

&#x20;       │

&#x20;       ▼

Translation Engine

&#x20;       │

&#x20;       ▼

Translated Text

&#x20;       │

&#x20;       ▼

Desktop GUI

```



For example:



```text

YouTube / Browser / Application

&#x20;             ↓

&#x20;       System Audio

&#x20;             ↓

&#x20;     Live Audio Translator

&#x20;             ↓

&#x20;    Speech Recognition

&#x20;             ↓

&#x20;         Translation

&#x20;             ↓

&#x20;     Live Translated Text

```



\---



\## 🖥️ Application Interface



The desktop interface provides:



\* Translation language selection

\* Start/Stop controls

\* Application status

\* Source transcription

\* Translated output

\* Real-time processing information



The interface is designed to remain simple so the application can run alongside videos, meetings, streams, and other applications.



\---



\## 🛠️ Technologies Used



The project is built primarily with:



\* \*\*Python\*\*

\* \*\*Tkinter\*\* — desktop graphical interface

\* \*\*Windows WASAPI / Loopback Audio\*\* — system audio capture

\* \*\*Whisper-based speech recognition\*\*

\* \*\*FFmpeg / audio-processing components\*\*

\* \*\*PyInstaller\*\* — Windows executable packaging

\* \*\*Inno Setup\*\* — Windows installer creation



Additional Python libraries are used for audio processing, translation, threading, and application management.



\---



\## 📁 Project Structure



```text

LiveAudioTranslator-Windows/

│

├── gui.py

│   Main graphical user interface

│

├── live\_translate\_windows.py

│   Core live transcription and translation logic

│

├── test\_wasapi.py

│   Windows audio-loopback testing

│

├── test\_whisper\_live.py

│   Live speech-recognition testing

│

├── LiveAudioTranslator.spec

│   PyInstaller build configuration

│

├── LiveAudioTranslator-Debug.spec

│   Debug build configuration

│

├── installer.iss

│   Inno Setup installer configuration

│

├── LiveAudioTranslator.ico

│   Application icon

│

└── README.md

```



Generated files, virtual environments, downloaded AI models, test recordings, build directories, and installer output are intentionally excluded from the Git repository.



\---



\## ⚙️ Requirements



\### Operating System



\* Windows 11 recommended

\* Windows audio output device capable of loopback capture



\### Development Environment



\* Python 3.x

\* Required Python dependencies

\* FFmpeg where required by the configured audio pipeline



A virtual environment is recommended when running the project from source.



\---



\## 🔧 Running From Source



Clone the repository:



```bash

git clone <repository-url>

```



Enter the project directory:



```bash

cd LiveAudioTranslator-Windows

```



Create a virtual environment:



```bash

python -m venv .venv

```



Activate it on Windows:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



Install the required dependencies once a `requirements.txt` file has been generated:



```bash

pip install -r requirements.txt

```



Run the application:



```bash

python gui.py

```



\---



\## 📦 Building the Windows Application



The project includes PyInstaller configuration files for producing a standalone Windows build.



Example:



```bash

pyinstaller LiveAudioTranslator.spec

```



The generated application will normally be placed inside:



```text

dist/

```



\---



\## 💿 Building the Installer



An Inno Setup configuration is included:



```text

installer.iss

```



Compile this script using \*\*Inno Setup 6\*\* after creating the PyInstaller build.



The resulting installer is generated separately from the Git repository because compiled builds and bundled AI models can be very large.



\---



\## 🧩 Why Large Files Aren't Stored in the Repository



AI models and compiled application builds can consume gigabytes of storage.



For that reason, the following are excluded from Git:



```text

.venv/

models/

build/

dist/

installer\_output/

\*.wav

```



This keeps the repository focused on the project's source code and makes it easier for developers to clone and contribute.



Future compiled releases can be distributed separately through the repository's \*\*Releases\*\* section where appropriate.



\---



\## 🗺️ Roadmap



Possible future improvements include:



\* \[ ] Additional translation languages

\* \[ ] Improved translation latency

\* \[ ] Automatic source-language detection

\* \[ ] Subtitle-style overlay mode

\* \[ ] Customizable fonts and interface settings

\* \[ ] Translation history

\* \[ ] Export translated transcripts

\* \[ ] Better CPU and memory optimization

\* \[ ] Additional Windows audio-device support

\* \[ ] Automatic model management

\* \[ ] Simplified installer downloads

\* \[ ] Hotkey support

\* \[ ] Improved error handling



\---



\## 🧪 Project Status



\*\*Current Status:\*\* Early Development / Experimental



The core Windows application has been successfully developed and packaged, but the project is still evolving.



Bugs, performance issues, and translation inaccuracies may occur.



Testing and improvements are ongoing.



\---



\## 🤝 Contributing



Contributions, suggestions, bug reports, and improvements are welcome.



If you would like to contribute:



1\. Fork the repository.

2\. Create a new branch.

3\. Make your changes.

4\. Test your changes.

5\. Submit a pull request.



For bugs or feature suggestions, please open an issue with as much relevant information as possible.



\---



\## ⚠️ Disclaimer



Live Audio Translator is an experimental project.



Speech-recognition and machine-translation systems can produce incorrect or incomplete results. Translations should not be relied upon for medical, legal, emergency, financial, or other critical decisions without independent verification.



Users are responsible for ensuring that their use of captured or translated audio complies with applicable laws, platform policies, privacy requirements, and content rights.



\---



\## 👨‍💻 Developer



\*\*Shabbi :)\*\*



Built while learning, experimenting, breaking things, fixing them again, and discovering how software actually makes its way from:



```text

"Maybe I should build this..."

&#x20;             ↓

"Why isn't this working?"

&#x20;             ↓

"It works!"

&#x20;             ↓

"Why did it stop working?"

&#x20;             ↓

"It works again!"

&#x20;             ↓

&#x20;         GitHub 🚀

```



\### 🏆 Achievement Unlocked



```text

╔══════════════════════════════════════╗

║        🏆 ACHIEVEMENT UNLOCKED      ║

║                                      ║

║          FIRST REPOSITORY            ║

║                                      ║

║   Survived dependency errors         ║

║   Survived audio debugging           ║

║   Survived packaging                 ║

║   Survived a 2+ GB installer         ║

║                                      ║

║        Welcome to Developer Land.    ║

║              🚀 💻 🎧               ║

╚══════════════════════════════════════╝

```



Every developer has a first repository.



\*\*This is mine.\*\*



\---



\## ⭐ Support the Project



If you find Live Audio Translator useful or interesting, consider giving the repository a ⭐.



It helps the project grow and lets me know that someone other than me managed to make it work. 😄



\---



\*\*Live Audio Translator\*\*



\*Hear it. Understand it.\*



