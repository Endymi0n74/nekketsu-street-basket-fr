-- _nav_log.lua : screenshots every 60 frames + state/$04 logging for the full navigation run.
local outdir = "D:/Codex/nes_translate/"
local f = io.open(outdir .. "_nav_log.txt", "w")
local function log(s)
  print(tostring(s))
  if f then f:write(tostring(s) .. "\n"); f:flush() end
end
local frame = 0
local last88 = -1
local ok, err = pcall(function()
  emu.addMemoryCallback(function(a, v)
    if v ~= last88 then
      last88 = v
      log(string.format("f%06d STATE=%02X", frame, v))
    end
  end, emu.callbackType.write, 0x0588, 0x0588, emu.memType.InternalRam)
end)
log("state hook -> " .. tostring(ok) .. " " .. tostring(err))
emu.addEventCallback(function()
  frame = frame + 1
  if frame % 60 == 0 then
    pcall(function()
      local sf = assert(io.open(string.format(outdir .. "_nav_shot_%06d.png", frame), "wb"))
      sf:write(emu.takeScreenshot())
      sf:close()
    end)
  end
end, emu.eventType.endFrame)
log("registered")
