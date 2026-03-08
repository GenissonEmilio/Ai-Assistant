import os
import asyncio
import numpy as np
import sounddevice as sd
import keyboard
import socketio
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
        self.user_name = os.getenv('USER_NAME', 'Genisson')
        self.memory = JarvisMemory()

        print("Iniciando audição (Faster-Whisper small)...")
        self.stt_model = WhisperModel("small", device="cpu", compute_type="int8")
        self.fs = 16000

        print("Iniciando sintetizador de voz (Kokoro)...")
        self.voice_system = JarvisVoice()
        self.is_busy = False

    async def emit_state(self, state, data=None):
        """Envia o estado atual para o Frontend via WebSocket"""
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
        prompt = (
            f"Você é o JARVIS. Responda ao {self.user_name} de forma concisa.\n"
            f"HISTÓRICO:\n{history}\n"
            f"FATOS: {relevant_facts}\n"
            "AÇÕES: [ACTION:OPEN_VSCODE], [ACTION:GET_TIME], [ACTION:OPEN_URL|link], "
            "[ACTION:OPEN_PROJECT|X], [ACTION:CHECK_PORT|X], [ACTION:SEARCH_DOCS|X], "
            "[ACTION:OPEN_DB], [ACTION:OPEN_BLENDER], [ACTION:CAPTURE], [ACTION:SAVE_MEMORY|fato]\n"
            f"Pergunta: {text}"
        )
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return response.text
        except Exception as e:
            if "429" in str(e): return "Senhor, atingi o limite de cota. Aguarde um instante."
            return f"Falha técnica: {e}"

    def execute_action(self, response_text):
        if "[ACTION:GET_TIME]" in response_text: return JarvisTools.get_time()
        if "[ACTION:OPEN_VSCODE]" in response_text: return JarvisTools.open_vscode()
        if "[ACTION:OPEN_DB]" in response_text: return JarvisTools.open_db_tool()
        if "[ACTION:OPEN_BLENDER]" in response_text: return JarvisTools.open_blender()
        if "[ACTION:CAPTURE]" in response_text: return JarvisTools.capture_screen()
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

    async def activate(self):
        if self.is_busy: return
        self.is_busy = True

        await self.emit_state('listening')
        user_text = self.listen_and_transcribe()

        if user_text:
            await self.emit_state('thinking')
            print(f"Você disse: {user_text}")
            self.memory.add_to_history("User", user_text)

            response = await self.think(user_text)
            action_result = self.execute_action(response)
            clean_response = response.split("[ACTION")[0].strip()

            final_speech = clean_response
            if action_result and any(x in action_result for x in ["Agora são", "ocupada", "livre", "memorizado"]):
                final_speech = f"{clean_response} {action_result}"
            elif action_result:
                print(f"Sistema: {action_result}")

            print(f"Jarvis: {final_speech}")

            # Estado Falando para o Frontend
            await self.emit_state('speaking', {'text': final_speech})
            self.voice_system.speak(final_speech)
            self.memory.add_to_history("Jarvis", final_speech)

        await self.emit_state('idle')
        self.is_busy = False


async def start_jarvis(app):
    loop = asyncio.get_event_loop()
    jarvis = Jarvis(loop)
    print(f"\n--- BACKEND JARVIS OPERACIONAL (Websocket Port 5000) ---")
    print("Atalho: CTRL + SHIFT + SPACE")

    keyboard.add_hotkey('ctrl+shift+space', lambda: asyncio.run_coroutine_threadsafe(jarvis.activate(), loop))
    app['jarvis'] = jarvis


@sio.on('send_text_command')
async def handle_text_command(sid, data):
    jarvis = app['jarvis']
    text_input = data.get('text')
    if not text_input or jarvis.is_busy:
        return

    jarvis.is_busy = True
    print(f"[TEXT_INPUT]: {text_input}")

    jarvis.memory.add_to_history("User", text_input)
    await jarvis.emit_state('thinking')

    # Pula o STT e vai direto para a IA
    response = await jarvis.think(text_input)
    action_result = jarvis.execute_action(response)
    clean_response = response.split("[ACTION")[0].strip()

    final_speech = clean_response
    if action_result:
        final_speech = f"{clean_response} {action_result}"

    await jarvis.emit_state('speaking', {'text': final_speech})
    jarvis.voice_system.speak(final_speech)
    jarvis.memory.add_to_history("Jarvis", final_speech)

    await jarvis.emit_state('idle')
    jarvis.is_busy = False


if __name__ == "__main__":
    app.on_startup.append(start_jarvis)
    web.run_app(app, host='127.0.0.1', port=5000)