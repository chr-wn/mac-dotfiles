local options = {
  formatters_by_ft = {
    lua = { "stylua" },
    python = { "isort", "black" },
    cpp = { "clang-format" },
    c = { "clang-format" },
    -- css = { "prettier" },
    -- html = { "prettier" },
  },

  -- Explicitly disable format on save
  format_on_save = false,
  
  formatters = {
    black = {
      prepend_args = { "--fast", "--line-length=88" },
    },
    ["clang-format"] = {
      prepend_args = { 
        "--style={BasedOnStyle: Google, IndentWidth: 2, TabWidth: 2, UseTab: Never}" 
      },
    },
    stylua = {
      prepend_args = { "--indent-type", "Spaces", "--indent-width", "2" },
    },
  },
}

return options
