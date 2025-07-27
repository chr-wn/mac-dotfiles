#!/usr/bin/env python3
"""
MP3 Transcription Tool (GPU Optimized)
A command-line tool for converting MP3 audio files to text transcripts using OpenAI's Whisper.
"""

import argparse
import sys
import os
import shutil
import time
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

import whisper
import torch
try:
    from mutagen import File as MutagenFile
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False


class ProgressSpinner:
    """Simple progress spinner for long-running operations."""
    
    def __init__(self, message: str = "Processing"):
        self.message = message
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the spinner in a separate thread."""
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the spinner."""
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the spinner line
        print("\r" + " " * (len(self.message) + 10) + "\r", end="", flush=True)
    
    def _spin(self):
        """Internal method to animate the spinner."""
        i = 0
        while self.running:
            char = self.spinner_chars[i % len(self.spinner_chars)]
            print(f"\r   {char} {self.message}...", end="", flush=True)
            time.sleep(0.1)
            i += 1


class TranscriptionError(Exception):
    """Custom exception for transcription-related errors."""
    pass


class ModelLoadError(TranscriptionError):
    """Exception raised when Whisper model fails to load."""
    pass


class FileOutputError(TranscriptionError):
    """Exception raised when file output operations fail."""
    pass


@dataclass
class TranscriptionResult:
    """Represents the result of a transcription operation."""
    text: str
    segments: List[Dict[str, Any]]  # For timestamp information
    language: str
    input_file: Path
    output_file: Path


@dataclass
class TranscriptionConfig:
    """Configuration settings for transcription operations."""
    model_name: str = 'base'
    include_timestamps: bool = False
    output_format: str = 'txt'
    batch_mode: bool = False
    custom_output: Optional[str] = None
    device: Optional[str] = None  # Auto-detect best device
    engine: str = 'auto'  # 'auto', 'original', 'faster'


class FileManager:
    """Handles file validation and output path generation."""
    
    SUPPORTED_EXTENSIONS = {'.mp3'}
    
    def get_audio_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get audio file information including duration and size.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with audio information
        """
        info = {
            'size_mb': file_path.stat().st_size / (1024 * 1024),
            'duration_seconds': None,
            'duration_formatted': None,
            'bitrate': None,
            'sample_rate': None
        }
        
        if MUTAGEN_AVAILABLE:
            try:
                audio_file = MutagenFile(file_path)
                if audio_file and hasattr(audio_file, 'info'):
                    if hasattr(audio_file.info, 'length'):
                        info['duration_seconds'] = audio_file.info.length
                        info['duration_formatted'] = self._format_duration(audio_file.info.length)
                    if hasattr(audio_file.info, 'bitrate'):
                        info['bitrate'] = audio_file.info.bitrate
                    if hasattr(audio_file.info, 'sample_rate'):
                        info['sample_rate'] = audio_file.info.sample_rate
            except Exception:
                # If we can't read metadata, continue without it
                pass
        
        return info
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in MM:SS or HH:MM:SS format."""
        if seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes:02d}:{secs:02d}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def validate_input_files(self, file_paths: List[str]) -> List[Path]:
        """
        Validates input files exist, are readable, and have correct format.
        
        Args:
            file_paths: List of file path strings
            
        Returns:
            List of validated Path objects
            
        Raises:
            FileNotFoundError: If any file doesn't exist
            ValueError: If any file has unsupported format or isn't readable
        """
        validated_files = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check if it's a file (not directory)
            if not path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            # Check file extension
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                raise ValueError(
                    f"Unsupported file format: {path.suffix}. "
                    f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
                )
            
            # Check if file is readable
            if not os.access(path, os.R_OK):
                raise ValueError(f"File is not readable: {file_path}")
            
            validated_files.append(path)
        
        return validated_files
    
    def generate_output_path(self, input_path: Path, custom_output: Optional[str] = None, 
                           model_name: Optional[str] = None, include_timestamps: bool = False) -> Path:
        """
        Generates appropriate output filename for a given input file.
        
        Args:
            input_path: Path to input MP3 file
            custom_output: Optional custom output filename
            model_name: Optional model name to append to filename
            include_timestamps: Whether timestamps are included (affects filename)
            
        Returns:
            Path object for output file
        """
        if custom_output:
            return Path(custom_output)
        
        # Build filename with suffixes: foo.mp3 -> foo-small-timestamps.txt
        stem = input_path.stem  # filename without extension
        suffixes = []
        
        if model_name:
            suffixes.append(model_name)
        
        if include_timestamps:
            suffixes.append("timestamps")
        
        if suffixes:
            suffix_str = "-" + "-".join(suffixes)
            return input_path.parent / f"{stem}{suffix_str}.txt"
        else:
            # Fallback to original behavior
            return input_path.with_suffix('.txt')
    
    def handle_batch_output_paths(self, input_paths: List[Path], 
                                custom_output: Optional[str] = None, model_name: Optional[str] = None,
                                include_timestamps: bool = False) -> List[Path]:
        """
        Handles output path generation for batch processing.
        
        Args:
            input_paths: List of input file paths
            custom_output: Optional custom output filename for concatenation
            model_name: Optional model name to append to filename
            include_timestamps: Whether timestamps are included (affects filename)
            
        Returns:
            List of output paths (single path if concatenating, multiple if separate files)
        """
        if custom_output:
            # Single output file for concatenation
            return [Path(custom_output)]
        else:
            # Separate output file for each input
            return [self.generate_output_path(path, model_name=model_name, include_timestamps=include_timestamps) for path in input_paths]


class AudioTranscriber:
    """Handles audio transcription using OpenAI's Whisper model with GPU acceleration."""
    
    def __init__(self, model_name: str = 'base', device: Optional[str] = None, engine: str = 'auto'):
        """
        Initialize the transcriber with a Whisper model.
        
        Args:
            model_name: Name of the Whisper model to use
            device: Device to use ('mps', 'cuda', 'cpu', or None for auto-detect)
            engine: Engine to use ('auto', 'original', 'faster')
        """
        self.model_name = model_name
        self.engine = self._choose_engine(engine)
        self.device = device or self._get_optimal_device()
        self.model = None
        self._load_model()
    
    def _choose_engine(self, engine: str) -> str:
        """Choose the best available engine."""
        if engine == 'auto':
            # Prefer faster-whisper if available, especially for MPS compatibility
            if FASTER_WHISPER_AVAILABLE:
                return 'faster'
            else:
                return 'original'
        elif engine == 'faster' and not FASTER_WHISPER_AVAILABLE:
            print("Warning: faster-whisper not available, falling back to original")
            return 'original'
        else:
            return engine
    
    def _get_optimal_device(self) -> str:
        """Determine the best device for transcription on this system."""
        # CUDA is most stable for Whisper
        if torch.cuda.is_available():
            return "cuda"  # NVIDIA GPU
        # For faster-whisper, we use CPU which works great
        elif self.engine == 'faster':
            return "cpu"  # Faster-whisper works well on CPU
        # MPS has some compatibility issues with original Whisper, but we'll try it with fallback
        elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
            return "mps"  # Apple Silicon GPU (with CPU fallback if needed)
        else:
            return "cpu"   # CPU fallback
    
    def _load_model(self):
        """Load the Whisper model with comprehensive error handling and hardware acceleration."""
        try:
            if self.engine == 'faster':
                self._load_faster_whisper_model()
            else:
                self._load_original_whisper_model()
        except Exception as e:
            raise ModelLoadError(f"Failed to load Whisper model '{self.model_name}': {e}")
    
    def _load_faster_whisper_model(self):
        """Load faster-whisper model."""
        print(f"Loading Faster-Whisper model '{self.model_name}' on CPU...")
        
        # Check available disk space for model download
        self._check_disk_space()
        
        # Faster-whisper uses CPU efficiently with different compute types
        compute_type = "int8"  # Good balance of speed and accuracy
        self.model = WhisperModel(self.model_name, device="cpu", compute_type=compute_type)
        print(f"Model '{self.model_name}' loaded successfully with Faster-Whisper (CPU, {compute_type})")
    
    def _load_original_whisper_model(self):
        """Load original OpenAI Whisper model."""
        original_device = self.device
        
        device_name = {
            "mps": "Apple Silicon GPU (Metal)",
            "cuda": "NVIDIA GPU (CUDA)", 
            "cpu": "CPU"
        }.get(self.device, self.device)
        
        print(f"Loading Whisper model '{self.model_name}' on {device_name}...")
        
        # Check available disk space for model download
        self._check_disk_space()
        
        try:
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"Model '{self.model_name}' loaded successfully on {device_name}")
        except Exception as e:
            # Check if it's an MPS compatibility issue
            if self.device == "mps" and ("sparse" in str(e).lower() or "mps" in str(e).lower()):
                print(f"Warning: MPS compatibility issue detected. Falling back to CPU...")
                self.device = "cpu"
                self.model = whisper.load_model(self.model_name, device=self.device)
                print(f"Model '{self.model_name}' loaded successfully on CPU (MPS fallback)")
            else:
                raise e
    
    def _check_disk_space(self):
        """Check if there's sufficient disk space for model download."""
        try:
            # Get available disk space
            _, _, free_bytes = shutil.disk_usage(Path.home())
            free_gb = free_bytes / (1024**3)
            
            # Model size estimates (approximate)
            model_sizes = {
                'tiny': 0.1,    # ~39MB
                'base': 0.2,    # ~74MB
                'small': 0.5,   # ~244MB
                'medium': 1.5,  # ~769MB
                'large': 3.0    # ~1550MB
            }
            
            required_gb = model_sizes.get(self.model_name, 1.0)
            
            if free_gb < required_gb + 0.5:  # Add 0.5GB buffer
                raise ModelLoadError(
                    f"Insufficient disk space. Model '{self.model_name}' requires ~{required_gb:.1f}GB, "
                    f"but only {free_gb:.1f}GB available. Please free up disk space."
                )
                
        except Exception:
            # If we can't check disk space, continue anyway
            pass  
  
    def transcribe_file(self, input_path: Path, include_timestamps: bool = False, verbose: bool = False) -> TranscriptionResult:
        """
        Transcribe a single audio file.
        
        Args:
            input_path: Path to the input audio file
            include_timestamps: Whether to include timestamp information
            verbose: Whether to show detailed progress information
            
        Returns:
            TranscriptionResult object containing transcription data
            
        Raises:
            TranscriptionError: If transcription fails
        """
        if not self.model:
            raise TranscriptionError("Model not loaded. Cannot perform transcription.")
        
        try:
            print(f"Transcribing: {input_path.name}")
            
            # Get audio file information
            # We need to access the file manager from the service, so let's pass it
            # For now, let's create a temporary FileManager instance
            temp_file_manager = FileManager()
            audio_info = temp_file_manager.get_audio_info(input_path)
            
            # Always show basic info (size and duration if available)
            size_info = f"{audio_info['size_mb']:.1f} MB"
            if audio_info['duration_formatted']:
                duration_info = f", {audio_info['duration_formatted']} duration"
                print(f"   File: {size_info}{duration_info}")
            else:
                print(f"   File: {size_info}")
            
            if verbose and audio_info['bitrate']:
                print(f"   Bitrate: {audio_info['bitrate']} kbps")
                if audio_info['sample_rate']:
                    print(f"   Sample rate: {audio_info['sample_rate']} Hz")
            
            start_time = time.time()
            
            # Show progress indicator during transcription
            spinner = None
            if not verbose:
                spinner = ProgressSpinner("Transcribing")
                spinner.start()
            elif verbose:
                print("   Starting transcription...")
            
            # Perform transcription based on engine
            if self.engine == 'faster':
                segments_iter, info = self.model.transcribe(str(input_path))
                
                # Convert faster-whisper format to original format
                text = ""
                segments = []
                for segment in segments_iter:
                    text += segment.text
                    if include_timestamps:
                        segments.append({
                            'start': segment.start,
                            'end': segment.end,
                            'text': segment.text
                        })
                
                language = info.language
                text = text.strip()
            else:
                # Original whisper
                result = self.model.transcribe(str(input_path))
                text = result['text'].strip()
                segments = result.get('segments', []) if include_timestamps else []
                language = result.get('language', 'unknown')
            
            # Stop spinner if it was running
            if spinner:
                spinner.stop()
            
            end_time = time.time()
            duration = end_time - start_time
            
            if verbose:
                print(f"\n   Transcription completed in {self._format_duration(duration)}")
            else:
                print(f"   Completed in {self._format_duration(duration)}")
            
            if verbose:
                print(f"   Language detected: {language}")
                print(f"   Text length: {len(text)} characters")
                if segments:
                    print(f"   Segments: {len(segments)}")
            
            return TranscriptionResult(
                text=text,
                segments=segments,
                language=language,
                input_file=input_path,
                output_file=Path()  # Will be set by caller
            )
            
        except Exception as e:
            raise TranscriptionError(f"Failed to transcribe {input_path.name}: {e}")
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in a human-readable way."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}h {minutes}m {secs:.1f}s"


class TranscriptionService:
    """Main service class that orchestrates the transcription process."""
    
    def __init__(self, config: TranscriptionConfig, verbose: bool = False):
        """Initialize the transcription service with configuration."""
        self.config = config
        self.verbose = verbose
        self.file_manager = FileManager()
        self.transcriber = AudioTranscriber(config.model_name, config.device, config.engine)
    
    def process_files(self, input_files: List[str]) -> List[TranscriptionResult]:
        """
        Process multiple audio files for transcription.
        
        Args:
            input_files: List of input file paths
            
        Returns:
            List of TranscriptionResult objects
            
        Raises:
            Various exceptions for file validation and transcription errors
        """
        overall_start_time = time.time()
        
        # Validate input files
        validated_files = self.file_manager.validate_input_files(input_files)
        
        if self.verbose:
            print(f"\nProcessing {len(validated_files)} file(s) with {self.config.model_name} model")
            total_size = sum(f.stat().st_size for f in validated_files) / (1024 * 1024)
            print(f"Total size: {total_size:.1f} MB")
            print()
        
        # Generate output paths
        if self.config.batch_mode and self.config.custom_output:
            output_paths = [Path(self.config.custom_output)]
        else:
            output_paths = [
                self.file_manager.generate_output_path(
                    path, 
                    self.config.custom_output, 
                    self.config.model_name,
                    self.config.include_timestamps
                )
                for path in validated_files
            ]
        
        results = []
        
        # Process each file
        for i, input_path in enumerate(validated_files):
            try:
                if len(validated_files) > 1:
                    print(f"\n[{i+1}/{len(validated_files)}]", end=" ")
                
                result = self.transcriber.transcribe_file(
                    input_path, 
                    self.config.include_timestamps,
                    self.verbose
                )
                
                # Set output path
                if self.config.batch_mode and self.config.custom_output:
                    result.output_file = output_paths[0]
                else:
                    result.output_file = output_paths[i]
                
                results.append(result)
                
            except TranscriptionError as e:
                print(f"Error: {e}", file=sys.stderr)
                if not self.config.batch_mode:
                    raise
                # In batch mode, continue with other files
                continue
        
        overall_end_time = time.time()
        overall_duration = overall_end_time - overall_start_time
        
        if len(validated_files) > 1 or self.verbose:
            print(f"\nTotal processing time: {self.transcriber._format_duration(overall_duration)}")
            if results:
                avg_time = overall_duration / len(results)
                print(f"Average time per file: {self.transcriber._format_duration(avg_time)}")
        
        return results
    
    def save_results(self, results: List[TranscriptionResult]):
        """
        Save transcription results to output files.
        
        Args:
            results: List of TranscriptionResult objects to save
            
        Raises:
            FileOutputError: If file writing fails
        """
        if not results:
            print("No results to save.")
            return
        
        try:
            if self.config.batch_mode and self.config.custom_output:
                # Concatenate all results into single file
                self._save_concatenated_results(results)
            else:
                # Save each result to separate file
                self._save_individual_results(results)
                
        except Exception as e:
            raise FileOutputError(f"Failed to save results: {e}")
    
    def _save_individual_results(self, results: List[TranscriptionResult]):
        """Save each result to its own output file."""
        for result in results:
            try:
                with open(result.output_file, 'w', encoding='utf-8') as f:
                    if self.config.include_timestamps and result.segments:
                        # Write with timestamps
                        for segment in result.segments:
                            start_time = self._format_timestamp(segment['start'])
                            end_time = self._format_timestamp(segment['end'])
                            text = segment['text'].strip()
                            f.write(f"[{start_time} -> {end_time}] {text}\n")
                    else:
                        # Write plain text
                        f.write(result.text)
                        f.write('\n')
                
                print(f"Saved: {result.output_file}")
                
            except Exception as e:
                raise FileOutputError(f"Failed to save {result.output_file}: {e}")
    
    def _save_concatenated_results(self, results: List[TranscriptionResult]):
        """Save all results concatenated into a single file."""
        output_file = results[0].output_file
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, result in enumerate(results):
                    # Add file header
                    f.write(f"=== {result.input_file.name} ===\n")
                    
                    if self.config.include_timestamps and result.segments:
                        # Write with timestamps
                        for segment in result.segments:
                            start_time = self._format_timestamp(segment['start'])
                            end_time = self._format_timestamp(segment['end'])
                            text = segment['text'].strip()
                            f.write(f"[{start_time} -> {end_time}] {text}\n")
                    else:
                        # Write plain text
                        f.write(result.text)
                        f.write('\n')
                    
                    # Add separator between files (except for last file)
                    if i < len(results) - 1:
                        f.write('\n' + '='*50 + '\n\n')
            
            print(f"Saved concatenated results: {output_file}")
            
        except Exception as e:
            raise FileOutputError(f"Failed to save concatenated results to {output_file}: {e}")
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp in MM:SS format."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert MP3 audio files to text transcripts using OpenAI's Whisper (GPU Optimized)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audio.mp3                    # Basic transcription (uses faster-whisper)
  %(prog)s -m large audio.mp3           # Use large model for better accuracy
  %(prog)s --engine original audio.mp3  # Use original Whisper (may have MPS issues)
  %(prog)s --engine faster audio.mp3    # Use faster-whisper (better compatibility)
  %(prog)s --device mps audio.mp3       # Force Apple Silicon GPU (original engine only)
  %(prog)s -t audio.mp3                 # Include timestamps
  %(prog)s -o transcript.txt audio.mp3  # Custom output filename
  %(prog)s *.mp3                        # Batch process multiple files
  %(prog)s -b -o all.txt *.mp3          # Concatenate all into single file
  %(prog)s -v audio.mp3                 # Verbose output

Supported Models (accuracy vs speed):
  tiny   - Fastest, least accurate (~39MB)
  base   - Good balance (default) (~74MB)
  small  - Better accuracy (~244MB)
  medium - High accuracy (~769MB)
  large  - Best accuracy (~1550MB)

Device Options:
  auto   - Automatically select best device (default)
  mps    - Apple Silicon GPU (Metal Performance Shaders)
  cuda   - NVIDIA GPU
  cpu    - CPU only

Engine Options:
  auto     - Prefer faster-whisper if available (default)
  original - Use OpenAI's original Whisper (may have MPS issues)
  faster   - Use faster-whisper (better compatibility, often faster)
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'files',
        nargs='+',
        help='MP3 audio file(s) to transcribe'
    )
    
    # Model selection
    parser.add_argument(
        '-m', '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='base',
        help='Whisper model to use (default: base)'
    )
    
    # Device selection
    parser.add_argument(
        '--device',
        choices=['auto', 'mps', 'cuda', 'cpu'],
        default='auto',
        help='Device to use for transcription (default: auto)'
    )
    
    # Engine selection
    parser.add_argument(
        '--engine',
        choices=['auto', 'original', 'faster'],
        default='auto',
        help='Whisper engine to use: auto (prefer faster), original (OpenAI), faster (faster-whisper) (default: auto)'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        help='Output filename (default: replace .mp3 with .txt)'
    )
    
    parser.add_argument(
        '-t', '--timestamps',
        action='store_true',
        help='Include timestamps in output'
    )
    
    parser.add_argument(
        '-b', '--batch',
        action='store_true',
        help='Batch mode: concatenate multiple files into single output'
    )
    
    # Utility options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed info: file stats, bitrate, sample rate, language detection, character counts'
    )
    
    return parser


def main():
    """Main entry point for the transcription tool."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # Create configuration
        config = TranscriptionConfig(
            model_name=args.model,
            include_timestamps=args.timestamps,
            batch_mode=args.batch,
            custom_output=args.output,
            device=None if args.device == 'auto' else args.device,
            engine=args.engine
        )
        
        if args.verbose:
            print(f"Configuration:")
            print(f"  Model: {config.model_name}")
            print(f"  Engine: {config.engine}")
            print(f"  Device: {config.device or 'auto-detect'}")
            print(f"  Timestamps: {config.include_timestamps}")
            print(f"  Batch mode: {config.batch_mode}")
            print(f"  Output: {config.custom_output or 'auto-generate'}")
            print()
        
        # Validate batch mode usage
        if args.batch and len(args.files) == 1:
            print("Warning: Batch mode specified but only one file provided.", file=sys.stderr)
        
        if args.batch and not args.output:
            print("Error: Batch mode requires output filename (-o/--output)", file=sys.stderr)
            sys.exit(1)
        
        # Create service and process files
        service = TranscriptionService(config, args.verbose)
        results = service.process_files(args.files)
        
        if results:
            service.save_results(results)
            print(f"\nSuccessfully processed {len(results)} file(s)")
        else:
            print("No files were successfully processed.", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except (TranscriptionError, FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()