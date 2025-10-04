# Wallpaper Theme Generator

Generate beautiful, readable terminal themes from your wallpapers with **WCAG-compliant contrast** for Kitty, Tmux, and Neovim.

## Quick Start

```bash
# Generate and apply theme from wallpaper
./apply_wallpaper_theme.sh ~/wallpapers/ocean.jpg ocean

# Switch between saved themes
./switch_theme.sh ocean
```

## Features

✅ **WCAG AA Compliant** - Minimum 4.5:1 contrast ratio (readable text)  
✅ **Multi-format** - Kitty, Tmux, and Neovim themes  
✅ **Theme Collection** - Save and switch between themes  
✅ **Auto-reload** - Kitty and Tmux reload automatically  
✅ **Dotfiles Friendly** - Works with stow and dotfiles repos  
✅ **Self-contained** - Manages its own virtual environment  

## One-Time Setup

### 1. Kitty

Add to `~/dotfiles/kitty/.config/kitty/kitty.conf`:
```conf
include current-theme.conf
```

### 2. Tmux

Add to `~/dotfiles/tmux/.config/tmux/tmux.conf`:
```conf
source-file ~/.config/tmux/current-theme.conf
```

### 3. Stow (if using)

```bash
cd ~/dotfiles
stow kitty
stow tmux
stow vim
```

## Usage

### Generate Theme from Wallpaper

```bash
./apply_wallpaper_theme.sh ~/wallpapers/ocean.jpg ocean
```

This will:
- Extract colors from wallpaper
- Adjust colors for WCAG AA contrast (4.5:1 minimum)
- Generate themes for Kitty, Tmux, and Neovim
- Save to `themes/` directories
- Update `current-theme.conf` (auto-applied)
- Reload Kitty and Tmux automatically

### Switch Between Themes

```bash
# List available themes
./switch_theme.sh

# Switch to a theme
./switch_theme.sh ocean
```

### Build a Theme Collection

```bash
./apply_wallpaper_theme.sh ~/wallpapers/ocean.jpg ocean
./apply_wallpaper_theme.sh ~/wallpapers/forest.jpg forest
./apply_wallpaper_theme.sh ~/wallpapers/sunset.jpg sunset
./apply_wallpaper_theme.sh ~/wallpapers/waves.jpg waves

# Now switch between them anytime
./switch_theme.sh forest
```

## Directory Structure

```
~/dotfiles/kitty/.config/kitty/
├── kitty.conf              # Add: include current-theme.conf
├── current-theme.conf      # Active theme (auto-updated)
├── themes/                 # Theme collection
│   ├── ocean.conf
│   ├── forest.conf
│   └── waves.conf
├── generate_palette.py     # Theme generator
├── apply_wallpaper_theme.sh
└── switch_theme.sh

~/dotfiles/tmux/.config/tmux/
├── tmux.conf               # Add: source-file ~/.config/tmux/current-theme.conf
├── current-theme.conf      # Active theme (auto-updated)
└── themes/
    ├── ocean.tmux.conf
    └── waves.tmux.conf

~/dotfiles/vim/.config/nvim/colors/
├── ocean.vim
└── waves.vim
```

## The Contrast Problem (Solved!)

Most wallpaper-to-theme tools (like pywal) extract colors without considering readability:

**Before (typical pywal):**
```
Background: #2e3440
Foreground: #3b4455
Contrast: 1.2:1 ❌ (unreadable!)
```

**After (this script):**
```
Background: #2e3440
Foreground: #84a7bf
Contrast: 4.91:1 ✅ (WCAG AA compliant!)
```

The script automatically adjusts colors to meet WCAG standards while preserving the wallpaper's aesthetic.

## Example Output

```bash
./apply_wallpaper_theme.sh ~/wallpapers/waves.jpg waves
```

```
🎨 Generating themes from: ~/wallpapers/waves.jpg
📝 Theme name: waves

✓ Extracted 7 colors from wallpaper
✓ Background: #2e3440
✓ Foreground: #84a7bf
✓ Contrast ratio: 4.91:1 (WCAG AA)

📦 Installing themes...
  ✓ Kitty theme saved to themes/waves.conf
  ✓ Updated current-theme.conf
  ✓ Kitty reloaded
  ✓ Tmux theme saved to themes/waves.tmux.conf
  ✓ Updated current-theme.conf
  ✓ Tmux reloaded
  ✓ Neovim theme saved to colors/waves.vim

🎉 Theme applied successfully!
```

## Scripts

- **generate_palette.py** - Core theme generator with contrast adjustment
- **apply_wallpaper_theme.sh** - Generate and apply theme from wallpaper
- **switch_theme.sh** - Switch between saved themes

## Documentation

- **QUICK_START.md** - Quick reference guide
- **DOTFILES_SETUP.md** - Detailed dotfiles integration
- **TMUX_SETUP.md** - Tmux-specific setup
- **CONTRAST_COMPARISON.md** - Contrast explanation and examples
- **README_PALETTE.md** - Technical details

## Requirements

- Python 3.6+
- Kitty terminal (optional)
- Tmux (optional)
- Neovim/Vim (optional)

Dependencies are auto-installed in a virtual environment on first run.

## Advanced Usage

### Custom Output Location

```bash
python3 generate_palette.py wallpaper.jpg -o custom-theme.conf
```

### Extract More Colors

```bash
./apply_wallpaper_theme.sh wallpaper.jpg theme --colors 32
```

### Generate Only Specific Formats

```bash
python3 generate_palette.py wallpaper.jpg --kitty  # Kitty only
python3 generate_palette.py wallpaper.jpg --tmux   # Tmux only
python3 generate_palette.py wallpaper.jpg --nvim   # Neovim only
python3 generate_palette.py wallpaper.jpg --all    # All formats
```

## NvChad Integration

The generated `.vim` files work as standard vim colorschemes:

```vim
:colorscheme waves
```

They won't appear in NvChad's `<leader>th` picker (which uses a different format), but they work fine as regular colorschemes.

## Why This Over Pywal?

| Feature | This Script | Pywal |
|---------|-------------|-------|
| Contrast adjustment | ✅ WCAG AA/AAA | ❌ No |
| Readable by default | ✅ Always | ❌ Often fails |
| Theme collection | ✅ Built-in | ⚠️ Manual |
| Dotfiles friendly | ✅ Yes | ⚠️ Requires setup |
| Contrast reporting | ✅ Shows ratio | ❌ No |
| Auto-reload | ✅ Yes | ✅ Yes |

## Troubleshooting

### Kitty not reloading
```bash
kitty @ load-config
```

### Tmux not reloading
```bash
tmux source-file ~/.config/tmux/current-theme.conf
```

### Low contrast warning
Try a wallpaper with more color variety, or extract more colors:
```bash
./apply_wallpaper_theme.sh wallpaper.jpg theme --colors 32
```

### Virtual environment issues
```bash
rm -rf palette_venv
./apply_wallpaper_theme.sh wallpaper.jpg theme  # Recreates venv
```

## License

MIT

## Credits

Uses K-means clustering for color extraction and WCAG 2.0 contrast formulas for readability.
