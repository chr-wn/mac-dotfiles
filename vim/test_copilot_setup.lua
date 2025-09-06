-- Test script to verify Copilot configuration
local copilot_config = require('configs.copilot')

print("Copilot Configuration Test")
print("==========================")

-- Check if configuration loads without errors
if copilot_config then
    print("✓ Configuration loaded successfully")
    
    -- Check Python filetype setting
    if copilot_config.filetypes and copilot_config.filetypes.python == true then
        print("✓ Python filetype is explicitly enabled")
    else
        print("✗ Python filetype not properly configured")
    end
    
    -- Check if suggestion is enabled
    if copilot_config.suggestion and copilot_config.suggestion.enabled == true then
        print("✓ Suggestions are enabled")
    else
        print("✗ Suggestions not enabled")
    end
    
    -- Check if panel is enabled
    if copilot_config.panel and copilot_config.panel.enabled == true then
        print("✓ Panel is enabled")
    else
        print("✗ Panel not enabled")
    end
    
    -- Check Node.js command
    if copilot_config.copilot_node_command then
        print("✓ Node.js command configured: " .. copilot_config.copilot_node_command)
    else
        print("✗ Node.js command not configured")
    end
    
else
    print("✗ Failed to load configuration")
end

print("\nConfiguration Summary:")
for k, v in pairs(copilot_config) do
    if type(v) == "table" then
        print(k .. ": [table]")
    else
        print(k .. ": " .. tostring(v))
    end
end