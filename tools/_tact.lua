-- _tact.lua: log $0588 (state) / $0589 (sub) writes, screenshot periodically + on state change
local outdir = "D:/Codex/nes_translate/"
local f = io.open(outdir .. "_tact_log.txt", "w")
local function log(s)
  print(tostring(s))
  if f then f:write(tostring(s) .. "\n"); f:flush() end
end
local frame = 0
local last88 = -1
local last89 = -1

local function screenshot(name)
  pcall(function()
    local sf = assert(io.open(outdir .. name .. ".png", "wb"))
    sf:write(emu.takeScreenshot())
    sf:close()
  end)
end

local ok, err = pcall(function()
  emu.addMemoryCallback(function(a, v)
    if v ~= last88 then
      last88 = v
      log(string.format("f%06d STATE=%02X", frame, v))
      screenshot("st" .. string.format("%02X_f%06d", v, frame))
    end
  end, emu.callbackType.write, 0x0588, 0x0588, emu.memType.InternalRam)
  emu.addMemoryCallback(function(a, v)
    if v ~= last89 then
      last89 = v
      log(string.format("f%06d SUB=%02X", frame, v))
    end
  end, emu.callbackType.write, 0x0589, 0x0589, emu.memType.InternalRam)
end)
log("state+sub hooks -> " .. tostring(ok) .. " " .. tostring(err))

emu.addEventCallback(function()
  frame = frame + 1
  if frame % 60 == 0 then
    screenshot(string.format("t%06d", frame))
  end
end, emu.eventType.endFrame)
log("registered")
