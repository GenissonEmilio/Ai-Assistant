import { app, BrowserWindow, screen, globalShortcut } from 'electron';
import * as path from 'path';
import { fileURLToPath } from 'url';
import isDev from 'electron-is-dev';
import { spawn, ChildProcess } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let pythonProcess: ChildProcess | null = null;

function startBackend() {
  const pythonPath = path.join(__dirname, '..', '..', 'backend', '.venv', 'Scripts', 'python.exe');
  const scriptPath = path.join(__dirname, '..', '..', 'backend', 'main.py');

  pythonProcess = spawn(pythonPath, [scriptPath]);

  pythonProcess.stdout?.on('data', (data) => {
    console.log(`[PYTHON]: ${data.toString().trim()}`);
  });

  pythonProcess.stderr?.on('data', (data) => {
    console.error(`[PYTHON-ERROR]: ${data.toString().trim()}`);
  });
}

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  const panelWidth = 450;

  const win = new BrowserWindow({
    width: panelWidth,
    height: screenHeight,
    x: screenWidth - panelWidth, // Inicia na direita, mas agora pode sair de lá
    y: 0,
    frame: false, // Mantém sem bordas
    transparent: true,
    alwaysOnTop: true,
    resizable: true, // AGORA É MÓVEL
    skipTaskbar: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadURL(isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, '../out/index.html')}`);

  globalShortcut.register('CommandOrControl+Shift+X', () => {
    app.quit();
  });

  startBackend();
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  if (pythonProcess && pythonProcess.pid) {
    spawn("taskkill", ["/pid", pythonProcess.pid.toString(), "/f", "/t"]);
  }
  globalShortcut.unregisterAll();
});