import struct
import wave
import io
import math

def generate_beep_wav(duration=1.0, frequency=880, volume=0.8, sample_rate=44100):
    num_samples = int(sample_rate * duration)
    max_amp = int(volume * 32767)

    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        value = int(max_amp * math.sin(2 * math.pi * frequency * t))
        packed = struct.pack('<h', value)
        samples.append(packed)

    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(samples))

    buffer.seek(0)
    return buffer.getvalue()

def generate_sos_pattern():
    short = 0.2
    long = 0.6
    gap = 0.1
    pause = 0.4
    pattern = [short, short, short, long, long, long, short, short, short]
    segments = []
    for i, dur in enumerate(pattern):
        segments.append(generate_beep_wav(dur, 880, 0.8))
        segments.append(generate_beep_wav(gap, 0, 0))
    segments.append(generate_beep_wav(pause, 0, 0))
    result = b''.join(segments)
    return result
