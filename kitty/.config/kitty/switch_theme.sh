#!/bin/bash
# Switch between saved Kitty themes

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KITTY_THEMES_DIR="$SCRIPT_DIR/themes"
KITTY_CURRENT="$SCRIPT_DIR/current-theme.conf"

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
        echo "  No themes found. Generate one with:"
        echo "  ./apply_wallpaper_theme.sh <wallpaper> <name>"
    fi
    echo ""
    echo "Usage: $0 <theme_name>"
    echo "Example: $0 ocean"
    exit 1
fi

THEME_NAME="$1"

if [ ! -f "$KITTY_THEMES_DIR/${THEME_NAME}.conf" ]; then
    echo "✗ Theme not found: $THEME_NAME"
    echo ""
    echo "Available themes:"
    for theme in "$KITTY_THEMES_DIR"/*.conf; do
        if [ -f "$theme" ]; then
            echo "  $(basename "$theme" .conf)"
        fi
    done
    exit 1
fi

echo "🔄 Switching to theme: $THEME_NAME"

cp "$KITTY_THEMES_DIR/${THEME_NAME}.conf" "$KITTY_CURRENT"
echo "  ✓ Updated current-theme.conf"

# # Reload kitty if running
# if command -v kitty &> /dev/null; then
#     kitty @ load-config 2>/dev/null && echo "  ✓ Kitty reloaded" || echo "  ℹ Restart kitty to apply"
# fi
#
# echo ""
# echo "🎉 Theme switched to: $THEME_NAME"
