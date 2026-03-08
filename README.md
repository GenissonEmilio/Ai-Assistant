# Jarvis Mark VII 🤖

![Next.js](https://img.shields.io/badge/next.js-%23000000.svg?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Three.js](https://img.shields.io/badge/threejs-black?style=for-the-badge&logo=three.js&logoColor=white)
![Electron](https://img.shields.io/badge/Electron-47848F?style=for-the-badge&logo=electron&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75C2?style=for-the-badge&logo=googlegemini&logoColor=white)

O **Jarvis Mark VII** é um assistente virtual de elite desenvolvido para automatizar fluxos de trabalho de desenvolvimento, gestão de projetos e controle de ambiente. Ele combina uma interface futurista em **Next.js** com um cérebro robusto em **Python**, integrando a **Gemini API** para processamento de linguagem natural e o **Faster-Whisper** para reconhecimento de voz de baixa latência.

---

## 🚀 Funcionalidades Principais

* **Interface Híbrida**: Aceita comandos de voz (STT) e entrada de texto via terminal interativo.
* **Orbe Energético 3D**: Interface visual reativa desenvolvida com Three.js/React Three Fiber que altera sua forma (esfera para onda infinita) baseada no estado do assistente (Ouvindo, Pensando, Falando).
* **Preparação de Ambiente**: Comandos inteligentes para abrir projetos específicos no VS Code, preparar containers ou APIs (ex: Morea, Assistant, API).
* **Automação de Sistema**: Captura de tela, verificação de portas de rede, abertura de ferramentas de design (Blender) e gerenciadores de banco de dados (DBeaver).
* **Execução Silenciosa**: Todas as ferramentas do sistema são disparadas em background, sem janelas indesejadas do CMD.

## 🛠️ Tecnologias Utilizadas

### Frontend
* **Next.js 15 & React**: Estrutura da aplicação e interface.
* **Three.js / React Three Fiber**: Renderização de partículas da Orbe.
* **Electron**: Empacotamento para Desktop e gerenciamento de janelas.
* **Tailwind CSS**: Estilização futurista e efeitos de blur.

### Backend (Core)
* **Python 3.10+**: Motor de processamento.
* **Google GenAI (Gemini 2.0 Flash)**: Processamento de intenções e lógica de ações.
* **Faster-Whisper**: Transcrição de áudio local ultrarrápida.
* **Socket.io**: Comunicação em tempo real entre Python e Frontend.

## ⌨️ Comandos de Atalho

* **`Ctrl + Shift + Space`**: Ativa o modo de escuta (Voice Command).
* **`Ctrl + Shift + X`**: Encerra o protocolo e fecha a aplicação completamente.
* **Teclas 1, 2, 3 (Modo de Teste)**: Força estados visuais (Listening, Thinking, Speaking) para testes de interface.

## 🔧 Instalação e Execução

1.  **Clone o repositório**:
    ```bash
    git clone [https://github.com/seu-usuario/Ai-Assistant.git](https://github.com/seu-usuario/Ai-Assistant.git)
    ```

2.  **Configure o Backend**:
    * Crie um ambiente virtual: `python -m venv .venv`
    * Instale as dependências: `pip install -r requirements.txt`
    * Configure o `.env` com sua `GEMINI_API_KEY` e `USER_NAME=Genisson`.

3.  **Inicie o Sistema**:
    No terminal do frontend, execute:
    ```bash
    npm run jarvis
    ```

## 📝 Licença

Este projeto é de uso pessoal e acadêmico. Desenvolvido por **Genisson**.

---
"Sistemas em espera. Invoque para interagir."
