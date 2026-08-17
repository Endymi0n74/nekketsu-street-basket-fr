-- Mesen 2.1.1 (GUI mode: Mesen.exe <rom> <script.lua> --enableStdout)
-- Continue from the SORT screen (a4): explore A / Start / Select presses, screenshot each stage.
local outdir = "D:/Codex/nes_translate/"
local prefix = os.getenv("CAP_PREFIX") or "_m2"
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

-- Reproduce the first part to reach the SORT screen (a4 of run 1)
wait(600); snap("p0_title")
hold("start", 10); wait(180); snap("p1")
hold("a", 10); wait(180); snap("p2")
hold("down", 10); wait(180); snap("p3")
hold("a", 10); wait(180); snap("p4")
hold("a", 10); wait(180); snap("p5")
hold("start", 10); wait(180); snap("p6")
hold("a", 10); wait(180); snap("p7_sort")

-- Explore: A, Down, Start, Select combos
hold("a", 10); wait(120); snap("x1_a")
hold("down", 10); wait(120); snap("x2_down")
hold("a", 10); wait(120); snap("x3_a")
hold("start", 10); wait(120); snap("x4_start")
hold("select", 10); wait(120); snap("x5_select")
hold("a", 10); wait(120); snap("x6_a")
hold("start", 10); wait(120); snap("x7_start")

local qi, inQ, frame = 1, 0, 0
emu.addEventCallback(function()
  frame = frame + 1
  local item = q[qi]
  if not item then
    emu.setInput({}, 1)
    if frame > 300 then log("done"); emu.stop() end
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
