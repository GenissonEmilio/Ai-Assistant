import os
import asyncio
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from google import genai
from faster_whisper import WhisperModel
from core.tts import JarvisVoice

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

        # Voz
        print("Iniciando sintetizador de voz (Kokoro)...")
        self.voice_system = JarvisVoice()

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
        prompt = (
            f"CONTEXTO: Você é o JARVIS, um assistente de IA sofisticado. "
            f"Responda ao {self.user_name} de forma concisa, educada e refinada. "
            f"Evite usar markdown (como asteriscos ou hashtags) na resposta para não confundir a leitura de voz.\n"
            f"PERGUNTA: {text}"
        )
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return response.text
        except Exception as e:
            return f"Senhor, tive uma falha técnica nos núcleos: {e}"


async def main():
    # Inicializa o Jarvis
    jarvis = Jarvis()
    print(f"\n--- JARVIS TOTALMENTE OPERACIONAL ---")

    # Saudação inicial
    jarvis.voice_system.speak(f"Sistemas carregados. Às suas ordens, {os.getenv('USER_NAME', 'Senhor')}.")

    while True:
        input("\nPressione ENTER para falar com o Jarvis...")

        # Escuta
        user_text = jarvis.listen_and_transcribe()

        if not user_text:
            print("Jarvis: Não consegui captar sua voz, Senhor.")
            continue

        print(f"Você disse: {user_text}")

        if "sair" in user_text.lower() or "desligar" in user_text.lower():
            jarvis.voice_system.speak("Desativando sistemas. Até logo, Senhor.")
            break

        # Processamento (Cérebro)
        print("Jarvis pensando...")
        response = await jarvis.think(user_text)
        print(f"Jarvis: {response}")

        # Resposta Vocal
        jarvis.voice_system.speak(response)


if __name__ == "__main__":
    asyncio.run(main())