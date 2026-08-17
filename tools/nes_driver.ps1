# nes_driver.ps1 - generic keyboard driver for emulator automation (Windows).
#
# Companion of tools/nes_state_hook.lua: it reads that hook's log, brings the
# emulator window to the foreground (AttachThreadInput + SetForegroundWindow,
# same-process SendKeys - the only input path that works with broken Lua
# setInput on Mesen 2.1.1), and drives a *data-defined sequence* of button
# presses, configurable per game. Defaults = Nekketsu Street Basket.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools/nes_driver.ps1
#
# Environment variables (optional):
#   NESDRV_LOG     hook log to read (default "hook_log.txt")
#   NESDRV_DLOG    driver log (default "driver_log.txt")
#   NESDRV_PROC    emulator process name (default "Mesen")
#
# Per-game configuration lives in the $KEYMAP / $SEQ blocks below.
#
# Sequence step types (hashtables):
#   @{ t="wait";  s=<seconds> }
#   @{ t="tap";   btn="A" }
#   @{ t="hold";  btn="Start"; ms=<milliseconds> }        # real press-and-hold
#   @{ t="taps";  btn="A"; n=<count>; gap=<ms>; after=<s>; stopNotIn="02,03,04" }
#   @{ t="until"; state=<regex>; timeout=<s>; tap=<btn>; gap=<ms>; msg=<str> }
#                 # poll log until current STATE matches <regex> (optionally
#                 # tapping <btn> every <gap> ms while waiting)
#   @{ t="log";   msg=<str> }

$ErrorActionPreference = "Stop"

# ---------- per-game configuration (edit or override via env) -------------
$LOG  = if ($env:NESDRV_LOG) { $env:NESDRV_LOG } else { "hook_log.txt" }
$DLOG = if ($env:NESDRV_DLOG) { $env:NESDRV_DLOG } else { "driver_log.txt" }
$PROC = if ($env:NESDRV_PROC) { $env:NESDRV_PROC } else { "Mesen" }

# NES button -> SendKeys string (Mesen Mapping2 defaults)
$KEYMAP = @{
  A = "s"; B = "a"; Start = "w"; Select = "q"
  Up = "{UP}"; Down = "{DOWN}"; Left = "{LEFT}"; Right = "{RIGHT}"
}

# Nekketsu default sequence: quiz speed-up -> Start at title -> A presses.
$SEQ = @(
  @{ t = "until"; state = "0[23]"; timeout = 240; tap = "A"; gap = 1900
     msg = "phase1: A taps until title(03)/SORT(02)" }
  @{ t = "tap"; btn = "Start"; msg = "phase2: Start at title" }
  @{ t = "wait"; s = 5 }
  @{ t = "tap"; btn = "Start"; msg = "phase2b: Start again if still title" }
  @{ t = "wait"; s = 5 }
  @{ t = "taps"; btn = "A"; n = 10; gap = 5000; stopNotIn = "02,03,04"
     msg = "phase3: A presses toward match (stop if state leaves 02/03/04)" }
)
# --------------------------------------------------------------------------

Add-Type @'
using System;
using System.Runtime.InteropServices;
public class N {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}
'@
Add-Type -AssemblyName System.Windows.Forms

$logger = New-Object System.IO.StreamWriter($DLOG)
function DLog($s) { $logger.WriteLine((Get-Date -Format "HH:mm:ss") + " " + $s); $logger.Flush() }

function FocusWindow {
    $p = Get-Process $PROC -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $p) { DLog "$PROC not running!"; return $false }
    $h = $p.MainWindowHandle
    $fg = [N]::GetForegroundWindow()
    if ($h -ne $fg) {
        $t = [N]::GetWindowThreadProcessId($fg, [ref]0)
        $m = [N]::GetCurrentThreadId()
        [N]::AttachThreadInput($m, $t, $true) | Out-Null
        [N]::ShowWindow($h, 9) | Out-Null
        [N]::BringWindowToTop($h) | Out-Null
        [N]::SetForegroundWindow($h) | Out-Null
        [N]::AttachThreadInput($m, $t, $false) | Out-Null
        Start-Sleep -Milliseconds 400
    }
    return $true
}

function Tap($btn) {
    $key = $KEYMAP[$btn]
    if (-not $key) { DLog "no key mapped for button '$btn'"; return }
    [System.Windows.Forms.SendKeys]::SendWait($key)
    Start-Sleep -Milliseconds 200
}

function VkOf($key) {
    # SendKeys string -> virtual key code (for hold via keybd_event)
    switch ($key) {
        "{UP}" { return 0x26 } "{DOWN}" { return 0x28 }
        "{LEFT}" { return 0x25 } "{RIGHT}" { return 0x27 }
        "{ENTER}" { return 0x0D } "{ESC}" { return 0x1B }
        "{TAB}" { return 0x09 } "{SPACE}" { return 0x20 }
        "{BACKSPACE}" { return 0x08 } "{DELETE}" { return 0x2E }
        default {
            if ($key.Length -eq 1) { return [int][char]($key.ToUpper()) }
            return 0
        }
    }
}

function Hold($btn, $ms) {
    $key = $KEYMAP[$btn]
    if (-not $key) { DLog "no key mapped for button '$btn'"; return }
    $vk = VkOf $key
    if ($vk -eq 0) { DLog "cannot hold key '$key'"; return }
    [N]::keybd_event([byte]$vk, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds $ms
    [N]::keybd_event([byte]$vk, 0, 2, [UIntPtr]::Zero)  # KEYEVENTF_KEYUP
}

function GetState {
    # Last STATE hex value from the hook log (nes_state_hook.lua format, or
    # legacy "STATE=XX" format). Returns "" if the log is empty/unreadable.
    $st = ""
    foreach ($l in (Get-Content $LOG -ErrorAction SilentlyContinue)) {
        if ($l -match "^f(\d+)\s+state\s+\$[0-9A-Fa-f]{4}=([0-9A-Fa-f]{2})") {
            $st = $Matches[2].ToUpper()
        } elseif ($l -match "^f(\d+)\s+STATE=([0-9A-Fa-f]{2})") {
            $st = $Matches[2].ToUpper()
        }
    }
    return $st
}

function Step-Until($s) {
    $deadline = (Get-Date).AddSeconds([int]$s.timeout)
    while ((Get-Date) -lt $deadline) {
        $cur = GetState
        if ($cur -and $cur -match $s.state) {
            DLog ("until '" + $s.state + "' matched at state " + $cur)
            return
        }
        if ($s.tap) { Tap $s.tap }
        Start-Sleep -Milliseconds ([int]$s.gap)
    }
    DLog ("until '" + $s.state + "' TIMEOUT after " + $s.timeout + "s (state=" + (GetState) + ")")
}

function Step-Taps($s) {
    for ($i = 1; $i -le [int]$s.n; $i++) {
        Tap $s.btn
        Start-Sleep -Milliseconds ([int]$s.gap)
        $cur = GetState
        if ($s.stopNotIn -and $cur -and ($s.stopNotIn.Split(",") -notcontains $cur)) {
            DLog ("state " + $cur + " not in [" + $s.stopNotIn + "], stopping taps")
            return
        }
        DLog ("tap#" + $i + " (" + $s.btn + ") -> state " + $cur)
    }
}

function Run-Sequence($seq) {
    foreach ($s in $seq) {
        switch ($s.t) {
            "wait"  { Start-Sleep -Seconds ([int]$s.s) }
            "tap"   { Tap $s.btn; if ($s.msg) { DLog ("tap " + $s.btn + " - " + $s.msg) } else { DLog ("tap " + $s.btn) } }
            "hold"  { Hold $s.btn ([int]$s.ms); DLog ("held " + $s.btn + " " + $s.ms + "ms") }
            "taps"  { Step-Taps $s }
            "until" { Step-Until $s }
            "log"   { DLog $s.msg }
            default { DLog ("unknown step type: " + $s.t) }
        }
    }
}

if ($MyInvocation.InvocationName -ne ".") {
    if (-not (FocusWindow)) { exit 1 }
    DLog ("focused " + $PROC + ", sequence starting (state=" + (GetState) + ")")
    Run-Sequence $SEQ
    DLog "DONE"
    $logger.Close()
}
