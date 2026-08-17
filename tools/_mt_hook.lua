-- _mt_hook.lua : trace the state machine by hooking WRAM writes.
--  $0588 = main state, $0589 = substate, $04 = controller byte.
local outdir = "D:/Codex/nes_translate/"
local prefix = "_hk"
local f = io.open(outdir .. prefix .. "_log.txt", "w")
local function log(s)
  print(tostring(s))
  if f then f:write(tostring(s) .. "\n"); f:flush() end
end
local function snapshot(tag)
  pcall(function()
    local sf = assert(io.open(outdir .. prefix .. "_shot_" .. tag .. ".png", "wb"))
    sf:write(emu.takeScreenshot())
    sf:close()
    log("shot " .. tag)
  end)
end

local frame = 0
local last4 = -1
local last88 = -1
local last89 = -1
local ctrl = {}

local function hook(addr, name)
  local ok, err = pcall(function()
    emu.addMemoryCallback(function(a, val)
      if name == "ctrl" and val ~= last4 then
        last4 = val
        log(string.format("f%05d ctrl $04=%02X", frame, val))
      elseif name == "state" and val ~= last88 then
        last88 = val
        log(string.format("f%05d STATE $0588=%02X", frame, val))
      elseif name == "sub" and val ~= last89 then
        last89 = val
        log(string.format("f%05d SUB  $0589=%02X", frame, val))
      end
    end, emu.callbackType.write, addr, addr, emu.memType.InternalRam)
  end)
  log(string.format("hook %s @ %04X -> %s %s", name, addr, tostring(ok), tostring(err)))
end
hook(0x04, "ctrl")
hook(0x0588, "state")
hook(0x0589, "sub")
log("hooks registered")

local q = {}
local function wait(n) q[#q + 1] = { t = "wait", n = n } end
local function hold(b, n) q[#q + 1] = { t = "hold", b = b, n = n } end
local function snap(tag) q[#q + 1] = { t = "snap", tag = tag } end

wait(500)
for i = 1, 170 do
  hold("a", 8)
  wait(42)
end
hold("start", 10); wait(60); snap("title")
-- probe inputs at title
hold("a", 10); wait(60); snap("a1")
hold("a", 10); wait(60); snap("a2")
hold("start", 20); wait(90); snap("st1")
hold("start", 20); wait(90); snap("st2")
hold("select", 10); wait(60); snap("sel1")
hold("b", 10); wait(60); snap("b1")
wait(120)

local qi, inQ = 1, 0
emu.addEventCallback(function()
  frame = frame + 1
  local item = q[qi]
  if not item then
    emu.setInput({}, 1)
    log("done")
    emu.stop()
    return
  end
  inQ = inQ + 1
  local input = {}
  if item.t == "hold" then
    if inQ <= item.n then input[item.b] = true end
    if inQ > item.n then qi, inQ = qi + 1, 0 end
  elseif item.t == "wait" then
    if inQ >= item.n then qi, inQ = qi + 1, 0 end
  elseif item.t == "snap" then
    if inQ == 1 then snapshot(item.tag) end
    qi, inQ = qi + 1, 0
  end
  emu.setInput(input, 1)
end, emu.eventType.endFrame)
log("registered")
