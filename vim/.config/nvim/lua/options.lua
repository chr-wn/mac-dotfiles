require "nvchad.options"

-- add yours here!
vim.wo.relativenumber = true
vim.wo.number = true

vim.opt.scrolloff = 3

-- Set 2-space indentation
vim.opt.tabstop = 2        -- Number of spaces that a <Tab> in the file counts for
vim.opt.shiftwidth = 2     -- Number of spaces to use for each step of (auto)indent
vim.opt.softtabstop = 2    -- Number of spaces that a <Tab> counts for while editing
vim.opt.expandtab = true   -- Use spaces instead of tabs

-- Force 2-space indentation for all filetypes (including Python)
vim.api.nvim_create_augroup('ForceIndentation', { clear = true })
vim.api.nvim_create_autocmd('FileType', {
  group = 'ForceIndentation',
  pattern = '*',
  callback = function()
    vim.bo.tabstop = 2
    vim.bo.shiftwidth = 2
    vim.bo.softtabstop = 2
    vim.bo.expandtab = true
  end,
})

-- Highlight on yank (native Neovim feature using Lua)
vim.api.nvim_create_augroup('YankHighlight', { clear = true })
vim.api.nvim_create_autocmd('TextYankPost', {
  group = 'YankHighlight',
  pattern = '*',
  callback = function()
    vim.highlight.on_yank({ higroup = 'IncSearch', timeout = 200 })
  end,
})

-- local o = vim.o
-- o.cursorlineopt ='both' -- to enable cursorline!
