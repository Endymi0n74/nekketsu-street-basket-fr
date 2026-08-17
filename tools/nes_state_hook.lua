-- nes_state_hook.lua - generic NES state-machine tracer for Mesen 2.1.1 (GUI).
--
-- Reusable on any NES game: configurable through environment variables, with
-- defaults matching Nekketsu Street Basket. It logs WRAM write-hooks per
-- address (state / substate / controller byte / anything), takes screenshots
-- periodically and on state change, and can count executions of a routine
-- (e.g. the input poll) to prove it runs every frame.
--
-- Mesen API note: emu.read/emu.write/emu.setInput are no-ops on this build;
-- memory write callbacks, event callbacks and exec callbacks work, and
-- emu.takeScreenshot() returns PNG bytes in GUI mode. See docs/05-emulator-notes.md.
--
-- Usage (Mesen.exe <rom> <script> --enableStdout):
--   HOOK_ADDRS="state:0x0588:snap,sub:0x0589,ctrl:0x04" \
--   HOOK_EXEC=0xFF98 HOOK_OUTDIR=D:/tmp ./Mesen.exe fr.nes nes_state_hook.lua
--
-- Environment variables (all optional):
--   HOOK_OUTDIR     output directory (default ".")          - set it, Mesen's
--                                                             cwd is the exe dir!
--   HOOK_PREFIX     log/shot file prefix (default "hook")
--   HOOK_MEMTYPE    memory type (default "InternalRam")
--   HOOK_ADDRS      comma list "name:addr" or "name:addr:snap"
--                   (default "state:0x0588:snap,sub:0x0589,ctrl:0x04")
--   HOOK_SNAP_EVERY screenshot every N frames (default 600; 0 = off)
--   HOOK_EXEC       exec-hook address to count executions (default 0xFF98,
--                   Nekketsu's input-poll end; "" or 0 = off)
--   HOOK_MAX_FRAMES stop after N frames (default 0 = unlimited)

local outdir = os.getenv("HOOK_OUTDIR") or "."
local prefix = os.getenv("HOOK_PREFIX") or "hook"
local memType = os.getenv("HOOK_MEMTYPE") or "InternalRam"

-- env number: unset/empty -> default; "0" stays 0 (explicit off)
local function envNum(name, dflt)
  local v = os.getenv(name)
  if v == nil or v == "" then return dflt end
  return tonumber(v) or 0
end
local snapEvery = envNum("HOOK_SNAP_EVERY", 600)
local execAddr = envNum("HOOK_EXEC", 0xFF98)
local maxFrames = envNum("HOOK_MAX_FRAMES", 0)

local ADDRS_DEFAULT = "state:0x0588:snap,sub:0x0589,ctrl:0x04"
local addrSpec = os.getenv("HOOK_ADDRS") or ADDRS_DEFAULT

local f = io.open(outdir .. "/" .. prefix .. "_log.txt", "w")
local function log(s)
  print(tostring(s))
  if f then f:write(tostring(s) .. "\n"); f:flush() end
end

local function u8(v)
  if v < 0 then v = v + 256 end
  return v
end

local frame = 0
local last = {}          -- name -> last seen value
local snapOnChange = {}  -- name -> bool (screenshot when value changes)

local function screenshot(tag)
  pcall(function()
    local sf = assert(io.open(outdir .. "/" .. prefix .. "_shot_" .. tag .. ".png", "wb"))
    sf:write(emu.takeScreenshot())
    sf:close()
    log("shot " .. tag)
  end)
end

-- --- write hooks ---------------------------------------------------------
local function addWriteHook(name, addr, snap)
  local ok, err = pcall(function()
    emu.addMemoryCallback(function(a, v)
      v = u8(v)
      if v ~= last[name] then
        last[name] = v
        log(string.format("f%06d %-8s $%04X=%02X", frame, name, addr, v))
        if snap then screenshot(string.format("%s_f%06d", name, frame)) end
      end
    end, emu.callbackType.write, addr, addr, emu.memType[memType])
  end)
  log(string.format("hook %s @ $%04X -> %s %s", name, addr, tostring(ok), tostring(err)))
end

for name, addr, snap in string.gmatch(addrSpec, "([^,:]+):([^,:]+)(:snap)?") do
  local a = tonumber(addr)
  if a then
    snapOnChange[name] = (snap ~= nil)
    addWriteHook(name, a, snapOnChange[name])
  else
    log("bad addr for " .. name .. ": " .. addr)
  end
end

-- --- exec counter --------------------------------------------------------
local execCount = 0
local execReported = 0
local function addExecHook(addr)
  local ok, err = pcall(function()
    emu.addEventCallback(function()
      execCount = execCount + 1
    end, emu.callbackType.exec, addr, addr, emu.memType[memType])
  end)
  log(string.format("exec hook @ $%04X -> %s %s", addr, tostring(ok), tostring(err)))
end
if execAddr and execAddr ~= 0 then addExecHook(execAddr) end

-- --- per-frame events -----------------------------------------------------
emu.addEventCallback(function()
  frame = frame + 1
  if snapEvery > 0 and frame % snapEvery == 0 then
    screenshot(string.format("t%06d", frame))
  end
  if execCount > 0 and frame - execReported >= 300 then
    log(string.format("f%06d exec $%04X: %d hits (~%.1f/frame)",
      frame, execAddr, execCount, execCount / frame))
    execReported = frame
  end
  if maxFrames > 0 and frame >= maxFrames then
    log("max frames reached, stopping")
    emu.stop()
  end
end, emu.eventType.endFrame)

log("nes_state_hook registered (outdir=" .. outdir .. ", prefix=" .. prefix
  .. ", addrs=" .. addrSpec .. ", snapEvery=" .. snapEvery
  .. ", exec=$" .. string.format("%04X", execAddr or 0) .. ")")
