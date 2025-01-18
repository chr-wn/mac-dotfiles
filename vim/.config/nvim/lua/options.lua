require "nvchad.options"

-- add yours here!
vim.wo.relativenumber = true
vim.wo.number = true

vim.opt.scrolloff = 3

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
