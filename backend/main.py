import os
import asyncio
import numpy as np
import sounddevice as sd
import keyboard
import socketio
import re
from aiohttp import web
from dotenv import load_dotenv
from google import genai
from faster_whisper import WhisperModel
from core.tts import JarvisVoice
from core.tools import JarvisTools
from core.memory import JarvisMemory

load_dotenv()

# Configuração do Servidor de Comunicação
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)


class Jarvis:
    def __init__(self, loop):
        self.loop = loop
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.5-flash"
        self.user_name = os.getenv('USER_NAME', 'Genilsson')
        self.memory = JarvisMemory()

        print("Iniciando audição (Faster-Whisper small)...")
        self.stt_model = WhisperModel("small", device="cpu", compute_type="int8")
        self.fs = 16000

        print("Iniciando sintetizador de voz (Kokoro)...")
        self.voice_system = JarvisVoice()
        self.is_busy = False

    async def emit_state(self, state, data=None):
        await sio.emit('jarvis_state', {'state': state, 'data': data})

    def listen_and_transcribe(self):
        duration = 7
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
        return " ".join([segment.text for segment in segments]).strip()

    async def think(self, text):
        history = self.memory.get_recent_context(limit=5)
        relevant_facts = self.memory.get_relevant_facts(text)

        system_instruction = (
            f"Você é o JARVIS, um assistente técnico avançado. Responda ao {self.user_name}.\n"
            "REGRAS CRÍTICAS:\n"
            "1. Para qualquer comando de execução, você DEVE incluir a tag exata ao final da resposta.\n"
            "2. Se o usuário pedir para abrir o VS Code, use: [ACTION:OPEN_VSCODE]\n"
            "3. Se pedir para preparar ambiente/projeto (morea, assistant, api), use: [ACTION:OPEN_PROJECT|nome]\n"
            "4. Use as tags exatamente como definidas, sem espaços extras dentro delas.\n\n"
            f"CONTEXTO DE MEMÓRIA: {relevant_facts}\n"
            f"HISTÓRICO RECENTE: {history}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config={'system_instruction': system_instruction},
                contents=text
            )
            return response.text
        except Exception as e:
            if "429" in str(e): return "Senhor, atingi o limite de cota."
            return f"Falha técnica: {e}"

    def execute_action(self, response_text):
        res = response_text.upper()
        print(f"[DEBUG]: Analisando tags em: {res}")

        # Comandos Simples
        if "[ACTION:GET_TIME]" in res: return JarvisTools.get_time()
        if "[ACTION:OPEN_VSCODE]" in res: return JarvisTools.open_vscode()
        if "[ACTION:OPEN_DB]" in res: return JarvisTools.open_db_tool()
        if "[ACTION:OPEN_BLENDER]" in res: return JarvisTools.open_blender()
        if "[ACTION:CAPTURE]" in res: return JarvisTools.capture_screen()

        try:
            if "[ACTION:OPEN_PROJECT|" in res:
                proj = response_text.split("|")[1].split("]")[0].strip()
                return JarvisTools.open_project(proj)

            if "[ACTION:CHECK_PORT|" in res:
                port = response_text.split("|")[1].split("]")[0].strip()
                return JarvisTools.check_port(port)

            if "[ACTION:SEARCH_DOCS|" in res:
                tech = response_text.split("|")[1].split("]")[0].strip()
                return JarvisTools.search_docs(tech)

            if "[ACTION:OPEN_URL|" in res:
                link = response_text.split("|")[1].split("]")[0].strip()
                return JarvisTools.open_browser(link)

            if "[ACTION:SAVE_MEMORY|" in res:
                fact = response_text.split("|")[1].split(")")[0].strip()
                return self.memory.save_fact(fact)
        except Exception as e:
            print(f"[ERROR]: Falha ao processar parâmetros: {e}")

        return None

    async def process_workflow(self, input_text, is_voice=True):
        if self.is_busy: return
        self.is_busy = True

        try:
            await self.emit_state('thinking')
            response = await self.think(input_text)
            print(f"IA Response: {response}")

            action_result = self.execute_action(response)

            clean_response = re.sub(r'\[ACTION:.*?\]', '', response).strip()

            final_speech = clean_response
            if action_result:
                print(f"Resultado da Ação: {action_result}")
                if any(x in action_result for x in ["Agora são", "ocupada", "livre", "memorizado"]):
                    final_speech = f"{clean_response} {action_result}"

            await self.emit_state('speaking', {'text': final_speech})
            self.voice_system.speak(final_speech)
            self.memory.add_to_history("User", input_text)
            self.memory.add_to_history("Jarvis", final_speech)

        finally:
            await self.emit_state('idle')
            self.is_busy = False

    async def activate(self):
        if self.is_busy: return
        await self.emit_state('listening')
        user_text = self.listen_and_transcribe()
        if user_text:
            print(f"Você disse: {user_text}")
            await self.process_workflow(user_text)
        else:
            await self.emit_state('idle')


async def start_jarvis(app):
    loop = asyncio.get_event_loop()
    jarvis = Jarvis(loop)
    print(f"\n--- BACKEND JARVIS OPERACIONAL (Port 5000) ---")
    keyboard.add_hotkey('ctrl+shift+space', lambda: asyncio.run_coroutine_threadsafe(jarvis.activate(), loop))
    app['jarvis'] = jarvis


@sio.on('send_text_command')
async def handle_text_command(sid, data):
    jarvis = app['jarvis']
    text_input = data.get('text')
    if text_input:
        print(f"[TEXT_INPUT]: {text_input}")
        await jarvis.process_workflow(text_input, is_voice=False)


if __name__ == "__main__":
    app.on_startup.append(start_jarvis)
    web.run_app(app, host='127.0.0.1', port=5000)