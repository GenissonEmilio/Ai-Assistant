import os
import asyncio
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from google import genai
from faster_whisper import WhisperModel
import collections

load_dotenv()


class Jarvis:
    def __init__(self):
        # Cérebro
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.5-flash"
        self.user_name = os.getenv('USER_NAME', 'Genisson')

        # Ouvido
        print("Iniciando audição (Faster-Whisper)...")
        self.stt_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.fs = 16000
        self.chunk_duration = 0.5

    def listen_and_transcribe(self):
        duration = 5
        print(f"\n[ Jarvis ouvindo por {duration}s... ]")

        # Gravação direta do ID 1
        audio = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=1, dtype='float32', device=1)
        sd.wait()

        print("[ Processando fala... ]")
        segments, _ = self.stt_model.transcribe(audio.flatten(), beam_size=5, language="pt")
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    async def think(self, text):
        prompt = f"CONTEXTO: Você é o JARVIS. Responda ao {self.user_name} de forma concisa.\nPERGUNTA: {text}"
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return response.text
        except Exception as e:
            return f"Erro nos núcleos: {e}"


async def main():
    jarvis = Jarvis()
    print(f"--- JARVIS ONLINE ---")

    while True:
        input("\nPressione ENTER para falar com o Jarvis...")

        # Ouvir
        user_text = jarvis.listen_and_transcribe()

        if not user_text:
            print("Jarvis: Não consegui ouvir nada, Senhor.")
            continue

        print(f"Você disse: {user_text}")

        if "sair" in user_text.lower() or "desligar" in user_text.lower():
            print("Jarvis: Desativando sistemas. Até logo!")
            break

        # Pensar
        print("Jarvis processando...")
        response = await jarvis.think(user_text)
        print(f"Jarvis: {response}")


if __name__ == "__main__":
    asyncio.run(main())