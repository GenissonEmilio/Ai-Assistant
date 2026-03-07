import { app, BrowserWindow, screen, globalShortcut } from 'electron';
import * as path from 'path';
import { fileURLToPath } from 'url';
import isDev from 'electron-is-dev';
import { spawn, exec, ChildProcess } from 'child_process';
import * as fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let pythonProcess: ChildProcess | null = null;
const PANEL_WIDTH = 450;

function reorganizeWindows() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width } = primaryDisplay.workAreaSize;
  const targetWidth = width - PANEL_WIDTH;

  // Criamos um script físico para evitar erros de escape de string no terminal
  const scriptPath = path.join(app.getPath('temp'), 'jarvis_snap.ps1');
  
  const psScript = `
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern void GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int nWidth, int nHeight, bool bRepaint);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

[Win32]::EnumWindows({
    param($handle, $param)
    if ([Win32]::IsWindowVisible($handle)) {
        $sb = New-Object System.Text.StringBuilder 256
        [Win32]::GetWindowText($handle, $sb, 256)
        $title = $sb.ToString()
        if ($title -and $title -notmatch "Jarvis|Program Manager|Task bar") {
            $rect = New-Object Win32+RECT
            [Win32]::GetWindowRect($handle, [ref]$rect)
            if ($rect.Right -gt ${targetWidth}) {
                $height = $rect.Bottom - $rect.Top
                [Win32]::MoveWindow($handle, $rect.Left, $rect.Top, ${targetWidth}, $height, $true)
            }
        }
    }
    return $true
}, [IntPtr]::Zero)
  `;

  fs.writeFileSync(scriptPath, psScript, 'utf8');

  // Executa o arquivo .ps1 de forma limpa
  exec(`powershell -ExecutionPolicy Bypass -File "${scriptPath}"`, (err) => {
    if (err) console.error("[POWERSHELL-ERROR]:", err);
    else console.log("[SYSTEM]: Janelas movidas com sucesso.");
    // Opcional: deletar o arquivo após uso
    try { fs.unlinkSync(scriptPath); } catch (e) {}
  });
}

function startBackend() {
  const pythonPath = path.join(__dirname, '..', '..', 'backend', '.venv', 'Scripts', 'python.exe');
  const scriptPath = path.join(__dirname, '..', '..', 'backend', 'main.py');
  pythonProcess = spawn(pythonPath, [scriptPath]);
}

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;

  const win = new BrowserWindow({
    width: PANEL_WIDTH,
    height: screenHeight,
    x: screenWidth - PANEL_WIDTH,
    y: 0,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadURL(isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, '../out/index.html')}`);
  
  globalShortcut.register('CommandOrControl+Shift+X', () => app.quit());

  win.on('ready-to-show', () => {
    // Dá um pequeno delay para garantir que a janela do Jarvis já está lá
    setTimeout(reorganizeWindows, 1000);
  });

  startBackend();
}

app.whenReady().then(createWindow);

app.on('will-quit', () => {
  if (pythonProcess && pythonProcess.pid) {
    spawn("taskkill", ["/pid", pythonProcess.pid.toString(), "/f", "/t"]);
  }
  globalShortcut.unregisterAll();
});