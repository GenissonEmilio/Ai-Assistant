import { app, BrowserWindow, screen, globalShortcut } from 'electron';
import * as path from 'path';
import { fileURLToPath } from 'url';
import isDev from 'electron-is-dev';
import { spawn, ChildProcess } from 'child_process';
import * as fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let pythonProcess: ChildProcess | null = null;
let win: BrowserWindow | null = null;
const PANEL_WIDTH = 450;

// Garante instância única
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (win) {
      if (win.isMinimized()) win.restore();
      win.show();
      win.focus();
    }
  });
}

function startBackend() {
  const isProd = app.isPackaged;
  const pythonPath = isProd 
    ? path.join(process.resourcesPath, 'backend', 'jarvis_backend.exe')
    : path.join(__dirname, '..', '..', 'backend', '.venv', 'Scripts', 'python.exe');

  const args = isProd ? [] : [path.join(__dirname, '..', '..', 'backend', 'main.py')];

  console.log(`[SYSTEM]: Iniciando backend em ${pythonPath}`);

  if (fs.existsSync(pythonPath) || !isProd) {
    // Iniciamos o processo normalmente. O Python cuidará do atalho via biblioteca 'keyboard'.
    pythonProcess = spawn(pythonPath, args);
    
    pythonProcess.stdout?.on('data', (data) => console.log(`[PYTHON]: ${data.toString()}`));
    pythonProcess.stderr?.on('data', (data) => console.error(`[PYTHON-ERROR]: ${data.toString()}`));
  }
}

function createWindow() {
  const { height: screenHeight, width: screenWidth } = screen.getPrimaryDisplay().workAreaSize;

  win = new BrowserWindow({
    width: PANEL_WIDTH,
    height: screenHeight,
    x: screenWidth - PANEL_WIDTH,
    y: 0,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: true,
    title: "Jarvis Mark VII",
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false 
    },
  });

  if (isDev) {
    win.loadURL('http://localhost:3000');
  } else {
    win.loadFile(path.join(__dirname, '..', 'out', 'index.html'));
  }

  // ATALHO DE SEGURANÇA: Apenas para fechar o app completamente.
  globalShortcut.register('CommandOrControl+Shift+X', () => {
    app.quit();
  });

  // REMOVIDO: O registro de Ctrl+Shift+Space aqui. 
  // Isso permite que o evento passe direto para o SO e seja lido pelo seu Python.

  startBackend();
}

app.whenReady().then(createWindow);

app.on('will-quit', () => {
  if (pythonProcess && pythonProcess.pid) {
    spawn("taskkill", ["/pid", pythonProcess.pid.toString(), "/f", "/t"]);
  }
  globalShortcut.unregisterAll();
});