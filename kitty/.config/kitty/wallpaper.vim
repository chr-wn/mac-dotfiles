" Generated neovim theme from wallpaper
" Colorscheme: wallpaper

hi clear
if exists('syntax_on')
  syntax reset
endif

let g:colors_name = 'wallpaper'
set background=dark

" UI Elements
hi Normal guifg=#84a7bf guibg=#2e3440
hi Cursor guifg=#2e3440 guibg=#84a7bf
hi CursorLine guibg=#b5bbc7 gui=NONE
hi CursorLineNr guifg=#a6afc0 guibg=#b5bbc7 gui=bold
hi LineNr guifg=#b5bbc7 guibg=#2e3440
hi Visual guifg=#84a7bf guibg=#565c68
hi VisualNOS guifg=#84a7bf guibg=#565c68

" Statusline
hi StatusLine guifg=#a3a9b5 guibg=#b8d1d4 gui=bold
hi StatusLineNC guifg=#b5bbc7 guibg=#a3a9b5 gui=NONE
hi VertSplit guifg=#b5bbc7 guibg=#a3a9b5 gui=NONE

" Tabs
hi TabLine guifg=#84a7bf guibg=#a3a9b5 gui=NONE
hi TabLineFill guifg=#a3a9b5 guibg=#a3a9b5 gui=NONE
hi TabLineSel guifg=#a3a9b5 guibg=#b8d1d4 gui=bold

" Search
hi Search guifg=#a3a9b5 guibg=#a6afc0 gui=bold
hi IncSearch guifg=#a3a9b5 guibg=#84a7bf gui=bold

" Messages
hi ErrorMsg guifg=#84a7bf guibg=#2e3440 gui=bold
hi WarningMsg guifg=#a6afc0 guibg=#2e3440 gui=bold
hi ModeMsg guifg=#c8d4d4 guibg=#2e3440 gui=bold
hi MoreMsg guifg=#c8d4d4 guibg=#2e3440 gui=bold

" Syntax Highlighting
hi Comment guifg=#b5bbc7 gui=italic
hi Constant guifg=#84a7bf gui=NONE
hi String guifg=#c8d4d4 gui=NONE
hi Character guifg=#c8d4d4 gui=NONE
hi Number guifg=#b2c1d5 gui=NONE
hi Boolean guifg=#b2c1d5 gui=NONE
hi Float guifg=#b2c1d5 gui=NONE

hi Identifier guifg=#b8d1d4 gui=NONE
hi Function guifg=#b8d1d4 gui=bold

hi Statement guifg=#a6afc0 gui=bold
hi Conditional guifg=#a6afc0 gui=bold
hi Repeat guifg=#a6afc0 gui=bold
hi Label guifg=#a6afc0 gui=NONE
hi Operator guifg=#84a7bf gui=NONE
hi Keyword guifg=#a6afc0 gui=bold
hi Exception guifg=#84a7bf gui=bold

hi PreProc guifg=#aabed4 gui=NONE
hi Include guifg=#aabed4 gui=NONE
hi Define guifg=#aabed4 gui=NONE
hi Macro guifg=#aabed4 gui=NONE
hi PreCondit guifg=#aabed4 gui=NONE

hi Type guifg=#b2c1d5 gui=NONE
hi StorageClass guifg=#b2c1d5 gui=bold
hi Structure guifg=#b2c1d5 gui=NONE
hi Typedef guifg=#b2c1d5 gui=NONE

hi Special guifg=#aabed4 gui=NONE
hi SpecialChar guifg=#84a7bf gui=NONE
hi Tag guifg=#b8d1d4 gui=NONE
hi Delimiter guifg=#84a7bf gui=NONE
hi SpecialComment guifg=#b5bbc7 gui=italic
hi Debug guifg=#84a7bf gui=NONE

hi Underlined guifg=#b8d1d4 gui=underline
hi Error guifg=#84a7bf guibg=#2e3440 gui=bold
hi Todo guifg=#a6afc0 guibg=#2e3440 gui=bold

" Diff
hi DiffAdd guifg=#c8d4d4 guibg=#a3a9b5 gui=NONE
hi DiffChange guifg=#a6afc0 guibg=#a3a9b5 gui=NONE
hi DiffDelete guifg=#84a7bf guibg=#a3a9b5 gui=NONE
hi DiffText guifg=#b8d1d4 guibg=#a3a9b5 gui=bold

" Popup Menu
hi Pmenu guifg=#84a7bf guibg=#b5bbc7
hi PmenuSel guifg=#a3a9b5 guibg=#b8d1d4 gui=bold
hi PmenuSbar guibg=#b5bbc7
hi PmenuThumb guibg=#84a7bf