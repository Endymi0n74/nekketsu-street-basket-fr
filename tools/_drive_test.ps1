# _drive_test.ps1 : focus Mesen (AttachThreadInput) then send keys in the same process.
$ErrorActionPreference = "Stop"
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class DRV {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}
'@
function Title($h) { if ($h -eq [IntPtr]::Zero) { return "(none)" }; $sb = New-Object System.Text.StringBuilder 256; [void][DRV]::GetWindowText($h, $sb, 256); $sb.ToString() }
function Focus-Mesen {
  $p = Get-Process Mesen -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { Write-Output "NO MESEN"; return $false }
  $h = $p.MainWindowHandle
  $fg = [DRV]::GetForegroundWindow()
  $fgThread = [DRV]::GetWindowThreadProcessId($fg, [ref]0)
  $myThread = [DRV]::GetCurrentThreadId()
  [void][DRV]::AttachThreadInput($myThread, $fgThread, $true)
  [void][DRV]::ShowWindow($h, 9)
  [void][DRV]::BringWindowToTop($h)
  [void][DRV]::SetForegroundWindow($h)
  [void][DRV]::AttachThreadInput($myThread, $fgThread, $false)
  Start-Sleep -Milliseconds 250
  return $true
}
function Tap($vk, [int]$holdMs = 120) {
  [DRV]::keybd_event([byte]$vk, 0, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds $holdMs
  [DRV]::keybd_event([byte]$vk, 0, 2, [UIntPtr]::Zero)
}
$vkS = 0x53  # S = A button
Focus-Mesen | Out-Null
Write-Output ("fg: '" + (Title ([DRV]::GetForegroundWindow())) + "'")
Write-Output "tapping S (A)"
Tap $vkS 200
Start-Sleep -Milliseconds 500
Write-Output "tapping S again"
Tap $vkS 200
Write-Output "done"
