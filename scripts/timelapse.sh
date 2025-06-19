#!/bin/zsh

C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_CYAN='\033[0;36m'
C_MAGENTA='\033[0;35m'
C_NONE='\033[0m'

_vd_usage() {
  echo "Usage: vd ${C_YELLOW}<input_file>${C_NONE} [-s ${C_YELLOW}<rate>${C_NONE}] [--yt] [-h|--help]"
  echo ""
  echo "  Creates a time-lapse video using FFmpeg."
  echo ""
  echo "  Arguments:"
  echo "    ${C_YELLOW}<input_file>${C_NONE}    The path to the source video file."
  echo ""
  echo "  Options:"
  echo "    -s, --speed ${C_YELLOW}<rate>${C_NONE}  The desired speedup rate (e.g., 60, 120, 240)."
  echo "                     (Default: 120)"
  echo "    --yt        ${C_MAGENTA}Use YouTube quality preset (slower, CPU-based encode).${C_NONE}"
  echo "                     (Default: Use fast hardware encoding)"
  echo "    -h, --help       Display this help and exit."
  echo ""
  echo "  Example:"
  echo "    ${C_CYAN}# Process using fast hardware encoding (default)${C_NONE}"
  echo "    vd my_video.mov -s 240"
  echo ""
  echo "    ${C_CYAN}# Process using YouTube quality preset${C_NONE}"
  echo "    vd my_video.mov --yt"
}

main() {
  local inputFile=""
  local speedupRate=120
  local useYoutubePreset=false

  while (( "$#" )); do
    case "$1" in
      -h|--help)
        _vd_usage
        return 0
        ;;
      -s|--speed)
        if [[ -n "$2" && "$2" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
          speedupRate="$2"
          shift 2
        else
          echo "${C_RED}Error: '$1' flag requires a numeric speedup rate.${C_NONE}" >&2
          _vd_usage
          return 1
        fi
        ;;
      --yt)
        useYoutubePreset=true
        shift
        ;;
      -*)
        echo "${C_RED}Error: Unknown flag '$1'${C_NONE}" >&2
        _vd_usage
        return 1
        ;;
      *)
        if [[ -z "$inputFile" ]]; then
          inputFile="$1"
          shift
        else
          echo "${C_RED}Error: Multiple input files specified.${C_NONE}" >&2
          return 1
        fi
        ;;
    esac
  done

  if [[ -z "$inputFile" ]]; then
    _vd_usage
    return 0
  fi
  
  if ! command -v ffmpeg &> /dev/null; then
    echo "${C_RED}Error: ffmpeg is not installed or not in your PATH.${C_NONE}" >&2
    return 1
  fi

  if [[ ! -f "$inputFile" ]]; then
    echo "${C_RED}Error: Input file not found: '$inputFile'${C_NONE}" >&2
    return 1
  fi

  local encoder_opts
  local output_suffix

  if [[ "$useYoutubePreset" == true ]]; then
    echo "${C_MAGENTA}Mode: YouTube Quality (x264 Software)${C_NONE}"
    encoder_opts=("-c:v" "libx264" "-crf" "22" "-preset" "medium")
    output_suffix="-${speedupRate}-yt-lapse"
  else
    echo "${C_CYAN}Mode: Hardware Accelerated${C_NONE}"
    encoder_opts=("-c:v" "h264_videotoolbox" "-b:v" "15M" "-profile:v" "high")
    output_suffix="-${speedupRate}-lapse"
  fi
  
  local filenameWithoutExt="${inputFile%.*}"
  local extension="${inputFile##*.}"
  local outputFile="${filenameWithoutExt}${output_suffix}.${extension}"

  echo "  - ${C_YELLOW}Input File:${C_NONE}   $inputFile"
  echo "  - ${C_YELLOW}Speedup Rate:${C_NONE} ${speedupRate}x"
  echo "  - ${C_YELLOW}Output File:${C_NONE}  $outputFile"
  echo ""

  ffmpeg -i "$inputFile" -vf "setpts=PTS/${speedupRate}" "${encoder_opts[@]}" -r 60 -an "$outputFile"

  if [[ $? -eq 0 ]]; then
    echo "\n${C_GREEN}Success! Time-lapse saved to '$outputFile'${C_NONE}"
  else
    echo "\n${C_RED}Error: FFmpeg failed to process the video.${C_NONE}" >&2
    return 1
  fi
}

main "$@"
