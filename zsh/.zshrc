if [[ -f "/opt/homebrew/bin/brew" ]] then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Zinit
ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"

if [ ! -d "$ZINIT_HOME" ]; then
   mkdir -p "$(dirname $ZINIT_HOME)"
   git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi

source "${ZINIT_HOME}/zinit.zsh"

# Zsh plugins
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions
zinit light Aloxaf/fzf-tab

# Snippets
zinit snippet OMZL::git.zsh
zinit snippet OMZP::git
# zinit snippet OMZP::sudo
# zinit snippet OMZP::archlinux
# zinit snippet OMZP::aws
# zinit snippet OMZP::kubectl
# zinit snippet OMZP::kubectx
zinit snippet OMZP::command-not-found

# Load completions
autoload -Uz compinit && compinit

zinit cdreplay -q

# Specify Oh-My-Posh Config Path
if [ "$TERM_PROGRAM" != "Apple_Terminal" ]; then
  eval "$(oh-my-posh init zsh --config $HOME/.config/ohmyposh/zen.toml)"
fi

# Keybindings
bindkey -e
bindkey '^p' history-search-backward
bindkey '^n' history-search-forward
bindkey '^[w' kill-region

# History
HISTSIZE=5000
HISTFILE=~/.zsh_history
SAVEHIST=$HISTSIZE
HISTDUP=erase
setopt appendhistory
setopt sharehistory
setopt hist_ignore_space
setopt hist_ignore_all_dups
setopt hist_save_no_dups
setopt hist_ignore_dups
setopt hist_find_no_dups
unsetopt extended_history
unset HIST_STAMPS

# Completion styling
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'ls --color $realpath'
zstyle ':fzf-tab:complete:__zoxide_z:*' fzf-preview 'ls --color $realpath'

# Aliases
alias ls='ls --color'
alias vim='nvim'
alias c='clear'
l() {
  eza --long --all --header --icons --hyperlink -R --level="${1:-1}"
}
# alias cat='bat'
alias zed="open -na /Applications/Zed.app"

alias dp='python3 ~/code/cp/download_prob.py'
alias mp='~/code/cp/make_prob.sh'
touch() {
  if [[ "$1" == "grass" ]]; then
    echo 
    echo 
    echo "\|/          (__)"
    echo "     \`\\------(oo)"
    echo "       ||    (__)"
    echo "       ||w--||     \|/"
    echo "   \|/"
    echo 
    echo 
  else
    command touch "$@"
  fi
}

rf() {
  make run TARGET="${1%.*}"
}
rt() {
    local target="main"
    local tests=()
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target)
                shift
                target="${1%.*}"
                ;;
            -h|--help)
                echo "Usage: rt [-t|--target target] [test_cases...]"
                echo "  -t, --target    Specify target (default: main)"
                echo "  -h, --help      Show this help"
                echo "Examples:"
                echo "  rt sample1              # Run sample1 with main"
                echo "  rt -t other sample1     # Run sample1 with other target"
                echo "  rt sample1 sample2      # Run multiple samples"
                echo "  rt                      # Run all tests with main"
                return
                ;;
            *)
                tests+=("$1")
                ;;
        esac
        shift
    done

    if [ ${#tests[@]} -eq 0 ]; then
        make test TARGET="$target"
    else
        make test TARGET="$target" TESTS="${tests[*]}"
    fi
}
ri() {
  make interactive TARGET="${1%.*}"
}

# https://michaeluloth.com/neovim-switch-configs/
vv() {
  # Assumes all configs exist in directories named ~/.config/nvim-*
  local config=$(find ~/.config -maxdepth 1 -type d -name 'nvim-*' | fzf --prompt="Neovim Configs > " --height=~50% --layout=reverse --border --exit-0)
  
  # If I exit fzf without selecting a config, don't open Neovim
  [[ -z $config ]] && echo "No config selected" && return

  # Open Neovim with the selected config
  NVIM_APPNAME=$(basename "$config") nvim "$@"
}

# ------------------------------------------------------------------------------
# vd - Creates a high-quality time-lapse video from a source file using FFmpeg.
# ------------------------------------------------------------------------------
function vd() {
  # --- Colors for output ---
  local C_RED='\033[0;31m'
  local C_GREEN='\033[0;32m'
  local C_YELLOW='\033[0;33m'
  local C_CYAN='\033[0;36m'
  local C_NONE='\033[0m' # No Color

  # --- Help and Usage Information ---
  _vd_usage() {
    echo "Usage: vd ${C_YELLOW}<input_file>${C_NONE} [-s ${C_YELLOW}<rate>${C_NONE}] [-h|--help]"
    echo ""
    echo "  Creates a high-quality time-lapse video using FFmpeg."
    echo ""
    echo "  Arguments:"
    echo "    ${C_YELLOW}<input_file>${C_NONE}    The path to the source video file."
    echo ""
    echo "  Options:"
    echo "    -s, --speed ${C_YELLOW}<rate>${C_NONE}  The desired speedup rate (e.g., 60, 120, 240)."
    echo "                     (Default: 120)"
    echo "    -h, --help       Display this help and exit."
    echo ""
    echo "  Example:"
    echo "    ${C_CYAN}# Process a video with a 240x speedup${C_NONE}"
    echo "    vd my_video.mov -s 240"
    echo ""
    echo "    ${C_CYAN}# Process a video with the default 120x speedup${C_NONE}"
    echo "    vd another_video.mov"
  }

  # --- Argument Parsing ---
  if [[ "$1" == "-h" || "$1" == "--help" || $# -eq 0 ]]; then
    _vd_usage
    return 0
  fi

  local inputFile="$1"
  local speedupRate=120 # Default speedup rate

  # Check for the optional speed flag
  if [[ "$2" == "-s" || "$2" == "--speed" ]]; then
    # Check if a rate was actually provided after the flag
    if [[ -n "$3" && "$3" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
      speedupRate="$3"
    else
      echo "${C_RED}Error: The '-s' flag requires a numeric speedup rate.${C_NONE}" >&2
      _vd_usage
      return 1
    fi
  fi

  # --- Pre-flight Checks ---
  if ! command -v ffmpeg &> /dev/null; then
    echo "${C_RED}Error: ffmpeg is not installed or not in your PATH.${C_NONE}" >&2
    echo "Please install ffmpeg to use this function (e.g., 'brew install ffmpeg')." >&2
    return 1
  fi

  if [[ ! -f "$inputFile" ]]; then
    echo "${C_RED}Error: Input file not found: '$inputFile'${C_NONE}" >&2
    return 1
  fi

  # --- Filename Generation ---
  local filenameWithoutExt="${inputFile%.*}"
  local extension="${inputFile##*.}"
  local outputFile="${filenameWithoutExt}-${speedupRate}-lapse.${extension}"

  # --- Execution ---
  echo "${C_CYAN}Processing Video...${C_NONE}"
  echo "  - ${C_YELLOW}Input File:${C_NONE}   $inputFile"
  echo "  - ${C_YELLOW}Speedup Rate:${C_NONE} ${speedupRate}x"
  echo "  - ${C_YELLOW}Output File:${C_NONE}  $outputFile"
  echo ""

  # The FFmpeg command, with robust quoting
  ffmpeg -i "$inputFile" -vf "setpts=PTS/${speedupRate}" -c:v libx264 -crf 17 -preset veryslow -r 60 -an "$outputFile"

  # --- Post-flight Check ---
  if [[ $? -eq 0 ]]; then
    echo "\n${C_GREEN}✅ Success! Time-lapse saved to '$outputFile'${C_NONE}"
  else
    echo "\n${C_RED}❌ Error: FFmpeg failed to process the video.${C_NONE}" >&2
    return 1
  fi
}

# Shell integrations
eval "$(fzf --zsh)"
eval "$(zoxide init --cmd cd zsh)"

# nvm
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"  # This loads nvm
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"  # This loads nvm bash_completion

# export JAVA_HOME=$(brew --prefix openjdk@23)
# export PATH=$JAVA_HOME/bin:$PATH

# Source the Lazyman shell initialization for aliases and nvims selector
# shellcheck source=.config/nvim-Lazyman/.lazymanrc
[ -f ~/.config/nvim-Lazyman/.lazymanrc ] && source ~/.config/nvim-Lazyman/.lazymanrc
# Source the Lazyman .nvimsbind for nvims key binding
# shellcheck source=.config/nvim-Lazyman/.nvimsbind
[ -f ~/.config/nvim-Lazyman/.nvimsbind ] && source ~/.config/nvim-Lazyman/.nvimsbind
