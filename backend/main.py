import os
import asyncio
from dotenv import load_dotenv
from google import genai

# Carrega variáveis de ambiente
load_dotenv()


class JarvisBrain:
    def __init__(self):
        # Client padrão
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        self.model_id = "gemini-2.5-flash"
        self.user_name = os.getenv('USER_NAME', 'Genilsson')

    async def get_response(self, text):
        try:
            prompt_completo = (
                f"CONTEXTO: Você é o JARVIS, assistente do {self.user_name}. "
                "Responda de forma concisa, refinada e prestativa.\n\n"
                f"PERGUNTA: {text}"
            )

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt_completo
            )
            return response.text
        except Exception as e:
            return f"Senhor, erro nos núcleos de processamento: {str(e)}"


async def main():
    try:
        jarvis = JarvisBrain()
        print("--- JARVIS ONLINE (v3.0) ---")
        print(f"Sistemas carregados com Gemini 2.5. Às suas ordens, {os.getenv('USER_NAME')}.")

        while True:
            user_input = input("\nVocê: ")

            if user_input.lower() in ["sair", "desligar", "tchau"]:
                print("Jarvis: Desativando sistemas. Até logo, Senhor.")
                break

            if not user_input.strip(): continue

            print("Jarvis processando...")
            response = await jarvis.get_response(user_input)
            print(f"Jarvis: {response}")

    except Exception as e:
        print(f"Falha na ignição: {e}")


if __name__ == "__main__":
    asyncio.run(main())