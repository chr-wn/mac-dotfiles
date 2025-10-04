#!/bin/bash
# Switch between saved themes

DOTFILES_ROOT="$HOME/dotfiles"
KITTY_THEMES_DIR="$DOTFILES_ROOT/kitty/.config/kitty/themes"
KITTY_CURRENT="$DOTFILES_ROOT/kitty/.config/kitty/current-theme.conf"
TMUX_THEMES_DIR="$DOTFILES_ROOT/tmux/.config/tmux/themes"
TMUX_CURRENT="$DOTFILES_ROOT/tmux/.config/tmux/current-theme.conf"

if [ -z "$1" ]; then
    echo "Available themes:"
    echo ""
    if [ -d "$KITTY_THEMES_DIR" ]; then
        for theme in "$KITTY_THEMES_DIR"/*.conf; do
            if [ -f "$theme" ]; then
                basename "$theme" .conf
            fi
        done
    else
        echo "  No themes found. Generate one with apply_wallpaper_theme.sh"
    fi
    echo ""
    echo "Usage: $0 <theme_name>"
    echo "Example: $0 ocean"
    exit 1
fi

THEME_NAME="$1"

echo "🔄 Switching to theme: $THEME_NAME"
echo ""

# Switch Kitty theme
if [ -f "$KITTY_THEMES_DIR/${THEME_NAME}.conf" ]; then
    cp "$KITTY_THEMES_DIR/${THEME_NAME}.conf" "$KITTY_CURRENT"
    echo "  ✓ Kitty theme switched"
    
    # Reload kitty if running
    if command -v kitty &> /dev/null; then
        kitty @ load-config 2>/dev/null && echo "  ✓ Kitty reloaded" || echo "  ℹ Restart kitty to apply"
    fi
else
    echo "  ✗ Kitty theme not found: $KITTY_THEMES_DIR/${THEME_NAME}.conf"
fi

# Switch Tmux theme
if [ -f "$TMUX_THEMES_DIR/${THEME_NAME}.tmux.conf" ]; then
    cp "$TMUX_THEMES_DIR/${THEME_NAME}.tmux.conf" "$TMUX_CURRENT"
    echo "  ✓ Tmux theme switched"
    
    # Reload tmux if running
    if command -v tmux &> /dev/null && tmux info &> /dev/null; then
        tmux source-file "$TMUX_CURRENT" 2>/dev/null && echo "  ✓ Tmux reloaded" || true
    fi
else
    echo "  ✗ Tmux theme not found: $TMUX_THEMES_DIR/${THEME_NAME}.tmux.conf"
fi

echo ""
echo "🎉 Theme switched to: $THEME_NAME"
