# Dotfiles Setup Guide

This guide shows how to integrate the wallpaper theme generator with your dotfiles + stow setup.

## Directory Structure

```
~/dotfiles/
├── kitty/.config/kitty/
│   ├── kitty.conf              # Your main config
│   ├── current-theme.conf      # Active theme (auto-updated)
│   ├── themes/                 # Theme collection
│   │   ├── ocean.conf
│   │   ├── forest.conf
│   │   └── waves.conf
│   ├── generate_palette.py     # Theme generator
│   ├── apply_wallpaper_theme.sh
│   └── switch_theme.sh
│
├── tmux/.config/tmux/
│   ├── tmux.conf               # Your main config
│   ├── current-theme.conf      # Active theme (auto-updated)
│   └── themes/                 # Theme collection
│       ├── ocean.tmux.conf
│       ├── forest.tmux.conf
│       └── waves.tmux.conf
│
└── vim/.config/nvim/
    └── colors/                 # Neovim colorschemes
        ├── ocean.vim
        ├── forest.vim
        └── waves.vim
```

## One-Time Setup

### 1. Kitty Configuration

Add this line to `~/dotfiles/kitty/.config/kitty/kitty.conf`:

```conf
# Wallpaper-based theme (auto-updated)
include current-theme.conf
```

That's it! The `current-theme.conf` file will be automatically updated when you apply a new theme.

### 2. Tmux Configuration

Add this line to `~/dotfiles/tmux/.config/tmux/tmux.conf`:

```conf
# Wallpaper-based theme (auto-updated)
source-file ~/.config/tmux/current-theme.conf
```

If your tmux.conf is in a different location, adjust the path accordingly.

### 3. Neovim with NvChad

NvChad has its own theme system, but standard vim colorschemes should still work:

**Option A: Use as regular colorscheme**
```vim
:colorscheme ocean
```

**Option B: Add to your chadrc.lua** (if you want it in NvChad's theme picker)

Create a custom theme integration in `~/.config/nvim/lua/custom/themes/ocean.lua`:

```lua
local M = {}

M.base_30 = {
  -- Colors will be extracted from the generated vim file
  -- This is optional - the .vim file works standalone
}

return M
```

**Option C: Just use the .vim file** (simplest)

The generated `.vim` files work as standard vim colorschemes. You can:
- Use `:colorscheme ocean` in nvim
- Add `vim.cmd('colorscheme ocean')` to your init.lua
- They won't appear in NvChad's `<leader>th` picker, but they'll work fine

## Usage

### Generate and Apply New Theme

```bash
cd ~/dotfiles/kitty/.config/kitty
./apply_wallpaper_theme.sh ~/wallpapers/ocean.jpg ocean
```

This will:
1. Generate theme from wallpaper
2. Save to `themes/ocean.conf` (kitty) and `themes/ocean.tmux.conf` (tmux)
3. Update `current-theme.conf` in both kitty and tmux
4. Auto-reload kitty and tmux if running
5. Save neovim colorscheme to `~/.config/nvim/colors/ocean.vim`

### Switch Between Existing Themes

```bash
# List available themes
./switch_theme.sh

# Switch to a theme
./switch_theme.sh ocean
```

This switches both kitty and tmux to the selected theme.

### Generate Multiple Themes

```bash
./apply_wallpaper_theme.sh ~/wallpapers/ocean.jpg ocean
./apply_wallpaper_theme.sh ~/wallpapers/forest.jpg forest
./apply_wallpaper_theme.sh ~/wallpapers/sunset.jpg sunset
./apply_wallpaper_theme.sh ~/wallpapers/waves.jpg waves
```

Now you have a collection of themes you can switch between!

## How It Works

### The Magic of current-theme.conf

Instead of modifying your main config files, we use an include/source pattern:

1. **kitty.conf** includes `current-theme.conf`
2. **tmux.conf** sources `current-theme.conf`
3. Scripts update `current-theme.conf` when you apply/switch themes
4. Your main configs never change!

### Theme Collection

All generated themes are saved to `themes/` directories:
- Kitty: `~/dotfiles/kitty/.config/kitty/themes/`
- Tmux: `~/dotfiles/tmux/.config/tmux/themes/`
- Neovim: `~/dotfiles/vim/.config/nvim/colors/`

You can switch between them anytime without regenerating.

## Stow Integration

Since everything is in your dotfiles, just stow as usual:

```bash
cd ~/dotfiles
stow kitty
stow tmux
stow vim
```

The `current-theme.conf` files will be symlinked to the right places:
- `~/.config/kitty/current-theme.conf`
- `~/.config/tmux/current-theme.conf`

## Advanced: Automatic Theme Switching

### Based on Wallpaper Changes

If you use a wallpaper changer, integrate it:

```bash
#!/bin/bash
# In your wallpaper change script

NEW_WALLPAPER="$1"
THEME_NAME=$(basename "$NEW_WALLPAPER" .jpg)

cd ~/dotfiles/kitty/.config/kitty
./apply_wallpaper_theme.sh "$NEW_WALLPAPER" "$THEME_NAME"
```

### Based on Time of Day

```bash
#!/bin/bash
# Switch themes based on time

HOUR=$(date +%H)

if [ $HOUR -ge 6 ] && [ $HOUR -lt 18 ]; then
    # Daytime: light theme
    ~/dotfiles/kitty/.config/kitty/switch_theme.sh beach
else
    # Nighttime: dark theme
    ~/dotfiles/kitty/.config/kitty/switch_theme.sh ocean
fi
```

## Troubleshooting

### Kitty doesn't reload automatically

```bash
kitty @ load-config
```

Or restart kitty.

### Tmux doesn't reload automatically

```bash
tmux source-file ~/.config/tmux/current-theme.conf
```

Or restart tmux.

### NvChad theme picker doesn't show custom themes

That's expected. NvChad's `<leader>th` only shows themes in its own format. Your generated themes work as standard vim colorschemes:

```vim
:colorscheme ocean
```

To add them to NvChad's picker, you'd need to convert them to NvChad's theme format (more complex).

### Themes not found after stow

Make sure you've stowed the packages:

```bash
cd ~/dotfiles
stow kitty
stow tmux
stow vim
```

### Want to edit a theme manually

Edit the file in `themes/` directory, then switch to it:

```bash
# Edit
vim ~/dotfiles/kitty/.config/kitty/themes/ocean.conf

# Apply
./switch_theme.sh ocean
```

## Example Workflow

```bash
# 1. Generate theme from current wallpaper
cd ~/dotfiles/kitty/.config/kitty
./apply_wallpaper_theme.sh ~/wallpapers/current.jpg current

# 2. Generate themes for different wallpapers
./apply_wallpaper_theme.sh ~/wallpapers/ocean.jpg ocean
./apply_wallpaper_theme.sh ~/wallpapers/forest.jpg forest

# 3. Switch between them
./switch_theme.sh ocean    # Ocean theme
./switch_theme.sh forest   # Forest theme
./switch_theme.sh current  # Back to current wallpaper

# 4. List all available themes
./switch_theme.sh
```

## Benefits of This Approach

✅ **Non-invasive**: Never modifies your main config files  
✅ **Reversible**: Easy to switch back to any theme  
✅ **Collection**: Build a library of themes over time  
✅ **Stow-friendly**: Works perfectly with dotfiles + stow  
✅ **Auto-reload**: Kitty and tmux reload automatically  
✅ **Organized**: All themes in dedicated directories  

## Quick Reference

```bash
# Generate new theme
./apply_wallpaper_theme.sh <wallpaper> <name>

# Switch theme
./switch_theme.sh <name>

# List themes
./switch_theme.sh

# Reload manually
kitty @ load-config
tmux source-file ~/.config/tmux/current-theme.conf
```
