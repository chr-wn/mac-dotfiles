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
  
  -- nvim-ufo for better folding
  {
    'kevinhwang91/nvim-ufo',
    dependencies = {
      'kevinhwang91/promise-async'
    },
    event = "BufReadPost",
    config = function()
      -- Using ufo provider need remap `zR` and `zM`
      vim.keymap.set('n', 'zR', require('ufo').openAllFolds)
      vim.keymap.set('n', 'zM', require('ufo').closeAllFolds)
      vim.keymap.set('n', 'zr', require('ufo').openFoldsExceptKinds)
      vim.keymap.set('n', 'zm', require('ufo').closeFoldsWith)

      -- Option 1: coc.nvim as LSP client
      -- use {'nvim-treesitter/nvim-treesitter', run = ':TSUpdate'}
      require('ufo').setup({
        provider_selector = function(bufnr, filetype, buftype)
          return {'treesitter', 'indent'}
        end
      })
    end
  },

  -- vim-pencil for prose writing
  {
    'preservim/vim-pencil',
    ft = { 'markdown', 'text', 'tex' },
    config = function()
      vim.g['pencil#wrapModeDefault'] = 'soft'   -- default is 'soft' for prose
      vim.g['pencil#textwidth'] = 80             -- set textwidth for hard mode
      
      -- Auto-enable pencil for prose filetypes
      vim.api.nvim_create_autocmd("FileType", {
        pattern = { "markdown", "text", "tex" },
        callback = function()
          vim.cmd("PencilSoft")  -- Use soft wrap by default
          -- Turn off line numbers for prose to avoid the mismatch issue
          -- vim.opt_local.number = false
          -- vim.opt_local.relativenumber = false
        end,
      })
    end
  },

  -- zen-mode for distraction-free writing
  {
    'folke/zen-mode.nvim',
    cmd = "ZenMode",
    opts = {
      window = {
        width = 90,
        options = {
          number = false,
          relativenumber = false,
          cursorline = false,
          cursorcolumn = false,
          foldcolumn = "0",
          list = false,
        }
      },
      plugins = {
        options = {
          enabled = true,
          ruler = false,
          showcmd = false,
          laststatus = 0, -- turn off the statusline in zen mode
        },
        twilight = { enabled = false }, -- disable twilight (we don't have it)
        gitsigns = { enabled = false },
        tmux = { enabled = true }, -- disables the tmux statusline
        kitty = {
          enabled = false,
          font = "+4", -- font size increment
        },
      },
    }
  },
}
