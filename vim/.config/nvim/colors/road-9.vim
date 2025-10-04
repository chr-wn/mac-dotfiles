" Generated neovim theme from wallpaper
" Colorscheme: road-9

hi clear
if exists('syntax_on')
  syntax reset
endif

let g:colors_name = 'road-9'
set background=dark

" UI Elements
hi Normal guifg=#b88d85 guibg=#15191f
hi Cursor guifg=#15191f guibg=#b88d85
hi CursorLine guibg=#9ca0a6 gui=NONE
hi CursorLineNr guifg=#929db1 guibg=#9ca0a6 gui=bold
hi LineNr guifg=#9ca0a6 guibg=#15191f
hi Visual guifg=#b88d85 guibg=#3d4147
hi VisualNOS guifg=#b88d85 guibg=#3d4147

" Statusline
hi StatusLine guifg=#8a8e94 guibg=#a3a7b9 gui=bold
hi StatusLineNC guifg=#9ca0a6 guibg=#8a8e94 gui=NONE
hi VertSplit guifg=#9ca0a6 guibg=#8a8e94 gui=NONE

" Tabs
hi TabLine guifg=#b88d85 guibg=#8a8e94 gui=NONE
hi TabLineFill guifg=#8a8e94 guibg=#8a8e94 gui=NONE
hi TabLineSel guifg=#8a8e94 guibg=#a3a7b9 gui=bold

" Search
hi Search guifg=#8a8e94 guibg=#929db1 gui=bold
hi IncSearch guifg=#8a8e94 guibg=#8a929e gui=bold

" Messages
hi ErrorMsg guifg=#8a929e guibg=#15191f gui=bold
hi WarningMsg guifg=#929db1 guibg=#15191f gui=bold
hi ModeMsg guifg=#96a2b3 guibg=#15191f gui=bold
hi MoreMsg guifg=#96a2b3 guibg=#15191f gui=bold

" Syntax Highlighting
hi Comment guifg=#9ca0a6 gui=italic
hi Constant guifg=#8a929e gui=NONE
hi String guifg=#96a2b3 gui=NONE
hi Character guifg=#96a2b3 gui=NONE
hi Number guifg=#a09b9c gui=NONE
hi Boolean guifg=#a09b9c gui=NONE
hi Float guifg=#a09b9c gui=NONE

hi Identifier guifg=#a3a7b9 gui=NONE
hi Function guifg=#a3a7b9 gui=bold

hi Statement guifg=#929db1 gui=bold
hi Conditional guifg=#929db1 gui=bold
hi Repeat guifg=#929db1 gui=bold
hi Label guifg=#929db1 gui=NONE
hi Operator guifg=#b88d85 gui=NONE
hi Keyword guifg=#929db1 gui=bold
hi Exception guifg=#8a929e gui=bold

hi PreProc guifg=#9f9d9d gui=NONE
hi Include guifg=#9f9d9d gui=NONE
hi Define guifg=#9f9d9d gui=NONE
hi Macro guifg=#9f9d9d gui=NONE
hi PreCondit guifg=#9f9d9d gui=NONE

hi Type guifg=#a09b9c gui=NONE
hi StorageClass guifg=#a09b9c gui=bold
hi Structure guifg=#a09b9c gui=NONE
hi Typedef guifg=#a09b9c gui=NONE

hi Special guifg=#9f9d9d gui=NONE
hi SpecialChar guifg=#8a929e gui=NONE
hi Tag guifg=#a3a7b9 gui=NONE
hi Delimiter guifg=#b88d85 gui=NONE
hi SpecialComment guifg=#9ca0a6 gui=italic
hi Debug guifg=#8a929e gui=NONE

hi Underlined guifg=#a3a7b9 gui=underline
hi Error guifg=#8a929e guibg=#15191f gui=bold
hi Todo guifg=#929db1 guibg=#15191f gui=bold

" Diff
hi DiffAdd guifg=#96a2b3 guibg=#8a8e94 gui=NONE
hi DiffChange guifg=#929db1 guibg=#8a8e94 gui=NONE
hi DiffDelete guifg=#8a929e guibg=#8a8e94 gui=NONE
hi DiffText guifg=#a3a7b9 guibg=#8a8e94 gui=bold

" Popup Menu
hi Pmenu guifg=#b88d85 guibg=#9ca0a6
hi PmenuSel guifg=#8a8e94 guibg=#a3a7b9 gui=bold
hi PmenuSbar guibg=#9ca0a6
hi PmenuThumb guibg=#b88d85