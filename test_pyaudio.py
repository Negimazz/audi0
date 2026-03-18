import traceback
try:
    import pyaudiowpatch as pyaudio
    import numpy as np

    print("Init PyAudio")
    p = pyaudio.PyAudio()

    try:
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
    except OSError:
        print("WASAPI API not found")
        p.terminate()
        exit(1)

    default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
    print(f"Default speaker: {default_speakers['name']}")
    
    if not default_speakers["isLoopbackDevice"]:
        for loopback in p.get_loopback_device_info_generator():
            if default_speakers["name"] in loopback["name"]:
                default_speakers = loopback
                break
                
    print(f"Loopback device mapping: {default_speakers['name']}")

    def callback(in_data, frame_count, time_info, status):
        data = np.frombuffer(in_data, dtype=np.float32)
        print("Data max:", np.max(data) if len(data) > 0 else "empty")
        return (in_data, pyaudio.paContinue)

    print("Opening stream...")
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=default_speakers["maxInputChannels"],
        rate=int(default_speakers["defaultSampleRate"]),
        frames_per_buffer=2048,
        input=True,
        input_device_index=default_speakers["index"],
        stream_callback=callback
    )

    print("Starting stream...")
    import time
    time.sleep(1)
    print("Stopping stream...")
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Success test pyaudiowpatch")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
