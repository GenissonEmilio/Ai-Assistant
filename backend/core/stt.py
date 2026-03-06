import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import io
import wave


class JarvisEar:
    def __init__(self, model_size="base"):
        print(f"Carregando sistema de audição ({model_size})...")
        self.model = WhisperModel(model_size, device="cuda", compute_type="int8")
        self.fs = 16000

    def listen(self, duration=5):
        print("Ouvindo...")
        audio_data = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')
        sd.wait()

        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.fs)
            wf.writeframes(audio_data.tobytes())

        audio_buffer.seek(0)

        segments, info = self.model.transcribe(audio_buffer, beam_size=5)
        text = "".join([segment.text for segment in segments])
        return text.strip()