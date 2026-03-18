import sys
import os
import soundcard as sc
import traceback

print("Testing mic.recorder...")

try:
    print("Getting default speaker...")
    default_speaker = sc.default_speaker()
    print("Getting loopback mic...")
    mic = sc.get_microphone(default_speaker.id, include_loopback=True)
    
    print(f"Opening recorder with channels=1...")
    with mic.recorder(samplerate=44100, channels=1, blocksize=2048) as recorder:
        print("Recorder opened successfully!")
        data = recorder.record(numframes=2048)
        print("Recorded data!")
except Exception as e:
    print("CAUGHT EXCEPTION:")
    traceback.print_exc()

print("Script finished!")
