#!/bin/zsh

PID_FILE="/tmp/binaural_beats.pid"

stop_existing_process() {
  if [ ! -f "$PID_FILE" ]; then
    return 0
  fi
  
  local old_pid
  old_pid=$(cat "$PID_FILE")
  
  if ps -p "$old_pid" > /dev/null; then
    echo "Stopping previous instance (PID: $old_pid)..."
    kill "$old_pid"
    sleep 0.1
  fi
  
  rm "$PID_FILE"
}

launch_new_process() {
  local carrier=$1
  local beat=$2
  local volume=$3
  local profile_info=$4
  
  local right_freq
  right_freq=$(awk -v c="$carrier" -v b="$beat" 'BEGIN {print c+b}')

  echo "Starting: $profile_info"
  echo " • Carrier/Beat: ${carrier} Hz / ${beat} Hz"
  echo " • Volume: ${volume}"
  
  sox -q -n -c 2 -r 44100 -p synth -1 sine "$carrier" sine "$right_freq" remix 1 2 vol "$volume" | play -q - > /dev/null 2>&1 &
  
  local child_pid=$!
  echo "$child_pid" > "$PID_FILE"
  echo "Process running with PID $child_pid."
}


if ! command -v sox &> /dev/null; then
  echo "Error: SoX is not installed." >&2
  echo "Please install it with Homebrew: brew install sox" >&2
  exit 1
fi

if [[ "$1" == "stop" ]]; then
  stop_existing_process
  echo "Beats stopped."
  exit 0
fi

stop_existing_process

custom_carrier=""
custom_beat=""
custom_volume=""
PROFILE=""
declare -a flag_args=()

for arg in "$@"; do
  case "$arg" in
    1|2|3)
      if [[ -z "$PROFILE" ]]; then
        PROFILE="$arg"
      else
        flag_args+=("$arg")
      fi
      ;;
    *)
      flag_args+=("$arg")
      ;;
  esac
done

while getopts ":f:b:v:" opt "${flag_args[@]}"; do
  case $opt in
    f) custom_carrier="$OPTARG" ;;
    b) custom_beat="$OPTARG" ;;
    v) custom_volume="$OPTARG" ;;
    \?|:)
      echo "Usage: $0 [1|2|3|stop] | [-f carrier -b beat] [-v volume]" >&2
      exit 1
      ;;
  esac
done

if [[ -n "$custom_carrier" || -n "$custom_beat" ]]; then
  if [[ -n "$custom_carrier" && -n "$custom_beat" ]]; then
    final_volume=${custom_volume:-0.05}
    launch_new_process "$custom_carrier" "$custom_beat" "$final_volume" "Custom Frequencies"
  else
    echo "Error: You must specify both -f and -b flags together." >&2
    exit 1
  fi
else
  if [[ -z "$PROFILE" ]]; then
    PROFILE=1
  fi

  case "$PROFILE" in
    1)
      final_volume=${custom_volume:-0.005}
      launch_new_process 174 18 "$final_volume" "p1 (f)"
      ;;
    2)
      final_volume=${custom_volume:-0.004}
      launch_new_process 136.1 10 "$final_volume" "p2 (r)"
      ;;
    3)
      final_volume=${custom_volume:-0.004}
      launch_new_process 90 2.5 "$final_volume" "p3 (s)"
      ;;
    *) 
      echo "Error: Invalid profile. Use 1, 2, 3, or 'stop'." >&2
      exit 1
      ;;
  esac
fi
