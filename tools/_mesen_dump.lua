-- Mesen 2.1.1 (GUI mode: Mesen.exe <rom> <script.lua> --enableStdout)
-- Navigate the menus toward the TACTICS screen; per stage: screenshot + WRAM dump.
-- Navigation mirrors _dump_ppu.lua: title -> Start -> A -> Down -> A -> A -> Start -> A.
-- NOTE: video-memory reads (nesPpuMemory/nesNametableRam) return 0 in this build;
-- screenshots + WRAM are the reliable channels (per romhack/NOTES_TEXTE.md).
local outdir = "D:/Codex/nes_translate/"
local prefix = os.getenv("CAP_PREFIX") or "_m"
local f = io.open(outdir .. prefix .. "_dump_log.txt", "w")
local function log(s)
  print(tostring(s))
  if f then f:write(tostring(s) .. "\n"); f:flush() end
end

local function save(name, data)
  local sf = assert(io.open(name, "wb"))
  sf:write(data)
  sf:close()
end

local function dumpWRAM(tag)
  local ok, err = pcall(function()
    local t = {}
    for i = 0, 0x1FFF do
      local v = emu.read(false, emu.memType.nesWorkRam, i)
      if v < 0 then v = v + 256 end
      t[i + 1] = string.char(v)
    end
    save(outdir .. prefix .. "_wram_" .. tag .. ".bin", table.concat(t))
    log("wram " .. tag)
  end)
  if not ok then log("wram " .. tag .. " ERR: " .. tostring(err)) end
end

local function snapshot(tag)
  local ok, err = pcall(function()
    save(outdir .. prefix .. "_shot_" .. tag .. ".png", emu.takeScreenshot())
    log("shot " .. tag)
  end)
  if not ok then log("shot " .. tag .. " ERR: " .. tostring(err)) end
end

local q = {}
local function wait(n) q[#q + 1] = { t = "wait", n = n } end
local function hold(b, n) q[#q + 1] = { t = "hold", b = b, n = n } end
local function snap(tag) q[#q + 1] = { t = "snap", tag = tag } end
local function wram(tag) q[#q + 1] = { t = "wram", tag = tag } end

wait(600); snap("t1"); wram("t1")
hold("start", 10); wait(90); snap("s1"); wram("s1"); wait(90); snap("s1b")
hold("a", 10); wait(90); snap("a1"); wram("a1"); wait(90); snap("a1b")
hold("down", 10); wait(90); snap("d1"); wram("d1")
hold("a", 10); wait(90); snap("a2"); wram("a2"); wait(90); snap("a2b")
hold("a", 10); wait(90); snap("a3"); wram("a3"); wait(90); snap("a3b")
hold("start", 10); wait(90); snap("st2"); wram("st2")
hold("a", 10); wait(90); snap("a4"); wram("a4")

local qi, inQ, frame = 1, 0, 0

emu.addEventCallback(function()
  frame = frame + 1
  local item = q[qi]
  if not item then
    emu.setInput({}, 1)
    if frame % 120 == 0 then log("idle f" .. frame) end
    if frame > 2400 then
      log("done")
      emu.stop()
    end
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
  elseif item.t == "wram" then
    if inQ == 1 then dumpWRAM(item.tag) end
    qi, inQ = qi + 1, 0
  end
  emu.setInput(input, 1)
end, emu.eventType.endFrame)
log("registered")
