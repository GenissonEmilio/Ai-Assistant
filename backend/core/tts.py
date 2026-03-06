import os
import sounddevice as sd
from kokoro_onnx import Kokoro


class JarvisVoice:
    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_path)

        model_path = os.path.join(project_root, "kokoro-v0_19.onnx")
        voices_path = os.path.join(project_root, "voices.bin")

        if not os.path.exists(voices_path):
            raise FileNotFoundError(f"Erro: O arquivo {voices_path} não foi encontrado!")

        print(f"Carregando sistema vocal com: {voices_path}")
        self.kokoro = Kokoro(model_path, voices_path)
        self.voice = "bm_lewis"

    def speak(self, text):
        if not text: return

        clean_text = text.replace("*", "").replace("#", "").strip()
        print(f"Jarvis: {clean_text}")

        try:
            samples, sample_rate = self.kokoro.create(
                clean_text,
                voice=self.voice,
                speed=1.2,
                lang="en-us"
            )
            sd.play(samples, sample_rate)
            sd.wait()
        except Exception as e:
            print(f"Erro na fala: {e}")