-- _mt_nav.lua : Mesen 2.1.1 GUI — navigate fr.nes to a match and probe the TACTIQUES menu.
-- Run:  Mesen.exe D:/Codex/nes_translate/fr.nes D:/Codex/nes_translate/_mt_nav.lua --enableStdout
-- Path: boot -> Downtown quiz (~90 boxes, A x N) -> title -> Start -> SELECT(STORY) ->
--       A(1P) -> A(NEW YORK stage) -> team menu(EQUIPE) -> FIN -> match ->
--       probe Select/Start/Down during match for the TACTIQUES menu.
local outdir = "D:/Codex/nes_translate/"
local prefix = "_mt"
local f = io.open(outdir .. prefix .. "_nav_log.txt", "w")
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

-- ============ PHASE Q: clear the Downtown quiz + plane intro ============
wait(500)
for i = 1, 170 do
  hold("a", 8)
  wait(42)
  if i % 20 == 0 then snap("q" .. i) end
end
-- quiz done (hopefully): we should be at the title. Press Start twice.
hold("start", 10); wait(80); snap("afterquiz")
hold("start", 10); wait(120); snap("menu_sel")

-- ============ PHASE S: menus ============
-- SELECT: STORY is default -> A -> PLAYERS 1P -> A -> STAGES NEW YORK -> A -> team menu
hold("a", 10); wait(120); snap("s1_players")
hold("a", 10); wait(120); snap("s2_stages")
hold("a", 10); wait(120); snap("s3_team")
-- team menu: ► is on EQUIPE; go Right to FIN then A
hold("right", 8); wait(30); hold("a", 10); wait(200); snap("m1_fin")
wait(300); snap("m2")
wait(300); snap("m3")

-- ============ PHASE C: probe for TACTIQUES during match ============
-- attempt 1: Select (open command/tactics menu)
hold("select", 10); wait(60); snap("c1_sel")
wait(80); snap("c1b")
-- attempt 2: Start
hold("start", 10); wait(60); snap("c2_start")
wait(80); snap("c2b")
-- attempt 3: Down (move menu cursor) + A
hold("down", 8); wait(20); hold("a", 10); wait(60); snap("c3_downa")
wait(80); snap("c3b")
-- attempt 4: Select again + Down (submenu navigation)
hold("select", 10); wait(40); hold("down", 8); wait(30); snap("c4_seldown")
hold("a", 10); wait(60); snap("c4b")
wait(120); snap("c4c")

-- idle a bit then done
wait(300)

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
  end
  emu.setInput(input, 1)
end, emu.eventType.endFrame)
log("registered")
