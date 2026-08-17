# _focus.ps1 : bring the Mesen window to the foreground (AttachThreadInput trick, then click fallback).
$ErrorActionPreference = "Stop"
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class FW {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);

  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  public struct RECT { public int Left, Top, Right, Bottom; }
}
'@
function Title($h) { if ($h -eq [IntPtr]::Zero) { return "(none)" }; $sb = New-Object System.Text.StringBuilder 256; [void][FW]::GetWindowText($h, $sb, 256); $sb.ToString() }

$p = Get-Process Mesen -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { Write-Output "NO MESEN"; exit 1 }
$h = $p.MainWindowHandle
Write-Output ("before: '" + (Title ([FW]::GetForegroundWindow())) + "'")

# Method 1: AttachThreadInput trick
$fg = [FW]::GetForegroundWindow()
$fgThread = [FW]::GetWindowThreadProcessId($fg, [ref]0)
$myThread = [FW]::GetCurrentThreadId()
[void][FW]::AttachThreadInput($myThread, $fgThread, $true)
[void][FW]::ShowWindow($h, 9)
[void][FW]::BringWindowToTop($h)
[void][FW]::SetForegroundWindow($h)
[void][FW]::AttachThreadInput($myThread, $fgThread, $false)
Start-Sleep -Milliseconds 300
$now = [FW]::GetForegroundWindow()
Write-Output ("after1: '" + (Title $now) + "'")

if ($now -ne $h) {
  # Method 2: real mouse click on the window center
  $r = New-Object FW+RECT
  [void][FW]::GetWindowRect($h, [ref]$r)
  $cx = [int](($r.Left + $r.Right) / 2)
  $cy = [int](($r.Top + $r.Bottom) / 2)
  [void][FW]::SetCursorPos($cx, $cy)
  Start-Sleep -Milliseconds 150
  [FW]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero) # LEFTDOWN
  Start-Sleep -Milliseconds 60
  [FW]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero) # LEFTUP
  Start-Sleep -Milliseconds 300
  $now2 = [FW]::GetForegroundWindow()
  Write-Output ("after2: '" + (Title $now2) + "'")
}
