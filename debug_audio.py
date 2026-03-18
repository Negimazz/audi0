import soundcard as sc
import traceback

print("Getting default speaker...")
default_speaker = sc.default_speaker()
print("Speaker:", default_speaker.name)

mic = sc.get_microphone(default_speaker.id, include_loopback=True)
print("Microphone:", mic.name)

print("Starting recorder...")
try:
    with mic.recorder(samplerate=44100, channels=1, blocksize=2048) as recorder:
        print("Recorder started!")
        data = recorder.record(numframes=2048)
        print("Data recorded:", data.shape)
except Exception as e:
    print("Error:")
    traceback.print_exc()
