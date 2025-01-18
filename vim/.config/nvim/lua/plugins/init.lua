return {
  {
    "kylechui/nvim-surround",
    version = "*", -- Use for stability; omit to use `main` branch for the latest features
    event = "VeryLazy",
    config = function()
        require("nvim-surround").setup({
            -- Configuration here, or leave empty to use defaults
        })
    end
  },
  {
    'numToStr/Comment.nvim',
    event = "BufReadPre",
    opts = require('configs.comment')
  },
  {
    "zbirenbaum/copilot.lua",
    cmd = "Copilot",
    event = "InsertEnter",
    opts = require('configs.copilot')
  },
  {
    "williamboman/mason.nvim",
    opts = {
      ensure_installed = {
        "clangd"
      }
    }
  },
  {
    "christoomey/vim-tmux-navigator",
    lazy=false,
  },
  {
    "stevearc/conform.nvim",
    -- event = 'BufWritePre', -- uncomment for format on save
    opts = require "configs.conform",
  },
  {
    "neovim/nvim-lspconfig",
    config = function()
      require "configs.lspconfig"
    end,
  },
  {
    'nvim-treesitter/nvim-treesitter',
  	opts = {
  		ensure_installed = {
  			"vim", "lua", "vimdoc",
       "html", "css", "cpp"
  		},
    },
    -- dependencies = {
    --     'nvim-treesitter/nvim-treesitter-refactor',
    -- },
    -- config = function()
    --     require'nvim-treesitter.configs'.setup {
    --         refactor = {
    --             highlight_definitions = { enable = true },
    --             smart_rename = {
    --                 enable = true,
    --                 keymaps = {
    --                     smart_rename = "<leader>rn",
    --                 },
    --             },
    --         },
    --     }
    -- end,
  },
}
