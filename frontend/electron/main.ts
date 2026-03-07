import { app, BrowserWindow, screen, globalShortcut } from 'electron';
import * as path from 'path';
import isDev from 'electron-is-dev';
import { spawn, ChildProcess, exec } from 'child_process';
import * as fs from 'fs';

let pythonProcess: ChildProcess | null = null;
let win: BrowserWindow | null = null;
const PANEL_WIDTH = 450;

function reorganizeWindows() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width } = primaryDisplay.workAreaSize;
  const targetWidth = width - PANEL_WIDTH;
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
        # Ignora o Jarvis pelo título exato para não mover a si mesmo
        if ($title -and $title -notmatch "Jarvis Mark VII|Program Manager|Task bar") {
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
  // Executa de forma oculta e com bypass para não falhar
  exec(`powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "${scriptPath}"`, () => {
    try { fs.unlinkSync(scriptPath); } catch (e) {}
  });
}

function startBackend() {
  const isProd = app.isPackaged;
  let pythonPath: string;
  let args: string[] = [];

  if (isProd) {
    pythonPath = path.join(process.resourcesPath, 'backend', 'jarvis_backend.exe');
  } else {
    pythonPath = path.join(__dirname, '..', '..', 'backend', '.venv', 'Scripts', 'python.exe');
    args = [path.join(__dirname, '..', '..', 'backend', 'main.py')];
  }

  if (fs.existsSync(pythonPath) || !isProd) {
    pythonProcess = spawn(pythonPath, args);
  }
}

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;

  win = new BrowserWindow({
    width: PANEL_WIDTH,
    height: screenHeight,
    x: screenWidth - PANEL_WIDTH,
    y: 0,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
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
    const indexPath = path.join(__dirname, '..', 'out', 'index.html');
    win.loadFile(indexPath);
  }

  // Atalho Global para Fechar
  globalShortcut.register('CommandOrControl+Shift+X', () => app.quit());

  // Atalho Global para Ativar/Esconder (O "Protocolo Mark VII")
  globalShortcut.register('CommandOrControl+Shift+Space', () => {
    if (win) {
      if (win.isVisible()) {
        win.hide();
      } else {
        win.show();
        win.focus();
        // Sempre que o Jarvis volta, ele garante o seu espaço na tela
        reorganizeWindows();
      }
    }
  });

  win.on('ready-to-show', () => {
    setTimeout(reorganizeWindows, 2500);
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