-- _mt_state.lua : dump $0588 (state) + controller bytes + key RAM at the title,
-- and observe what A / Start / Select presses do.
local outdir = "D:/Codex/nes_translate/"
local prefix = "_st"
local f = io.open(outdir .. prefix .. "_log.txt", "w")
local function log(s)
  print(tostring(s))
  if f then f:write(tostring(s) .. "\n"); f:flush() end
end
local function save(name, data)
  local sf = assert(io.open(name, "wb"))
  sf:write(data)
  sf:close()
end
local function snapshot(tag)
  pcall(function()
    save(outdir .. prefix .. "_shot_" .. tag .. ".png", emu.takeScreenshot())
    log("shot " .. tag)
  end)
end
local function dumpState(tag)
  pcall(function()
    local out = {}
    for i = 0x0580, 0x05A0 do
      local v = emu.read(false, emu.memType.nesWorkRam, i)
      if v < 0 then v = v + 256 end
      out[#out + 1] = string.format("%02X:%02X ", i, v)
    end
    -- controller bytes $04/$05 + timers
    local c = {}
    for i = 0x04, 0x0B do
      local v = emu.read(false, emu.memType.nesWorkRam, i)
      if v < 0 then v = v + 256 end
      c[#c + 1] = string.format("%02X:%02X ", i, v)
    end
    local t = {}
    for i = 0x0300, 0x0310 do
      local v = emu.read(false, emu.memType.nesWorkRam, i)
      if v < 0 then v = v + 256 end
      t[#t + 1] = string.format("%02X:%02X ", i, v)
    end
    log("STATE " .. tag .. " 0588-05A0: " .. table.concat(out))
    log("STATE " .. tag .. " 04-0B: " .. table.concat(c))
    log("STATE " .. tag .. " 0300-0310: " .. table.concat(t))
  end)
end

local q = {}
local function wait(n) q[#q + 1] = { t = "wait", n = n } end
local function hold(b, n) q[#q + 1] = { t = "hold", b = b, n = n } end
local function snap(tag) q[#q + 1] = { t = "snap", tag = tag } end
local function st(tag) q[#q + 1] = { t = "st", tag = tag } end

wait(500)
for i = 1, 170 do
  hold("a", 8)
  wait(42)
end
hold("start", 10); wait(60)
st("title"); snap("title")
-- try A, watch state
hold("a", 10); wait(60); st("a1"); snap("a1")
hold("a", 10); wait(60); st("a2"); snap("a2")
-- try Start, held longer
hold("start", 20); wait(90); st("st1"); snap("st1")
hold("start", 20); wait(90); st("st2"); snap("st2")
-- try Select
hold("select", 10); wait(60); st("sel1"); snap("sel1")
-- try B
hold("b", 10); wait(60); st("b1"); snap("b1")
-- try Up
hold("up", 10); wait(60); st("up1"); snap("up1")
-- try Right
hold("right", 10); wait(60); st("r1"); snap("r1")
wait(120)

local qi, inQ, frame = 1, 0, 0
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
  elseif item.t == "st" then
    if inQ == 1 then dumpState(item.tag) end
    qi, inQ = qi + 1, 0
  end
  emu.setInput(input, 1)
end, emu.eventType.endFrame)
log("registered")
