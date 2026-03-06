import os
from kokoro_onnx import Kokoro
import sounddevice as sd

class JarvisVoice:
    def __init__(self):
        print("Iniciando sistema vocal (Kokoro)...")
        self.kokoro = Kokoro("kokoro-v0_19.onnx", "voices.json")
        self.voice = "am_adam"

    def speak(self, text):
        print(f"Jarvis falando: {text}")
        samples, sample_rate = self.kokoro.create(text, voice=self.voice, speed=1.0, lang="en-us")
        sd.play(samples, sample_rate)
        sd.wait()