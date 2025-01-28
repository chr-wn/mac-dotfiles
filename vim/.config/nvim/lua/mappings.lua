require "nvchad.mappings"

-- add yours here
local map = vim.keymap.set

-- Tmux key mappings
map("n", "<C-h>", "<cmd> TmuxNavigateLeft<CR>", { desc = "Navigate left in tmux" })
map("n", "<C-l>", "<cmd> TmuxNavigateRight<CR>", { desc = "Navigate right in tmux" })
map("n", "<C-j>", "<cmd> TmuxNavigateDown<CR>", { desc = "Navigate down in tmux" })
map("n", "<C-k>", "<cmd> TmuxNavigateUp<CR>", { desc = "Navigate up in tmux" })

-- map leader oe to open finder
map("n", "<leader>oe", ":!open .<CR>", { desc = "Open Finder" })

local opts = { noremap = true, silent = true }

-- vim.keymap.set('n', '[d', function() vim.diagnostic.goto_prev() end, opts)
-- vim.keymap.set('n', ']d', function() vim.diagnostic.goto_next() end, opts)

-- Open diagnostic float with <leader>df
map('n', '<leader>df', vim.diagnostic.open_float, opts)
vim.api.nvim_set_keymap('n', '<leader>rn', '<cmd>lua vim.lsp.buf.rename()<CR>', opts)

-- Add transparency toggle mapping
map("n", "<leader>tt", function()
  require("base46").toggle_transparency()
end, { desc = "Toggle transparency" })

-- Lua function to extract filename and call the `make` command
function RunMakeTarget()
    local file_path = vim.fn.expand('%:p')
    local file_dir = vim.fn.fnamemodify(file_path, ':h')
    local file_name = vim.fn.expand('%:t:r')
    local cmd = string.format("cd %s && make test TARGET=%s", file_dir, file_name)
    vim.cmd('!' .. cmd)
end

-- Mapping run file
map('n', '<leader>rt', ":w<CR>:lua RunMakeTarget()<CR>", { noremap = true, silent = true })

-- vim.keymap.set('n', 's', '<NOP>')
-- vim.keymap.set('x', 's', '<NOP>')
-- vim.o.timeoutlen = 2000
-- vim.keymap.set({ "n", "x" }, "s", "<Nop>")

-- map("n", ";", ":", { desc = "CMD enter command mode" })
-- map("i", "jk", "<ESC>")  -- Uncomment for custom escape mapping

-- map({ "n", "i", "v" }, "<C-s>", "<cmd> w <cr>") -- Save shortcut
