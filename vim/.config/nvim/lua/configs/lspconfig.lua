local nvlsp = require "nvchad.configs.lspconfig"

-- Add folding capabilities for nvim-ufo
local capabilities = vim.deepcopy(nvlsp.capabilities)
capabilities.textDocument.foldingRange = {
  dynamicRegistration = false,
  lineFoldingOnly = true
}

-- Common LSP configuration
local common_config = {
  on_attach = nvlsp.on_attach,
  on_init = nvlsp.on_init,
  capabilities = capabilities,
}

-- Configure LSP servers using new vim.lsp.config API
local servers = {
  html = {},
  cssls = {},
  clangd = {
    settings = {
      offset_encoding = "utf-16",
    }
  },
  pyright = {
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
}

-- Setup servers with new API
for server, config in pairs(servers) do
  local final_config = vim.tbl_deep_extend("force", common_config, config)
  vim.lsp.config[server] = final_config
end
