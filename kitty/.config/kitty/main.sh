#!/bin/bash
# Generate and apply Kitty theme from wallpaper

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KITTY_THEMES_DIR="$SCRIPT_DIR/themes"
KITTY_CURRENT="$SCRIPT_DIR/current-theme.conf"

if [ -z "$1" ]; then
    echo "Usage: $0 <wallpaper_path> [theme_name]"
    echo "Example: $0 ~/wallpapers/ocean.jpg ocean"
    echo ""
    echo "This will:"
    echo "  1. Generate Kitty theme from wallpaper"
    echo "  2. Save to themes/ directory"
    echo "  3. Update current-theme.conf (auto-applied)"
    exit 1
fi

WALLPAPER="$1"
THEME_NAME="${2:-$(basename "$WALLPAPER" | sed 's/\.[^.]*$//')}"

echo "🎨 Generating Kitty theme from: $WALLPAPER"
echo "📝 Theme name: $THEME_NAME"
echo ""

# Create themes directory if it doesn't exist
mkdir -p "$KITTY_THEMES_DIR"

# Generate theme
python3 "$SCRIPT_DIR/generate_palette.py" "$WALLPAPER"

echo ""
echo "📦 Installing theme..."

# Check if temp theme was generated
if [ -f "$SCRIPT_DIR/_temp_theme.conf" ]; then
    # Save to themes collection
    cp "$SCRIPT_DIR/_temp_theme.conf" "$KITTY_THEMES_DIR/${THEME_NAME}.conf"
    # Update current theme (this is what kitty.conf includes)
    cp "$SCRIPT_DIR/_temp_theme.conf" "$KITTY_CURRENT"
    # Clean up temp file
    rm "$SCRIPT_DIR/_temp_theme.conf"
    
    echo "  ✓ Theme saved to themes/${THEME_NAME}.conf"
    echo "  ✓ Updated current-theme.conf"
    
    # # Reload kitty if running
    # if command -v kitty &> /dev/null; then
    #     kitty @ load-config 2>/dev/null && echo "  ✓ Kitty reloaded" || echo "  ℹ Restart kitty to apply"
    # fi
else
    echo "  ✗ Failed to generate theme"
    exit 1
fi

# Clean up any stray files from pip install
rm -f "$SCRIPT_DIR/"=*.* 2>/dev/null || true

echo ""
echo "🎉 Theme applied successfully!"
echo ""
echo "📁 Theme saved to: themes/${THEME_NAME}.conf"
echo ""
echo "🔄 To switch back to this theme later:"
echo "  ./switch_theme.sh ${THEME_NAME}"
