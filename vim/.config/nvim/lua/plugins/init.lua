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
       "html", "css", "cpp", "python", "markdown"
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

  -- -- vim-pencil for prose writing
  -- {
  --   'preservim/vim-pencil',
  --   ft = { 'markdown', 'text', 'tex' },
  --   config = function()
  --     vim.g['pencil#wrapModeDefault'] = 'soft'   -- default is 'soft' for prose
  --     vim.g['pencil#textwidth'] = 80             -- set textwidth for hard mode
  --     
  --     -- Auto-enable pencil for prose filetypes
  --     vim.api.nvim_create_autocmd("FileType", {
  --       pattern = { "markdown", "text", "tex" },
  --       callback = function()
  --         vim.cmd("PencilSoft")  -- Use soft wrap by default
  --         -- Turn off line numbers for prose to avoid the mismatch issue
  --         -- vim.opt_local.number = false
  --         -- vim.opt_local.relativenumber = false
  --       end,
  --     })
  --   end
  -- },
  --
  -- -- zen-mode for distraction-free writing
  -- {
  --   'folke/zen-mode.nvim',
  --   cmd = "ZenMode",
  --   opts = {
  --     window = {
  --       width = 90,
  --       options = {
  --         number = false,
  --         relativenumber = false,
  --         cursorline = false,
  --         cursorcolumn = false,
  --         foldcolumn = "0",
  --         list = false,
  --       }
  --     },
  --     plugins = {
  --       options = {
  --         enabled = true,
  --         ruler = false,
  --         showcmd = false,
  --         laststatus = 0, -- turn off the statusline in zen mode
  --       },
  --       twilight = { enabled = false }, -- disable twilight (we don't have it)
  --       gitsigns = { enabled = false },
  --       tmux = { enabled = true }, -- disables the tmux statusline
  --       kitty = {
  --         enabled = false,
  --         font = "+4", -- font size increment
  --       },
  --     },
  --   }
  -- },
  --
  -- -- render-markdown for beautiful markdown rendering
  -- {
  --   'MeanderingProgrammer/render-markdown.nvim',
  --   dependencies = { 'nvim-treesitter/nvim-treesitter', 'nvim-tree/nvim-web-devicons' },
  --   ft = { 'markdown' },
  --   opts = {
  --     -- Headings with different icons and highlights
  --     heading = {
  --       enabled = true,
  --       sign = true,
  --       icons = { '󰲡 ', '󰲣 ', '󰲥 ', '󰲧 ', '󰲩 ', '󰲫 ' },
  --     },
  --     -- Code blocks
  --     code = {
  --       enabled = true,
  --       sign = true,
  --       style = 'full',
  --       left_pad = 0,
  --       right_pad = 0,
  --     },
  --     -- Bullet points
  --     bullet = {
  --       enabled = false,
  --       -- icons = { '●', '○', '◆', '◇' },
  --     },
  --     -- Checkboxes
  --     checkbox = {
  --       enabled = true,
  --       unchecked = { icon = '󰄱 ' },
  --       checked = { icon = '󰱒 ' },
  --     },
  --     -- Quotes
  --     quote = {
  --       enabled = true,
  --       icon = '▋',
  --     },
  --     -- Tables
  --     pipe_table = {
  --       enabled = true,
  --       style = 'full',
  --     },
  --     -- Callouts (GitHub style)
  --     callout = {
  --       note = { raw = '[!NOTE]', rendered = '󰋽 Note', highlight = 'RenderMarkdownInfo' },
  --       tip = { raw = '[!TIP]', rendered = '󰌶 Tip', highlight = 'RenderMarkdownSuccess' },
  --       important = { raw = '[!IMPORTANT]', rendered = '󰅾 Important', highlight = 'RenderMarkdownHint' },
  --       warning = { raw = '[!WARNING]', rendered = '󰀪 Warning', highlight = 'RenderMarkdownWarn' },
  --       caution = { raw = '[!CAUTION]', rendered = '󰳦 Caution', highlight = 'RenderMarkdownError' },
  --     },
  --   },
  -- },

  -- autolist for automatic list continuation and formatting
  -- {
  --   'gaoDean/autolist.nvim',
  --   ft = { 'markdown', 'text', 'tex' },
  --   config = function()
  --     require('autolist').setup()
      
  --     -- Keybindings for list manipulation
  --     vim.keymap.set('i', '<tab>', '<cmd>AutolistTab<cr>')
  --     vim.keymap.set('i', '<s-tab>', '<cmd>AutolistShiftTab<cr>')
  --     vim.keymap.set('i', '<CR>', '<CR><cmd>AutolistNewBullet<cr>')
  --     vim.keymap.set('n', 'o', 'o<cmd>AutolistNewBullet<cr>')
  --     vim.keymap.set('n', 'O', 'O<cmd>AutolistNewBulletBefore<cr>')
  --     vim.keymap.set('n', '<CR>', '<cmd>AutolistToggleCheckbox<cr><CR>')
  --     vim.keymap.set('n', '<C-r>', '<cmd>AutolistRecalculate<cr>')
      
  --     -- Cycle list types with <C-t>
  --     vim.keymap.set('n', '<C-t>', '<cmd>AutolistCycleNext<cr>')
  --     -- vim.keymap.set('n', '<C-d>', '<cmd>AutolistCyclePrev<cr>')
      
  --     -- Move list items up/down
  --     vim.keymap.set('n', '<<', '<<<cmd>AutolistRecalculate<cr>')
  --     vim.keymap.set('n', '>>', '>><cmd>AutolistRecalculate<cr>')
  --     vim.keymap.set('n', 'dd', 'dd<cmd>AutolistRecalculate<cr>')
  --     vim.keymap.set('v', 'd', 'd<cmd>AutolistRecalculate<cr>')
  --   end,
  -- },

  -- bullets.vim for automatic bullet list formatting
  -- {
  --   'dkarter/bullets.vim',
  --   ft = { 'markdown', 'text', 'gitcommit', 'scratch' },
  --   config = function()
  --     vim.g.bullets_enabled_file_types = {
  --       'markdown',
  --       'text',
  --       'gitcommit',
  --       'scratch'
  --     }
  --     -- Disable default key mappings (we'll set them manually)
  --     vim.g.bullets_set_mappings = 0
  --     -- Enable renumbering of ordered lists
  --     vim.g.bullets_renumber_on_change = 1
  --     -- Enable nested bullets
  --     vim.g.bullets_nested_checkboxes = 1
  --     -- Checkbox symbols
  --     vim.g.bullets_checkbox_markers = ' .oOX'
  --     
  --     -- Set up keymaps manually for better control
  --     vim.api.nvim_create_autocmd("FileType", {
  --       pattern = { "markdown", "text", "gitcommit", "scratch" },
  --       callback = function()
  --         local opts = { buffer = true, silent = true }
  --         
  --         -- Insert mode mappings
  --         vim.keymap.set('i', '<CR>', '<Plug>(bullets-newline)', opts)
  --         vim.keymap.set('i', '<C-CR>', '<CR>', opts)  -- Ctrl+Enter for regular newline
  --         
  --         -- Indent/dedent in insert mode
  --         -- vim.keymap.set('i', '<C-]>', '<Plug>(bullets-demote)', opts)
  --         -- vim.keymap.set('i', '<C-[>', '<Plug>(bullets-promote)', opts)
  --         
  --         -- Normal mode mappings
  --         vim.keymap.set('n', 'o', '<Plug>(bullets-newline)', opts)
  --         
  --         -- Visual mode indent/dedent
  --         vim.keymap.set('v', '>', '<Plug>(bullets-demote)', opts)
  --         vim.keymap.set('v', '<', '<Plug>(bullets-promote)', opts)
  --         
  --         -- Checkbox toggle
  --         vim.keymap.set('n', '<leader>x', '<Plug> bullets-toggle-checkbox', opts)
  --         
  --         -- Renumber
  --         vim.keymap.set('n', '<leader>rn', ':RenumberList<CR>', opts)
  --       end,
  --     })
  --   end
  -- },

}
