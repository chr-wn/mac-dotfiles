-- Simple test to check nvim config syntax
local success, result = pcall(function()
  -- Test loading the plugins config
  local plugins = dofile('.config/nvim/lua/plugins/init.lua')
  print("✓ Plugins config loaded successfully")
  print("✓ Found " .. #plugins .. " plugins configured")
  
  -- Check if nvim-ufo is in the config
  local ufo_found = false
  for i, plugin in ipairs(plugins) do
    if type(plugin) == "table" and plugin[1] == 'kevinhwang91/nvim-ufo' then
      ufo_found = true
      print("✓ nvim-ufo plugin found in configuration")
      break
    end
  end
  
  if not ufo_found then
    print("✗ nvim-ufo plugin not found")
  end
  
  return true
end)

if success then
  print("✓ Configuration test passed!")
else
  print("✗ Configuration test failed: " .. tostring(result))
end