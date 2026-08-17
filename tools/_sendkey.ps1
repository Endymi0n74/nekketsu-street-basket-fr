# _sendkey.ps1 : focus Mesen and press one key (tap or hold).
param([string]$key = "X", [int]$hold = 80)
$ErrorActionPreference = "Stop"
$sig = @'
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
'@
$k = Add-Type -MemberDefinition $sig -Name K32 -Namespace W -PassThru
$p = Get-Process Mesen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($p) { [void]$k::SetForegroundWindow($p.MainWindowHandle) }
Start-Sleep -Milliseconds 250
$vk = switch ($key) {
  "UP"    { 0x26 } "DOWN" { 0x28 } "LEFT" { 0x25 } "RIGHT" { 0x27 }
  "ENTER" { 0x0D } "SPACE" { 0x20 } "RSHIFT" { 0xA1 } "LSHIFT" { 0xA0 }
  "A"     { 0x41 } "S" { 0x53 } "D" { 0x44 } "Z" { 0x5A } "X" { 0x58 } "W" { 0x57 } "Q" { 0x51 } "E" { 0x45 }
  default { [int][char]$key[0] }
}
$k::keybd_event([byte]$vk, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds $hold
$k::keybd_event([byte]$vk, 0, 2, [UIntPtr]::Zero)
