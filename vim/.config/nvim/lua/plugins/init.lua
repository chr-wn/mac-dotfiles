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
        "clangd",
        "pyright",
        "black",
        "isort",
        "clang-format"
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
    dependencies = {
      "williamboman/mason.nvim",
    },
    event = { "BufReadPre", "BufNewFile" },
    config = function()
      require("nvchad.configs.lspconfig").defaults()
      require "configs.lspconfig"
      
      -- Python LSP configuration
      local lspconfig = require "lspconfig"
      local nvlsp = require "nvchad.configs.lspconfig"

      lspconfig.pyright.setup {
        on_attach = nvlsp.on_attach,
        on_init = nvlsp.on_init,
        capabilities = nvlsp.capabilities,
        settings = {
          python = {
            analysis = {
              autoSearchPaths = true,
              diagnosticMode = "workspace",
              useLibraryCodeForTypes = true,
              typeCheckingMode = "basic"
            }
          }
        }
      }
    end,
  },

  {
    'nvim-treesitter/nvim-treesitter',
  	opts = {
  		ensure_installed = {
  			"vim", "lua", "vimdoc",
       "html", "css", "cpp", "python"
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
