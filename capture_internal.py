import sys
import traceback
import soundcard as sc

f = open('debug_pure.txt', 'w', encoding='utf-8')
sys.stdout = f
sys.stderr = f

print("Testing mic.recorder...")

try:
    print("Getting default speaker...")
    default_speaker = sc.default_speaker()
    print("Getting loopback mic...")
    mic = sc.get_microphone(default_speaker.id, include_loopback=True)
    
    print("Opening recorder...")
    with mic.recorder(samplerate=44100, channels=1, blocksize=2048) as recorder:
        print("Recorder opened successfully!")
        data = recorder.record(numframes=2048)
        print("Recorded data!")
except Exception as e:
    print("CAUGHT EXCEPTION:")
    traceback.print_exc()

print("Script finished!")
f.close()
