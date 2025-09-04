local lspconfig = require "lspconfig"
local nvlsp = require "nvchad.configs.lspconfig"

-- Add folding capabilities for nvim-ufo
local capabilities = nvlsp.capabilities
capabilities.textDocument.foldingRange = {
  dynamicRegistration = false,
  lineFoldingOnly = true
}

-- EXAMPLE  
local servers = { "html", "cssls", "clangd" }

-- lsps with default config
for _, lsp in ipairs(servers) do
  lspconfig[lsp].setup {
    on_attach = nvlsp.on_attach,
    on_init = nvlsp.on_init,
    capabilities = capabilities,
     settings = {
      offset_encoding = "utf-16",
    }
  }
end



-- configuring single server, example: typescript
-- lspconfig.ts_ls.setup {
--   on_attach = nvlsp.on_attach,
--   on_init = nvlsp.on_init,
--   capabilities = nvlsp.capabilities,
-- }
