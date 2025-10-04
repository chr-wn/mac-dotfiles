require "nvchad.options"

vim.wo.relativenumber = true
vim.wo.number = true

vim.opt.scrolloff = 3

-- nvim-ufo folding options
vim.o.foldcolumn = '1' -- '0' is not bad
vim.o.foldlevel = 99 -- Using ufo provider need a large value, feel free to decrease the value
vim.o.foldlevelstart = 99
vim.o.foldenable = true

-- -- Set 2-space indentation
-- vim.opt.tabstop = 2        -- Number of spaces that a <Tab> in the file counts for
-- vim.opt.shiftwidth = 2     -- Number of spaces to use for each step of (auto)indent
-- vim.opt.softtabstop = 2    -- Number of spaces that a <Tab> counts for while editing
-- vim.opt.expandtab = true   -- Use spaces instead of tabs

-- -- Force 2-space indentation for all filetypes (including Python)
-- vim.api.nvim_create_augroup('ForceIndentation', { clear = true })
-- vim.api.nvim_create_autocmd('FileType', {
--   group = 'ForceIndentation',
--   pattern = '*',
--   callback = function()
--     vim.bo.tabstop = 2
--     vim.bo.shiftwidth = 2
--     vim.bo.softtabstop = 2
--     vim.bo.expandtab = true
--   end,
-- })

-- Highlight on yank (native nvim)
vim.api.nvim_create_augroup('YankHighlight', { clear = true })
vim.api.nvim_create_autocmd('TextYankPost', {
  group = 'YankHighlight',
  pattern = '*',
  callback = function()
    vim.highlight.on_yank({ higroup = 'IncSearch', timeout = 200 })
  end,
})

-- Auto-reload kitty config on save
vim.api.nvim_create_augroup('KittyReload', { clear = true })
vim.api.nvim_create_autocmd('BufWritePost', {
  group = 'KittyReload',
  pattern = { 'kitty.conf', '*.conf' },
  callback = function()
    -- Check if the file is actually a kitty config file
    local filename = vim.fn.expand('%:t')
    local filepath = vim.fn.expand('%:p')
    if filename == 'kitty.conf' or filepath:match('kitty.*%.conf$') then
      vim.fn.system('kill -SIGUSR1 $(pgrep kitty)')
      vim.notify('Kitty config reloaded!', vim.log.levels.INFO)
    end
  end,
})

-- local o = vim.o
-- o.cursorlineopt ='both' -- to enable cursorline!
