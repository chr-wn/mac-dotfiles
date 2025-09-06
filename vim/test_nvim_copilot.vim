" Test Neovim script for Copilot
" This script can be run with: nvim -u test_nvim_copilot.vim

" Set up basic configuration
set nocompatible
set runtimepath+=.config/nvim

" Load the copilot plugin configuration
lua << EOF
-- Test if copilot config loads properly
local ok, copilot_config = pcall(require, 'configs.copilot')
if ok then
    print("✓ Copilot config loaded successfully")
    if copilot_config.filetypes and copilot_config.filetypes.python == true then
        print("✓ Python is enabled in filetypes")
    else
        print("✗ Python not enabled in filetypes")
    end
else
    print("✗ Failed to load copilot config:", copilot_config)
end
EOF

" Commands to test Copilot functionality
echo "Run these commands to test Copilot:"
echo ":Copilot status"
echo ":Copilot enable"
echo ":Copilot auth"