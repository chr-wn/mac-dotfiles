#!/bin/bash
# Helper script to generate and apply wallpaper-based themes
# Works with dotfiles + stow setup

set -e

# Configuration
DOTFILES_ROOT="$HOME/dotfiles"
KITTY_THEMES_DIR="$DOTFILES_ROOT/kitty/.config/kitty/themes"
KITTY_CURRENT="$DOTFILES_ROOT/kitty/.config/kitty/current-theme.conf"
TMUX_THEMES_DIR="$DOTFILES_ROOT/tmux/.config/tmux/themes"
TMUX_CURRENT="$DOTFILES_ROOT/tmux/.config/tmux/current-theme.conf"
NVIM_COLORS_DIR="$DOTFILES_ROOT/vim/.config/nvim/colors"

if [ -z "$1" ]; then
    echo "Usage: $0 <wallpaper_path> [theme_name]"
    echo "Example: $0 ~/wallpapers/ocean.jpg ocean"
    echo ""
    echo "This will:"
    echo "  1. Generate theme from wallpaper"
    echo "  2. Save to themes/ directory"
    echo "  3. Update current-theme.conf (auto-applied)"
    exit 1
fi

WALLPAPER="$1"
THEME_NAME="${2:-$(basename "$WALLPAPER" | sed 's/\.[^.]*$//')}"

echo "🎨 Generating themes from: $WALLPAPER"
echo "📝 Theme name: $THEME_NAME"
echo ""

# Create theme directories if they don't exist
mkdir -p "$KITTY_THEMES_DIR"
mkdir -p "$TMUX_THEMES_DIR"
mkdir -p "$NVIM_COLORS_DIR"

# Generate all themes
python3 "$(dirname "$0")/generate_palette.py" "$WALLPAPER" --all --theme-name "$THEME_NAME"

echo ""
echo "📦 Installing themes..."

# Install Kitty theme
if [ -f "colors-wallpaper.conf" ]; then
    # Save to themes collection
    cp colors-wallpaper.conf "$KITTY_THEMES_DIR/${THEME_NAME}.conf"
    # Update current theme (this is what kitty.conf includes)
    cp colors-wallpaper.conf "$KITTY_CURRENT"
    echo "  ✓ Kitty theme saved to themes/${THEME_NAME}.conf"
    echo "  ✓ Updated current-theme.conf"
    
    # Reload kitty if running
    if command -v kitty &> /dev/null; then
        kitty @ load-config 2>/dev/null && echo "  ✓ Kitty reloaded" || echo "  ℹ Restart kitty to apply"
    fi
fi

# Install Tmux theme
if [ -f "colors-wallpaper.tmux.conf" ]; then
    # Save to themes collection
    cp colors-wallpaper.tmux.conf "$TMUX_THEMES_DIR/${THEME_NAME}.tmux.conf"
    # Update current theme (this is what tmux.conf sources)
    cp colors-wallpaper.tmux.conf "$TMUX_CURRENT"
    echo "  ✓ Tmux theme saved to themes/${THEME_NAME}.tmux.conf"
    echo "  ✓ Updated current-theme.conf"
    
    # Reload tmux if running
    if command -v tmux &> /dev/null && tmux info &> /dev/null; then
        tmux source-file "$TMUX_CURRENT" 2>/dev/null && echo "  ✓ Tmux reloaded" || true
    fi
fi

# Install Neovim theme
if [ -f "${THEME_NAME}.vim" ]; then
    cp "${THEME_NAME}.vim" "$NVIM_COLORS_DIR/"
    echo "  ✓ Neovim theme saved to colors/${THEME_NAME}.vim"
    echo "  ℹ For NvChad: May need custom integration (see below)"
fi

echo ""
echo "🎉 Theme applied successfully!"
echo ""
echo "📁 Theme files saved:"
echo "  Kitty:  $KITTY_THEMES_DIR/${THEME_NAME}.conf"
echo "  Tmux:   $TMUX_THEMES_DIR/${THEME_NAME}.tmux.conf"
echo "  Neovim: $NVIM_COLORS_DIR/${THEME_NAME}.vim"
echo ""
echo "🔄 To switch back to this theme later:"
echo "  cp $KITTY_THEMES_DIR/${THEME_NAME}.conf $KITTY_CURRENT"
echo "  cp $TMUX_THEMES_DIR/${THEME_NAME}.tmux.conf $TMUX_CURRENT"
echo ""
echo "📋 One-time setup (if not done):"
echo ""
echo "Kitty (~/dotfiles/kitty/.config/kitty/kitty.conf):"
echo "  include current-theme.conf"
echo ""
echo "Tmux (~/dotfiles/tmux/.config/tmux/tmux.conf):"
echo "  source-file ~/.config/tmux/current-theme.conf"
echo ""
echo "Neovim with NvChad:"
echo "  Standard vim colorscheme should work: :colorscheme ${THEME_NAME}"
echo "  Or add to chadrc.lua: M.ui = { theme = '${THEME_NAME}' }"
