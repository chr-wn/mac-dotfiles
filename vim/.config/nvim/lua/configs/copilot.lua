return {
  -- https://github.com/zbirenbaum/copilot.lua?tab=readme-ov-file#setup-and-configuration
  panel = {
    enabled = true,
    auto_refresh = true,
    keymap = {
      -- open = "<Leader>cp",  -- don't use <leader> key in insert mode (delay)
    },
    layout = { position = "right", ratio = 0.3 },
  },
  suggestion = {
    enabled = true,
    auto_trigger = false,
    keymap = {
      accept = "<C-f>",
      next = "<C-j>",
      prev = "<C-k>",
      dismiss = "<C-x>",
    },
  },
  filetypes = {
    python = true,  -- explicitly enable Python
  }
}