import os
import asyncio
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from google import genai
from faster_whisper import WhisperModel
from core.tts import JarvisVoice
from core.tools import JarvisTools

load_dotenv()

class Jarvis:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.5-flash"
        self.user_name = os.getenv('USER_NAME', 'Genisson')

        print("Iniciando audição (Faster-Whisper)...")
        self.stt_model = WhisperModel("small", device="cpu", compute_type="int8")
        self.fs = 16000

        print("Iniciando sintetizador de voz (Kokoro)...")
        self.voice_system = JarvisVoice()

    def listen_and_transcribe(self):
        duration = 5
        print(f"\n[ Jarvis ouvindo por {duration}s... ]")
        audio = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=1, dtype='float32', device=1)
        sd.wait()

        print("[ Processando fala... ]")
        segments, _ = self.stt_model.transcribe(
            audio.flatten(),
            beam_size=5,
            language="pt",
            initial_prompt="Jarvis, NestJS, Laravel, Django, Morea, Blender, VS Code, Genisson, Preparar"
        )
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    async def think(self, text):
        prompt = (
            f"Você é o JARVIS. Responda ao {self.user_name} de forma concisa e refinada.\n"
            "DIRETRIZES DE AÇÃO:\n"
            "- Se pedirem para abrir o VS Code: [ACTION:OPEN_VSCODE]\n"
            "- Se pedirem a hora: [ACTION:GET_TIME]\n"
            "- Se pedirem para abrir um site ou pesquisar: [ACTION:OPEN_URL|link_ou_busca]\n"
            "- Se disserem 'preparar ambiente X' ou 'abrir projeto X': [ACTION:OPEN_PROJECT|X]\n"
            "- Se perguntarem sobre a porta X: [ACTION:CHECK_PORT|X]\n"
            "- Se quiserem documentação de X: [ACTION:SEARCH_DOCS|X]\n"
            "- Se pedirem para abrir banco de dados ou DB: [ACTION:OPEN_DB]\n"
            "- Se pedirem para abrir o Blender: [ACTION:OPEN_BLENDER]\n"
            "- Se disserem 'tire um print' ou 'capturar tela': [ACTION:CAPTURE]\n"
            f"Pergunta do usuário: {text}"
        )
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return response.text
        except Exception as e:
            return f"Senhor, tive uma falha técnica nos núcleos: {e}"

    def execute_action(self, response_text):
        if "[ACTION:GET_TIME]" in response_text:
            return JarvisTools.get_time()

        if "[ACTION:OPEN_VSCODE]" in response_text:
            return JarvisTools.open_vscode()

        if "[ACTION:OPEN_DB]" in response_text:
            return JarvisTools.open_db_tool()

        if "[ACTION:OPEN_BLENDER]" in response_text:
            return JarvisTools.open_blender()

        if "[ACTION:CAPTURE]" in response_text:
            return JarvisTools.capture_screen()

        if "[ACTION:OPEN_PROJECT|" in response_text:
            proj = response_text.split("|")[1].split("]")[0]
            return JarvisTools.open_project(proj)

        if "[ACTION:CHECK_PORT|" in response_text:
            port = response_text.split("|")[1].split("]")[0]
            return JarvisTools.check_port(port)

        if "[ACTION:SEARCH_DOCS|" in response_text:
            tech = response_text.split("|")[1].split("]")[0]
            return JarvisTools.search_docs(tech)

        if "[ACTION:OPEN_URL|" in response_text:
            link = response_text.split("|")[1].split("]")[0]
            return JarvisTools.open_browser(link)

        return None

async def main():
    jarvis = Jarvis()
    print(f"\n--- JARVIS TOTALMENTE OPERACIONAL ---")
    jarvis.voice_system.speak(f"Sistemas carregados. Às suas ordens, {os.getenv('USER_NAME', 'Senhor')}.")

    while True:
        input("\nPressione ENTER para falar com o Jarvis...")

        user_text = jarvis.listen_and_transcribe()
        if not user_text:
            continue

        print(f"Você disse: {user_text}")

        if any(word in user_text.lower() for word in ["sair", "desligar", "tchau"]):
            jarvis.voice_system.speak("Desativando sistemas. Até logo, Senhor.")
            break

        print("Jarvis pensando...")
        response = await jarvis.think(user_text)

        action_result = jarvis.execute_action(response)
        clean_response = response.split("[ACTION")[0].strip()

        final_speech = clean_response
        if action_result:
            if any(x in action_result for x in ["Agora são", "está ocupada", "está livre"]):
                final_speech = f"{clean_response} {action_result}"
            else:
                print(f"Sistema: {action_result}")

        print(f"Jarvis: {final_speech}")
        jarvis.voice_system.speak(final_speech)

if __name__ == "__main__":
    asyncio.run(main())