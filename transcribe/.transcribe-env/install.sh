#!/bin/bash
# Installation script for MP3 Transcription Tool

set -e  # Exit on any error

INSTALL_DIR="$HOME/.transcribe-env"
SCRIPT_NAME="transcribe.py"
ALIAS_NAME="transcribe"

echo "🎵 Installing MP3 Transcription Tool..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if virtual environment already exists
if [ -d "$INSTALL_DIR" ]; then
    echo "📁 Virtual environment already exists at $INSTALL_DIR"
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing installation..."
        rm -rf "$INSTALL_DIR"
    else
        echo "Installation cancelled."
        exit 0
    fi
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR"

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source "$INSTALL_DIR/bin/activate"
pip install --upgrade pip
pip install openai-whisper

# Copy the transcribe script
echo "📋 Installing transcription script..."
cp transcribe.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/transcribe.py"

# Set up shell alias
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    # Try to detect shell from $SHELL variable
    case "$SHELL" in
        */zsh)
            SHELL_RC="$HOME/.zshrc"
            ;;
        */bash)
            SHELL_RC="$HOME/.bashrc"
            ;;
        *)
            echo "⚠️  Could not detect shell type. Please manually add the following alias to your shell configuration:"
            echo "alias $ALIAS_NAME=\"$INSTALL_DIR/bin/python $INSTALL_DIR/$SCRIPT_NAME\""
            exit 0
            ;;
    esac
fi

# Add alias to shell configuration
ALIAS_LINE="alias $ALIAS_NAME=\"$INSTALL_DIR/bin/python $INSTALL_DIR/$SCRIPT_NAME\""

if [ -f "$SHELL_RC" ]; then
    # Check if alias already exists
    if grep -q "alias $ALIAS_NAME=" "$SHELL_RC"; then
        echo "🔄 Updating existing alias in $SHELL_RC"
        # Remove old alias and add new one
        grep -v "alias $ALIAS_NAME=" "$SHELL_RC" > "$SHELL_RC.tmp"
        mv "$SHELL_RC.tmp" "$SHELL_RC"
    else
        echo "➕ Adding alias to $SHELL_RC"
    fi
    
    echo "" >> "$SHELL_RC"
    echo "# MP3 Transcription Tool" >> "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
else
    echo "📝 Creating $SHELL_RC"
    echo "# MP3 Transcription Tool" > "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Summary:"
echo "  • Virtual environment: $INSTALL_DIR"
echo "  • Script location: $INSTALL_DIR/$SCRIPT_NAME"
echo "  • Shell alias: $ALIAS_NAME"
echo "  • Configuration: $SHELL_RC"
echo ""
echo "🚀 To start using the tool:"
echo "  1. Restart your terminal or run: source $SHELL_RC"
echo "  2. Test with: $ALIAS_NAME --help"
echo ""
echo "📖 Usage examples:"
echo "  $ALIAS_NAME audio.mp3                    # Basic transcription"
echo "  $ALIAS_NAME -t audio.mp3                 # With timestamps"
echo "  $ALIAS_NAME -o transcript.txt audio.mp3  # Custom output"
echo "  $ALIAS_NAME *.mp3                        # Batch processing"