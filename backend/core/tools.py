import os
import subprocess
import webbrowser
import pyautogui
from datetime import datetime

class JarvisTools:
    @staticmethod
    def open_project(project_name):
        projects = {
            "morea": r"C:\Users\esgen\OneDrive\Documentos\GitHub\trancadura-web-react",
            "assistant": r"C:\Users\esgen\OneDrive\Documentos\GitHub\Ai-Assistant",
            "api": r"C:\Users\esgen\OneDrive\Documentos\GitHub\trancadura-web-react-api"
        }
        path = projects.get(project_name.lower())
        if path:
            subprocess.Popen(f'code "{path}"', shell=True)
            return f"Ambiente {project_name} preparado no VS Code, Senhor."
        return "Projeto não localizado na base de dados."

    @staticmethod
    def open_vscode():
        try:
            subprocess.Popen(['code'], shell=True)
            return "Abrindo o Visual Studio Code, Senhor."
        except Exception:
            return "Não consegui localizar o VS Code no sistema."

    @staticmethod
    def check_port(port):
        try:
            result = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            return f"A porta {port} está ocupada por um processo, Senhor." if result else f"A porta {port} está livre."
        except:
            return f"A porta {port} parece estar disponível."

    @staticmethod
    def search_docs(tech):
        docs = {
            "laravel": "https://laravel.com/docs",
            "django": "https://docs.djangoproject.com/en/stable/",
            "nestjs": "https://docs.nestjs.com/",
            "blender": "https://docs.blender.org/manual/en/latest/"
        }
        url = docs.get(tech.lower(), f"https://www.google.com/search?q={tech}+documentation")
        webbrowser.open(url)
        return f"Localizando documentação de {tech}."

    @staticmethod
    def open_db_tool():
        subprocess.Popen("dbeaver", shell=True)
        return "Iniciando gerenciador de banco de dados para seus modelos DER."

    @staticmethod
    def monitor_serial():
        return "Senhor, recomendo abrir o monitor serial via VS Code para o projeto SPARC."

    @staticmethod
    def toggle_ssh(host="fedora-vm"):
        os.system(f"start cmd /k ssh {host}")
        return f"Estabelecendo conexão segura com {host}."

    @staticmethod
    def open_blender():
        path = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
        if os.path.exists(path):
            subprocess.Popen([path])
            return "Iniciando Blender. O notebook 3D nos espera, Senhor."
        return "Executável do Blender não encontrado no caminho padrão."

    @staticmethod
    def capture_screen():
        folder = r"C:\Users\esgen\OneDrive\Documentos\GitHub\portfolio\screenshots"
        if not os.path.exists(folder): os.makedirs(folder)
        filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(folder, filename)
        pyautogui.screenshot(path)
        return f"Captura de tela salva no seu diretório de portfólio."

    @staticmethod
    def get_time():
        return f"Agora são {datetime.now().strftime('%H:%M')}, Senhor."

    @staticmethod
    def open_browser(url="https://google.com"):
        webbrowser.open(url)
        return f"Abrindo navegador."