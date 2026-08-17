$ErrorActionPreference = "Stop"
$LOG = "D:/Codex/nes_translate/_tact_log.txt"
$DLOG = "D:/Codex/nes_translate/_tact_drive_log.txt"
$log = New-Object System.IO.StreamWriter($DLOG)
function DLog($s) { $log.WriteLine((Get-Date -Format "HH:mm:ss") + " " + $s); $log.Flush() }

Add-Type @'
using System;
using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
'@
Add-Type -AssemblyName System.Windows.Forms

function FocusMesen {
    $p = Get-Process Mesen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $p) { DLog "Mesen not running!"; return $false }
    $h = $p.MainWindowHandle
    $fg = [W]::GetForegroundWindow()
    if ($h -ne $fg) {
        $t = [W]::GetWindowThreadProcessId($fg, [ref]0)
        $m = [W]::GetCurrentThreadId()
        [W]::AttachThreadInput($m, $t, $true) | Out-Null
        [W]::ShowWindow($h, 9) | Out-Null
        [W]::BringWindowToTop($h) | Out-Null
        [W]::SetForegroundWindow($h) | Out-Null
        [W]::AttachThreadInput($m, $t, $false) | Out-Null
        Start-Sleep -Milliseconds 400
    }
    return $true
}

function Tap($key) {
    [System.Windows.Forms.SendKeys]::SendWait($key)
    Start-Sleep -Milliseconds 200
}

function GetGameInfo {
    # returns "state|frame|lines"; retries on transient read issues
    for ($try = 0; $try -lt 5; $try++) {
        try {
            $lines = @(Get-Content $LOG -ErrorAction Stop)
            if ($lines.Count -eq 0) { throw "empty" }
            $st = ""; $fr = 0
            foreach ($l in $lines) {
                if ($l -match "STATE=([0-9A-F]{2})") { $st = $Matches[1] }
                if ($l -match "^f(\d+)") { $fr = [int]$Matches[1] }
            }
            return "$st|$fr|$($lines.Count)"
        } catch {
            Start-Sleep -Milliseconds 300
        }
    }
    return "|0|0"
}

if (-not (FocusMesen)) { exit 1 }
DLog "focused"

# ---- Phase 1: quiz speed-up with A taps, stop at title (03) ----
for ($i = 0; $i -lt 12; $i++) {
    $info = GetGameInfo
    DLog ("pre-tap " + $i + ": " + $info)
    $parts = $info.Split("|")
    if ($parts[0] -eq "03") { DLog "title already showing -> will Start"; break }
    if ($parts[0] -eq "02") { DLog "SORT already open"; break }
    Tap("s")
    Start-Sleep -Milliseconds 1900
    $info = GetGameInfo
    DLog ("post-tap " + $i + ": " + $info)
    if ($info.StartsWith("03")) { DLog "title appeared after tap -> breaking to Start"; break }
}
DLog ("phase1 done: " + (GetGameInfo))

# ---- Phase 2: at title, press Start ----
$info = GetGameInfo
if ($info.StartsWith("03")) {
    DLog "at title -> pressing Start (W)"
    Tap("w")
    Start-Sleep -Seconds 5
    DLog ("after Start: " + (GetGameInfo))
}
if ((GetGameInfo).StartsWith("03")) {
    DLog "still title -> pressing Start again"
    Tap("w")
    Start-Sleep -Seconds 5
    DLog ("after Start#2: " + (GetGameInfo))
}
if ((GetGameInfo).StartsWith("03")) {
    DLog "still title -> pressing A"
    Tap("s")
    Start-Sleep -Seconds 4
    DLog ("after A: " + (GetGameInfo))
}

# ---- Phase 3: A presses following BizHawk fr3 (6-8 A's, long waits) ----
$info = GetGameInfo
DLog ("phase3 start: " + $info)
for ($i = 1; $i -le 10; $i++) {
    Tap("s")
    Start-Sleep -Seconds 5
    $cur = GetGameInfo
    DLog ("A#" + $i + " -> " + $cur)
    $parts = $cur.Split("|")
    # if we left state 02/03/04 (e.g. match=01 or other), stop
    if ($parts[0] -ne "02" -and $parts[0] -ne "03" -and $parts[0] -ne "04" -and $parts[0] -ne "") {
        DLog "!! state changed to $($parts[0]), stopping A presses"
        break
    }
}

DLog "DONE"
$log.Close()
