require "nvchad.mappings"

-- add yours here
local map = vim.keymap.set

-- Tmux key mappings
map("n", "<C-h>", "<cmd> TmuxNavigateLeft<CR>", { desc = "Navigate left in tmux" })
map("n", "<C-l>", "<cmd> TmuxNavigateRight<CR>", { desc = "Navigate right in tmux" })
map("n", "<C-j>", "<cmd> TmuxNavigateDown<CR>", { desc = "Navigate down in tmux" })
map("n", "<C-k>", "<cmd> TmuxNavigateUp<CR>", { desc = "Navigate up in tmux" })

-- map leader oe to open finder
map("n", "<leader>fe", ":!open .<CR>", { desc = "open finder" })
map("n", "<leader>ce", ":!pwd | pbcopy<CR>", { desc = "copy dir path" })

-- search files from home
map("n", "<leader>fc", function()
  require("telescope.builtin").find_files({ cwd = "~/code/cp" })
end, { desc = "telescope find cp" })

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

-- Zen mode toggle
-- map("n", "<leader>z", "<cmd>ZenMode<CR>", { desc = "Toggle zen mode" })

-- Prose writing mappings
map("n", "<leader>ps", "<cmd>PencilSoft<CR>", { desc = "Pencil soft wrap mode" })
map("n", "<leader>ph", "<cmd>PencilHard<CR>", { desc = "Pencil hard wrap mode" })
map("n", "<leader>pt", "<cmd>PencilToggle<CR>", { desc = "Toggle pencil mode" })

-- nvim-ufo folding keymaps
map('n', 'zR', function() require('ufo').openAllFolds() end, { desc = "Open all folds" })
map('n', 'zM', function() require('ufo').closeAllFolds() end, { desc = "Close all folds" })
map('n', 'zr', function() require('ufo').openFoldsExceptKinds() end, { desc = "Open folds except kinds" })
map('n', 'zm', function() require('ufo').closeFoldsWith() end, { desc = "Close folds with" })
map('n', 'zK', function()
  local winid = require('ufo').peekFoldedLinesUnderCursor()
  if not winid then
    vim.lsp.buf.hover()
  end
end, { desc = "Peek fold or hover" })

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

-- Format mappings
map("n", "<leader>fm", function()
  require("conform").format()
end, { desc = "Format file" })

-- LSP format mapping (backup) - only for servers that support formatting
map("n", "<leader>lf", function()
  local clients = vim.lsp.get_clients({ bufnr = 0 })
  local has_formatting = false
  
  for _, client in ipairs(clients) do
    if client.server_capabilities.documentFormattingProvider then
      has_formatting = true
      break
    end
  end
  
  if has_formatting then
    vim.lsp.buf.format()
  else
    -- Fallback to conform if LSP doesn't support formatting
    require("conform").format()
  end
end, { desc = "LSP Format file (with fallback)" })

-- Safe format mapping (isort only)
map("n", "<leader>fs", function()
  require("conform").format({ formatters = { "isort" } })
end, { desc = "Format imports only" })

-- vim.keymap.set('n', 's', '<NOP>')
-- vim.keymap.set('x', 's', '<NOP>')
-- vim.o.timeoutlen = 2000
-- vim.keymap.set({ "n", "x" }, "s", "<Nop>")

-- map("n", ";", ":", { desc = "CMD enter command mode" })
-- map("i", "jk", "<ESC>")  -- Uncomment for custom escape mapping

-- map({ "n", "i", "v" }, "<C-s>", "<cmd> w <cr>") -- Save shortcut

vim.keymap.set('n', '<leader>mr', '<cmd>RenderMarkdown toggle<cr>', { desc = 'Toggle Markdown Rendering' })
