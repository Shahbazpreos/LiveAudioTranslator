import soundcard as sc
import numpy as np
from scipy.io.wavfile import write


SAMPLE_RATE = 16000
SECONDS = 8


print("\nAvailable speakers:\n")

speakers = sc.all_speakers()

for i, speaker in enumerate(speakers):
    print(f"{i}: {speaker.name}")


default_speaker = sc.default_speaker()

print("\nDefault speaker:")
print(default_speaker.name)


print("\nCreating loopback capture...")

loopback = sc.get_microphone(
    id=str(default_speaker.id),
    include_loopback=True
)

print("Loopback device:")
print(loopback.name)


print(f"\nRecording Windows system audio for {SECONDS} seconds...")
print("Play a YouTube video now.\n")


with loopback.recorder(
    samplerate=SAMPLE_RATE,
    channels=1
) as recorder:

    data = recorder.record(
        numframes=SAMPLE_RATE * SECONDS
    )


print("Recording complete.")

data = np.asarray(data)

peak = np.max(np.abs(data))
rms = np.sqrt(np.mean(data ** 2))

print(f"Peak level: {peak:.6f}")
print(f"RMS level : {rms:.6f}")


audio_int16 = np.clip(
    data * 32767,
    -32768,
    32767
).astype(np.int16)


write(
    "windows_loopback_test.wav",
    SAMPLE_RATE,
    audio_int16
)


print("\nSaved:")
print("windows_loopback_test.wav")