#!/usr/bin/env python3
"""
Self-contained robust color palette generator from wallpaper images.
Creates a virtual environment and installs dependencies automatically.
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path

# Script configuration
SCRIPT_DIR = Path(__file__).parent
VENV_DIR = SCRIPT_DIR / "palette_venv"
REQUIREMENTS = [
    "Pillow>=10.0.0",
    "scikit-learn>=1.3.0",
    "numpy>=1.24.0"
]

def hex_to_rgb(hex_color):
    """Convert hex string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_luminance(rgb):
    """Calculate relative luminance of RGB color."""
    r, g, b = [x/255.0 for x in rgb]
    r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
    g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
    b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def get_contrast_ratio(rgb1, rgb2):
    """Calculate WCAG contrast ratio between two colors."""
    lum1 = get_luminance(rgb1)
    lum2 = get_luminance(rgb2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

def run_command(cmd, check=True, capture_output=False):
    """Run a command with proper error handling."""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        if capture_output and e.stdout:
            print(f"Stdout: {e.stdout}")
        if capture_output and e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def setup_venv():
    """Create and setup virtual environment with required packages."""
    print("Setting up virtual environment...")
    
    # Create venv if it doesn't exist
    if not VENV_DIR.exists():
        print(f"Creating virtual environment at {VENV_DIR}")
        if not run_command(f"python3 -m venv {VENV_DIR}"):
            print("Failed to create virtual environment")
            return False
    
    # Determine activation script path
    if sys.platform == "win32":
        activate_script = VENV_DIR / "Scripts" / "activate"
        pip_path = VENV_DIR / "Scripts" / "pip"
    else:
        activate_script = VENV_DIR / "bin" / "activate"
        pip_path = VENV_DIR / "bin" / "pip"
    
    # Install requirements
    print("Installing required packages...")
    for req in REQUIREMENTS:
        print(f"Installing {req}...")
        if not run_command(f"{pip_path} install {req}"):
            print(f"Failed to install {req}")
            return False
    
    print("✓ Virtual environment setup complete")
    return True

def get_venv_python():
    """Get the path to the Python executable in the virtual environment."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    else:
        return VENV_DIR / "bin" / "python"

def extract_colors_script():
    """Return the color extraction script as a string."""
    return '''
import sys
import json
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string."""
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def hex_to_rgb(hex_color):
    """Convert hex string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def hex_to_rgb(hex_color):
    """Convert hex string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_contrast_ratio(rgb1, rgb2):
    """Calculate WCAG contrast ratio between two colors."""
    def get_lum(rgb):
        r, g, b = [x/255.0 for x in rgb]
        r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
        g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
        b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    lum1 = get_lum(rgb1)
    lum2 = get_lum(rgb2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

def adjust_color_for_contrast(color, background, target_ratio=4.5, lighten=True):
    """Adjust a color to meet minimum contrast ratio with background."""
    current_ratio = get_contrast_ratio(color, background)
    if current_ratio >= target_ratio:
        return color
    
    adjusted = list(color)
    step = 128
    direction = 1 if lighten else -1
    
    for _ in range(8):
        test_color = tuple(max(0, min(255, c + direction * step)) for c in adjusted)
        ratio = get_contrast_ratio(test_color, background)
        
        if ratio >= target_ratio:
            adjusted = list(test_color)
            step //= 2
            direction *= -1
        else:
            step //= 2
    
    return tuple(max(0, min(255, c)) for c in adjusted)

def get_luminance(rgb):
    """Calculate relative luminance of RGB color."""
    r, g, b = [x/255.0 for x in rgb]
    # Apply gamma correction
    r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
    g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
    b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def get_contrast_ratio(rgb1, rgb2):
    """Calculate WCAG contrast ratio between two colors."""
    lum1 = get_luminance(rgb1)
    lum2 = get_luminance(rgb2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

def adjust_color_for_contrast(color, background, target_ratio=7.0, lighten=True):
    """Adjust a color to meet minimum contrast ratio with background."""
    current_ratio = get_contrast_ratio(color, background)
    if current_ratio >= target_ratio:
        return color
    
    # Binary search for the right adjustment
    adjusted = list(color)
    step = 128
    direction = 1 if lighten else -1
    
    for _ in range(8):  # 8 iterations for precision
        test_color = tuple(max(0, min(255, c + direction * step)) for c in adjusted)
        ratio = get_contrast_ratio(test_color, background)
        
        if ratio >= target_ratio:
            adjusted = list(test_color)
            step //= 2
            direction *= -1
        else:
            step //= 2
    
    return tuple(max(0, min(255, c)) for c in adjusted)

def ensure_readable_colors(colors, background, foreground):
    """Ensure all colors have good contrast with background."""
    # WCAG AA standard: 4.5:1 for normal text, 7:1 for AAA
    min_contrast = 4.5
    
    adjusted = {}
    for key, hex_color in colors.items():
        if key.startswith('color') or key == 'foreground':
            rgb = hex_to_rgb(hex_color)
            
            # Check contrast with background
            contrast = get_contrast_ratio(rgb, background)
            
            if contrast < min_contrast:
                # Adjust color to meet contrast requirement
                bg_lum = get_luminance(background)
                lighten = bg_lum < 0.5  # Lighten if background is dark
                
                adjusted_rgb = adjust_color_for_contrast(rgb, background, min_contrast, lighten)
                adjusted[key] = rgb_to_hex(adjusted_rgb)
            else:
                adjusted[key] = hex_color
        else:
            adjusted[key] = hex_color
    
    return adjusted

def is_too_similar(color1, color2, threshold=20):
    """Check if two colors are too similar."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    distance = ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2) ** 0.5
    return distance < threshold

def extract_palette(image_path, num_colors=16):
    """Extract color palette from image using K-means clustering."""
    try:
        # Load and process image
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize for faster processing
        image.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        data = np.array(image)
        data = data.reshape((-1, 3))
        
        # Remove pure black and white pixels (often artifacts)
        mask = ~((data.sum(axis=1) < 10) | (data.sum(axis=1) > 745))
        if mask.sum() > 0:
            data = data[mask]
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=min(num_colors, len(data)), random_state=42, n_init=10)
        kmeans.fit(data)
        
        # Get cluster centers (dominant colors)
        colors = kmeans.cluster_centers_.astype(int)
        
        # Sort by cluster size (most dominant first)
        labels = kmeans.labels_
        color_counts = [(np.sum(labels == i), colors[i]) for i in range(len(colors))]
        color_counts.sort(reverse=True, key=lambda x: x[0])
        
        # Extract just the colors
        palette = [color for count, color in color_counts]
        
        # Remove similar colors
        filtered_palette = []
        for color in palette:
            if not any(is_too_similar(color, existing) for existing in filtered_palette):
                filtered_palette.append(color)
                if len(filtered_palette) >= num_colors:
                    break
        
        return filtered_palette
        
    except Exception as e:
        print(f"Error extracting palette: {e}")
        return None

def ensure_readable_colors(colors, background):
    """Ensure all colors have good contrast with background."""
    min_contrast = 4.5
    
    adjusted = {}
    for key, hex_color in colors.items():
        if key.startswith('color') or key == 'foreground':
            rgb = hex_to_rgb(hex_color)
            contrast = get_contrast_ratio(rgb, background)
            
            if contrast < min_contrast:
                bg_lum = get_luminance(background)
                lighten = bg_lum < 0.5
                adjusted_rgb = adjust_color_for_contrast(rgb, background, min_contrast, lighten)
                adjusted[key] = rgb_to_hex(adjusted_rgb)
            else:
                adjusted[key] = hex_color
        else:
            adjusted[key] = hex_color
    
    return adjusted

def generate_terminal_colors(palette):
    """Generate a complete terminal color scheme from the palette."""
    if len(palette) < 2:
        print("Error: Need at least 2 colors in palette")
        return None
    
    # Sort colors by luminance
    palette_with_lum = [(color, get_luminance(color)) for color in palette]
    palette_with_lum.sort(key=lambda x: x[1])
    
    # Extract colors by luminance
    darkest = palette_with_lum[0][0]
    brightest = palette_with_lum[-1][0]
    
    # Find colors for different purposes
    background = darkest
    foreground = brightest
    
    # Helper to get color from palette or generate variant
    def get_color(idx, default_rgb, brighten=0):
        if idx < len(palette):
            base = palette[idx]
        else:
            # Generate from existing colors
            base = palette[idx % len(palette)]
        
        if brighten > 0:
            return tuple(min(255, c + brighten) for c in base)
        return base
    
    # Generate 16 colors for terminal
    colors = {
        # Standard colors (0-7)
        'color0': rgb_to_hex(background),  # black
        'color1': rgb_to_hex(get_color(1, (204, 102, 102))),  # red
        'color2': rgb_to_hex(get_color(2, (153, 204, 102))),  # green
        'color3': rgb_to_hex(get_color(3, (204, 204, 102))),  # yellow
        'color4': rgb_to_hex(get_color(4, (102, 153, 204))),  # blue
        'color5': rgb_to_hex(get_color(5, (204, 102, 204))),  # magenta
        'color6': rgb_to_hex(get_color(6, (102, 204, 204))),  # cyan
        'color7': rgb_to_hex(foreground),  # white
        
        # Bright colors (8-15) - brightened versions
        'color8': rgb_to_hex(tuple(min(255, c + 50) for c in background)),  # bright black
        'color9': rgb_to_hex(get_color(1, (255, 132, 132), brighten=30)),  # bright red
        'color10': rgb_to_hex(get_color(2, (183, 255, 132), brighten=30)),  # bright green
        'color11': rgb_to_hex(get_color(3, (255, 255, 132), brighten=30)),  # bright yellow
        'color12': rgb_to_hex(get_color(4, (132, 183, 255), brighten=30)),  # bright blue
        'color13': rgb_to_hex(get_color(5, (255, 132, 255), brighten=30)),  # bright magenta
        'color14': rgb_to_hex(get_color(6, (132, 255, 255), brighten=30)),  # bright cyan
        'color15': rgb_to_hex(tuple(min(255, c + 30) for c in foreground)),  # bright white
        
        # Special colors
        'background': rgb_to_hex(background),
        'foreground': rgb_to_hex(foreground),
        'cursor': rgb_to_hex(foreground),
        'cursor_text_color': rgb_to_hex(background),
        'selection_background': rgb_to_hex(tuple(min(255, c + 40) for c in background)),
        'selection_foreground': rgb_to_hex(foreground),
    }
    
    return colors

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_colors.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"Error: Image file '{image_path}' not found")
        sys.exit(1)
    
    print(f"Extracting colors from: {image_path}")
    
    # Extract palette
    palette = extract_palette(image_path)
    if not palette:
        print("Failed to extract color palette")
        sys.exit(1)
    
    print(f"Extracted {len(palette)} colors")
    
    # Generate terminal colors
    colors = generate_terminal_colors(palette)
    if not colors:
        print("Failed to generate terminal colors")
        sys.exit(1)
    
    # Ensure readable contrast
    background_rgb = hex_to_rgb(colors['background'])
    colors = ensure_readable_colors(colors, background_rgb)
    
    # Output results
    result = {
        'palette': [rgb_to_hex(color) for color in palette],
        'terminal_colors': colors
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
'''

def generate_kitty_config(colors):
    """Generate kitty configuration from colors."""
    config_lines = [
        "# Generated color scheme from wallpaper",
        "",
        f"background {colors['background']}",
        f"foreground {colors['foreground']}",
        f"cursor {colors['cursor']}",
        f"cursor_text_color {colors['cursor_text_color']}",
        f"selection_background {colors['selection_background']}",
        f"selection_foreground {colors['selection_foreground']}",
        "",
        "# Terminal colors"
    ]
    
    for i in range(16):
        config_lines.append(f"color{i} {colors[f'color{i}']}")
    
    return "\n".join(config_lines)

def generate_tmux_config(colors):
    """Generate tmux configuration from colors."""
    config_lines = [
        "# Generated tmux theme from wallpaper",
        "# Add to your ~/.tmux.conf or source this file",
        "",
        "# Clear any old deprecated settings (if they exist)",
        "set -gu status-bg",
        "set -gu status-fg",
        "",
        "# Status bar colors",
        f"set -g status-style 'bg={colors['background']} fg={colors['foreground']}'",
        f"set -g status-left-style 'bg={colors['color4']} fg={colors['background']}'",
        f"set -g status-right-style 'bg={colors['color8']} fg={colors['foreground']}'",
        "",
        "# Window status colors",
        f"set -g window-status-style 'bg={colors['background']} fg={colors['color7']}'",
        f"set -g window-status-current-style 'bg={colors['color4']} fg={colors['background']} bold'",
        f"set -g window-status-activity-style 'bg={colors['color1']} fg={colors['background']}'",
        "",
        "# Pane border colors",
        f"set -g pane-border-style 'fg={colors['color8']}'",
        f"set -g pane-active-border-style 'fg={colors['color4']}'",
        "",
        "# Message colors",
        f"set -g message-style 'bg={colors['color3']} fg={colors['background']}'",
        f"set -g message-command-style 'bg={colors['color3']} fg={colors['background']}'",
        "",
        "# Clock mode",
        f"set -g clock-mode-colour {colors['color4']}",
        "",
        "# Copy mode colors",
        f"set -g mode-style 'bg={colors['color4']} fg={colors['background']}'",
    ]
    
    return "\n".join(config_lines)

def generate_neovim_theme(colors, theme_name="wallpaper"):
    """Generate neovim/vim colorscheme from colors."""
    config_lines = [
        f'" Generated neovim theme from wallpaper',
        f'" Colorscheme: {theme_name}',
        "",
        "hi clear",
        "if exists('syntax_on')",
        "  syntax reset",
        "endif",
        "",
        f"let g:colors_name = '{theme_name}'",
        "set background=dark",
        "",
        "\" UI Elements",
        f"hi Normal guifg={colors['foreground']} guibg={colors['background']}",
        f"hi Cursor guifg={colors['cursor_text_color']} guibg={colors['cursor']}",
        f"hi CursorLine guibg={colors['color8']} gui=NONE",
        f"hi CursorLineNr guifg={colors['color3']} guibg={colors['color8']} gui=bold",
        f"hi LineNr guifg={colors['color8']} guibg={colors['background']}",
        f"hi Visual guifg={colors['selection_foreground']} guibg={colors['selection_background']}",
        f"hi VisualNOS guifg={colors['selection_foreground']} guibg={colors['selection_background']}",
        "",
        "\" Statusline",
        f"hi StatusLine guifg={colors['color0']} guibg={colors['color4']} gui=bold",
        f"hi StatusLineNC guifg={colors['color8']} guibg={colors['color0']} gui=NONE",
        f"hi VertSplit guifg={colors['color8']} guibg={colors['color0']} gui=NONE",
        "",
        "\" Tabs",
        f"hi TabLine guifg={colors['color7']} guibg={colors['color0']} gui=NONE",
        f"hi TabLineFill guifg={colors['color0']} guibg={colors['color0']} gui=NONE",
        f"hi TabLineSel guifg={colors['color0']} guibg={colors['color4']} gui=bold",
        "",
        "\" Search",
        f"hi Search guifg={colors['color0']} guibg={colors['color3']} gui=bold",
        f"hi IncSearch guifg={colors['color0']} guibg={colors['color1']} gui=bold",
        "",
        "\" Messages",
        f"hi ErrorMsg guifg={colors['color1']} guibg={colors['background']} gui=bold",
        f"hi WarningMsg guifg={colors['color3']} guibg={colors['background']} gui=bold",
        f"hi ModeMsg guifg={colors['color2']} guibg={colors['background']} gui=bold",
        f"hi MoreMsg guifg={colors['color2']} guibg={colors['background']} gui=bold",
        "",
        "\" Syntax Highlighting",
        f"hi Comment guifg={colors['color8']} gui=italic",
        f"hi Constant guifg={colors['color1']} gui=NONE",
        f"hi String guifg={colors['color2']} gui=NONE",
        f"hi Character guifg={colors['color2']} gui=NONE",
        f"hi Number guifg={colors['color5']} gui=NONE",
        f"hi Boolean guifg={colors['color5']} gui=NONE",
        f"hi Float guifg={colors['color5']} gui=NONE",
        "",
        f"hi Identifier guifg={colors['color4']} gui=NONE",
        f"hi Function guifg={colors['color4']} gui=bold",
        "",
        f"hi Statement guifg={colors['color3']} gui=bold",
        f"hi Conditional guifg={colors['color3']} gui=bold",
        f"hi Repeat guifg={colors['color3']} gui=bold",
        f"hi Label guifg={colors['color3']} gui=NONE",
        f"hi Operator guifg={colors['color7']} gui=NONE",
        f"hi Keyword guifg={colors['color3']} gui=bold",
        f"hi Exception guifg={colors['color1']} gui=bold",
        "",
        f"hi PreProc guifg={colors['color6']} gui=NONE",
        f"hi Include guifg={colors['color6']} gui=NONE",
        f"hi Define guifg={colors['color6']} gui=NONE",
        f"hi Macro guifg={colors['color6']} gui=NONE",
        f"hi PreCondit guifg={colors['color6']} gui=NONE",
        "",
        f"hi Type guifg={colors['color5']} gui=NONE",
        f"hi StorageClass guifg={colors['color5']} gui=bold",
        f"hi Structure guifg={colors['color5']} gui=NONE",
        f"hi Typedef guifg={colors['color5']} gui=NONE",
        "",
        f"hi Special guifg={colors['color6']} gui=NONE",
        f"hi SpecialChar guifg={colors['color1']} gui=NONE",
        f"hi Tag guifg={colors['color4']} gui=NONE",
        f"hi Delimiter guifg={colors['color7']} gui=NONE",
        f"hi SpecialComment guifg={colors['color8']} gui=italic",
        f"hi Debug guifg={colors['color1']} gui=NONE",
        "",
        f"hi Underlined guifg={colors['color4']} gui=underline",
        f"hi Error guifg={colors['color1']} guibg={colors['background']} gui=bold",
        f"hi Todo guifg={colors['color3']} guibg={colors['background']} gui=bold",
        "",
        "\" Diff",
        f"hi DiffAdd guifg={colors['color2']} guibg={colors['color0']} gui=NONE",
        f"hi DiffChange guifg={colors['color3']} guibg={colors['color0']} gui=NONE",
        f"hi DiffDelete guifg={colors['color1']} guibg={colors['color0']} gui=NONE",
        f"hi DiffText guifg={colors['color4']} guibg={colors['color0']} gui=bold",
        "",
        "\" Popup Menu",
        f"hi Pmenu guifg={colors['color7']} guibg={colors['color8']}",
        f"hi PmenuSel guifg={colors['color0']} guibg={colors['color4']} gui=bold",
        f"hi PmenuSbar guibg={colors['color8']}",
        f"hi PmenuThumb guibg={colors['color7']}",
    ]
    
    return "\n".join(config_lines)

def main():
    parser = argparse.ArgumentParser(description="Generate color palette from wallpaper")
    parser.add_argument("image_path", nargs='?', help="Path to wallpaper image")
    parser.add_argument("--output", "-o", help="Output file for kitty config", default="colors-wallpaper.conf")
    parser.add_argument("--colors", "-c", type=int, default=16, help="Number of colors to extract")
    parser.add_argument("--setup-only", action="store_true", help="Only setup virtual environment")
    parser.add_argument("--tmux", action="store_true", help="Generate tmux theme")
    parser.add_argument("--nvim", action="store_true", help="Generate neovim theme")
    parser.add_argument("--all", action="store_true", help="Generate all themes (kitty, tmux, nvim)")
    parser.add_argument("--theme-name", default="wallpaper", help="Theme name for neovim")
    
    args = parser.parse_args()
    
    # Setup virtual environment
    if not setup_venv():
        print("Failed to setup virtual environment")
        return 1
    
    if args.setup_only:
        print("Virtual environment setup complete")
        return 0
    
    if not args.image_path:
        print("Error: image_path is required")
        parser.print_help()
        return 1
    
    # Expand user path
    image_path = Path(args.image_path).expanduser()
    
    if not image_path.exists():
        print(f"Error: Image file '{image_path}' not found")
        return 1
    
    print(f"Generating color palette from: {image_path}")
    
    # Create temporary script file
    script_content = extract_colors_script()
    temp_script = SCRIPT_DIR / "temp_extract_colors.py"
    
    try:
        with open(temp_script, 'w') as f:
            f.write(script_content)
        
        # Run color extraction in virtual environment
        python_path = get_venv_python()
        result = run_command(f"{python_path} {temp_script} '{image_path}'", 
                           capture_output=True)
        
        if not result:
            print("Failed to extract colors")
            return 1
        
        # Parse results - extract JSON from output
        try:
            # Find JSON in output (starts with { and ends with })
            json_start = result.find('{')
            if json_start == -1:
                raise ValueError("No JSON found in output")
            json_str = result[json_start:]
            
            data = json.loads(json_str)
            colors = data['terminal_colors']
            palette = data['palette']
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse color extraction results: {e}")
            print(f"Raw output: {result}")
            return 1
        
        # Determine what to generate
        generate_all = args.all
        generate_kitty = not (args.tmux or args.nvim) or generate_all
        generate_tmux_theme = args.tmux or generate_all
        generate_nvim_theme = args.nvim or generate_all
        
        generated_files = []
        
        # Generate kitty config
        if generate_kitty:
            kitty_config = generate_kitty_config(colors)
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(kitty_config)
            generated_files.append(('Kitty', output_path))
        
        # Generate tmux config
        if generate_tmux_theme:
            tmux_config = generate_tmux_config(colors)
            tmux_path = Path("colors-wallpaper.tmux.conf")
            with open(tmux_path, 'w') as f:
                f.write(tmux_config)
            generated_files.append(('Tmux', tmux_path))
        
        # Generate neovim theme
        if generate_nvim_theme:
            nvim_config = generate_neovim_theme(colors, args.theme_name)
            nvim_path = Path(f"{args.theme_name}.vim")
            with open(nvim_path, 'w') as f:
                f.write(nvim_config)
            generated_files.append(('Neovim', nvim_path))
        
        print(f"✓ Extracted {len(palette)} colors from wallpaper")
        print(f"✓ Background: {colors['background']}")
        print(f"✓ Foreground: {colors['foreground']}")
        
        # Check contrast ratio
        bg_rgb = hex_to_rgb(colors['background'])
        fg_rgb = hex_to_rgb(colors['foreground'])
        contrast = get_contrast_ratio(bg_rgb, fg_rgb)
        print(f"✓ Contrast ratio: {contrast:.2f}:1 (WCAG {'AAA' if contrast >= 7 else 'AA' if contrast >= 4.5 else 'Fail'})")
        
        # Show palette preview
        print("\nColor palette:")
        for i, color in enumerate(palette[:8]):
            print(f"  {i+1}: {color}")
        
        print("\nGenerated files:")
        for theme_type, file_path in generated_files:
            print(f"  {theme_type}: {file_path}")
        
        # Show usage instructions
        if generate_kitty:
            print(f"\nKitty: Add to your kitty.conf:")
            print(f"  include {generated_files[0][1]}")
        
        if generate_tmux_theme:
            tmux_file = next(f[1] for f in generated_files if f[0] == 'Tmux')
            print(f"\nTmux: Add to your ~/.tmux.conf:")
            print(f"  source-file ~/{tmux_file}")
        
        if generate_nvim_theme:
            nvim_file = next(f[1] for f in generated_files if f[0] == 'Neovim')
            print(f"\nNeovim: Copy to ~/.config/nvim/colors/ and add to init.vim:")
            print(f"  colorscheme {args.theme_name}")
        
    finally:
        # Clean up temporary script
        if temp_script.exists():
            temp_script.unlink()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())