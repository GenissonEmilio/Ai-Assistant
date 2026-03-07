import os
import asyncio
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from google import genai
from faster_whisper import WhisperModel
from core.tts import JarvisVoice
from core.tools import JarvisTools
from core.memory import JarvisMemory

load_dotenv()


class Jarvis:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.5-flash"
        self.user_name = os.getenv('USER_NAME', 'Genisson')

        print("Iniciando memória (SQLite)...")
        self.memory = JarvisMemory()

        print("Iniciando audição (Faster-Whisper small)...")
        self.stt_model = WhisperModel("small", device="cpu", compute_type="int8")
        self.fs = 16000

        print("Iniciando sintetizador de voz (Kokoro)...")
        self.voice_system = JarvisVoice()

    def listen_and_transcribe(self):
        duration = 10
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
        # Busca contexto e fatos na memória
        history = self.memory.get_recent_context(limit=5)
        relevant_facts = self.memory.get_relevant_facts(text)

        prompt = (
            f"Você é o JARVIS. Responda ao {self.user_name} de forma concisa e refinada.\n"
            f"HISTÓRICO RECENTE:\n{history}\n"
            f"FATOS RELEVANTES: {relevant_facts}\n"
            "DIRETRIZES DE AÇÃO:\n"
            "- VS Code: [ACTION:OPEN_VSCODE]\n"
            "- Hora: [ACTION:GET_TIME]\n"
            "- Site/Pesquisa: [ACTION:OPEN_URL|link]\n"
            "- Projeto: [ACTION:OPEN_PROJECT|X]\n"
            "- Porta: [ACTION:CHECK_PORT|X]\n"
            "- Docs: [ACTION:SEARCH_DOCS|X]\n"
            "- Banco de Dados: [ACTION:OPEN_DB]\n"
            "- Blender: [ACTION:OPEN_BLENDER]\n"
            "- Print: [ACTION:CAPTURE]\n"
            "- Lembrar/Salvar informação: [ACTION:SAVE_MEMORY|fato]\n"
            f"Pergunta do usuário: {text}"
        )
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                return "Senhor, os núcleos de processamento atingiram a cota limite. Por favor, aguarde alguns segundos."
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

        if "[ACTION:SAVE_MEMORY|" in response_text:
            fact = response_text.split("|")[1].split("]")[0]
            return self.memory.save_fact(fact)

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

    initial_msg = f"Sistemas carregados. Às suas ordens, {os.getenv('USER_NAME', 'Senhor')}."
    jarvis.voice_system.speak(initial_msg)
    jarvis.memory.add_to_history("Jarvis", initial_msg)

    while True:
        input("\nPressione ENTER para falar com o Jarvis...")

        user_text = jarvis.listen_and_transcribe()
        if not user_text:
            continue

        print(f"Você disse: {user_text}")
        jarvis.memory.add_to_history("User", user_text)

        print("Jarvis pensando...")
        response = await jarvis.think(user_text)

        action_result = jarvis.execute_action(response)
        clean_response = response.split("[ACTION")[0].strip()

        final_speech = clean_response
        if action_result:
            if any(x in action_result for x in ["Agora são", "está ocupada", "está livre", "Fato memorizado"]):
                final_speech = f"{clean_response} {action_result}"
            else:
                print(f"Sistema: {action_result}")

        print(f"Jarvis: {final_speech}")
        jarvis.voice_system.speak(final_speech)
        jarvis.memory.add_to_history("Jarvis", final_speech)


if __name__ == "__main__":
    asyncio.run(main())