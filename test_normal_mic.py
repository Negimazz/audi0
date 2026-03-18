import sys
import soundcard as sc

print("Testing normal mic...")

try:
    mic = sc.default_microphone()
    
    print(f"Opening recorder: {mic.name}...")
    with mic.recorder(samplerate=44100, channels=1, blocksize=2048) as recorder:
        print("Recorder opened successfully!")
        data = recorder.record(numframes=2048)
        print("Recorded data shape:", data.shape)
except Exception as e:
    print(f"EXCEPTION: {e}")

print("Script finished!")
