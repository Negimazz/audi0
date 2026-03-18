import sys
import os
import soundcard as sc

try:
    spk = sc.default_speaker()
    print(f"Speaker Channels: {spk.channels}")
    mic = sc.get_microphone(spk.id, include_loopback=True)
    
    print(f"Testing loopback mic: {mic.id}")
except Exception as e:
    print("Failed to get device:", e)
    sys.exit(1)

formats = [
    (48000, 2),
    (44100, 2),
    (48000, 1),
    (44100, 1),
]

for rate, ch in formats:
    print(f"Testing {rate}Hz, {ch}ch...")
    try:
        with mic.recorder(samplerate=rate, channels=ch, blocksize=1024) as rec:
            print(f"SUCCESS: {rate}Hz, {ch}ch")
    except Exception as e:
        print(f"ERROR {rate}/{ch}: {e}")

print("Done testing formats!")
