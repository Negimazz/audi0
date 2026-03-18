import sys
import soundcard as sc

print("Testing stereo mic.recorder...")

try:
    default_speaker = sc.default_speaker()
    mic = sc.get_microphone(default_speaker.id, include_loopback=True)
    
    print("Opening recorder with channels=2...")
    with mic.recorder(samplerate=44100, channels=2, blocksize=2048) as recorder:
        print("Recorder opened successfully!")
        data = recorder.record(numframes=2048)
        print("Recorded data shape:", data.shape)
except Exception as e:
    print(f"EXCEPTION: {e}")

print("Script finished!")
