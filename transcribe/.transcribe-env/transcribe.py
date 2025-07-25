#!/usr/bin/env python3
"""
MP3 Transcription Tool
A command-line tool for converting MP3 audio files to text transcripts using OpenAI's Whisper.
"""

import argparse
import sys
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

import whisper


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


class FileManager:
    """Handles file validation and output path generation."""
    
    SUPPORTED_EXTENSIONS = {'.mp3'}
    
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
    
    def generate_output_path(self, input_path: Path, custom_output: Optional[str] = None) -> Path:
        """
        Generates appropriate output filename for a given input file.
        
        Args:
            input_path: Path to input MP3 file
            custom_output: Optional custom output filename
            
        Returns:
            Path object for output file
        """
        if custom_output:
            return Path(custom_output)
        
        # Default: replace extension with .txt
        return input_path.with_suffix('.txt')
    
    def handle_batch_output_paths(self, input_paths: List[Path], 
                                custom_output: Optional[str] = None) -> List[Path]:
        """
        Handles output path generation for batch processing.
        
        Args:
            input_paths: List of input file paths
            custom_output: Optional custom output filename for concatenation
            
        Returns:
            List of output paths (single path if concatenating, multiple if separate files)
        """
        if custom_output:
            # Single output file for concatenation
            return [Path(custom_output)]
        else:
            # Separate output file for each input
            return [self.generate_output_path(path) for path in input_paths]


class AudioTranscriber:
    """Handles audio transcription using OpenAI's Whisper model."""
    
    def __init__(self, model_name: str = 'base'):
        """
        Initialize the transcriber with a Whisper model.
        
        Args:
            model_name: Name of the Whisper model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model with comprehensive error handling."""
        try:
            print(f"Loading Whisper model '{self.model_name}'...")
            
            # Check available disk space for model download
            self._check_disk_space()
            
            self.model = whisper.load_model(self.model_name)
            print(f"✓ Model '{self.model_name}' loaded successfully")
            
        except MemoryError:
            raise ModelLoadError(
                f"Insufficient memory to load model '{self.model_name}'. "
                f"Try using a smaller model like 'tiny' or 'base'."
            )
        except OSError as e:
            if "No space left on device" in str(e):
                raise ModelLoadError(
                    f"Insufficient disk space to download model '{self.model_name}'. "
                    f"Please free up disk space and try again."
                )
            else:
                raise ModelLoadError(f"Failed to load model '{self.model_name}': {e}")
        except Exception as e:
            # Check if it's a network-related error
            if "connection" in str(e).lower() or "network" in str(e).lower():
                raise ModelLoadError(
                    f"Network error while downloading model '{self.model_name}': {e}. "
                    f"Please check your internet connection and try again."
                )
            else:
                raise ModelLoadError(f"Failed to load Whisper model '{self.model_name}': {e}")
    
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
    
    def transcribe_file(self, file_path: Path, include_timestamps: bool = False) -> TranscriptionResult:
        """
        Transcribe a single audio file with comprehensive error handling.
        
        Args:
            file_path: Path to the audio file
            include_timestamps: Whether to include timestamp information
            
        Returns:
            TranscriptionResult object with transcription data
            
        Raises:
            TranscriptionError: If transcription fails
        """
        if not self.model:
            raise TranscriptionError("Model not loaded")
        
        try:
            print(f"Transcribing: {file_path.name}")
            
            # Check file size and provide warnings for very large files
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 100:
                print(f"⚠️  Large file detected ({file_size_mb:.1f}MB). This may take a while...")
            
            # Perform transcription
            result = self.model.transcribe(str(file_path))
            
            # Validate transcription result
            if not isinstance(result, dict):
                raise TranscriptionError(f"Invalid transcription result format for {file_path}")
            
            # Extract text and segments
            text = result.get("text", "").strip()
            segments = result.get("segments", [])
            language = result.get("language", "unknown")
            
            # Check if transcription produced any text
            if not text and not segments:
                raise TranscriptionError(
                    f"No speech detected in {file_path}. "
                    f"Please check if the file contains audible speech."
                )
            
            print(f"✓ Transcription complete ({language})")
            
            return TranscriptionResult(
                text=text,
                segments=segments,
                language=language,
                input_file=file_path,
                output_file=Path("")  # Will be set later
            )
            
        except MemoryError:
            raise TranscriptionError(
                f"Insufficient memory to transcribe {file_path}. "
                f"Try using a smaller model or processing smaller audio files."
            )
        except OSError as e:
            if "No space left on device" in str(e):
                raise TranscriptionError(
                    f"Insufficient disk space during transcription of {file_path}. "
                    f"Please free up disk space and try again."
                )
            else:
                raise TranscriptionError(f"File system error while transcribing {file_path}: {e}")
        except Exception as e:
            # Check for common audio format issues
            error_msg = str(e).lower()
            if "format" in error_msg or "codec" in error_msg or "decode" in error_msg:
                raise TranscriptionError(
                    f"Audio format error in {file_path}: {e}. "
                    f"Please ensure the file is a valid MP3 audio file."
                )
            else:
                raise TranscriptionError(f"Failed to transcribe {file_path}: {e}")
    
    def transcribe_multiple_files(self, file_paths: List[Path], 
                                include_timestamps: bool = False) -> List[TranscriptionResult]:
        """
        Transcribe multiple audio files with enhanced batch processing.
        
        Args:
            file_paths: List of paths to audio files
            include_timestamps: Whether to include timestamp information
            
        Returns:
            List of TranscriptionResult objects
        """
        results = []
        failed_files = []
        total_files = len(file_paths)
        
        print(f"\n🎵 Starting batch transcription of {total_files} file(s)")
        print("=" * 50)
        
        # Calculate total size for progress estimation
        total_size_mb = 0
        for file_path in file_paths:
            try:
                total_size_mb += file_path.stat().st_size / (1024 * 1024)
            except OSError:
                pass  # Skip if we can't get file size
        
        if total_size_mb > 0:
            print(f"Total audio size: {total_size_mb:.1f}MB")
        
        import time
        start_time = time.time()
        
        for i, file_path in enumerate(file_paths, 1):
            print(f"\n[{i}/{total_files}] Processing: {file_path.name}")
            
            # Show file size
            try:
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  File size: {file_size_mb:.1f}MB")
            except OSError:
                pass
            
            # Show progress percentage
            progress = (i - 1) / total_files * 100
            print(f"  Progress: {progress:.1f}% complete")
            
            file_start_time = time.time()
            
            try:
                result = self.transcribe_file(file_path, include_timestamps)
                results.append(result)
                
                # Show processing time
                file_duration = time.time() - file_start_time
                print(f"  ✓ Completed in {file_duration:.1f}s")
                
            except TranscriptionError as e:
                failed_files.append((file_path, str(e)))
                print(f"  ✗ Error processing {file_path.name}: {e}", file=sys.stderr)
                continue
            except Exception as e:
                failed_files.append((file_path, str(e)))
                print(f"  ✗ Unexpected error processing {file_path.name}: {e}", file=sys.stderr)
                continue
        
        # Show final summary
        total_duration = time.time() - start_time
        successful_count = len(results)
        failed_count = len(failed_files)
        
        print("\n" + "=" * 50)
        print(f"📊 Batch Processing Summary")
        print(f"  Total files: {total_files}")
        print(f"  Successful: {successful_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total time: {total_duration:.1f}s")
        
        if total_size_mb > 0 and total_duration > 0:
            throughput = total_size_mb / total_duration
            print(f"  Throughput: {throughput:.1f}MB/s")
        
        if failed_files:
            print(f"\n⚠️  Failed files:")
            for file_path, error in failed_files:
                print(f"  - {file_path.name}: {error}")
        
        return results


class TimestampFormatter:
    """Handles formatting of timestamps for transcript output."""
    
    @staticmethod
    def format_seconds_to_timestamp(seconds: float) -> str:
        """
        Convert seconds to readable timestamp format [HH:MM:SS].
        
        Args:
            seconds: Time in seconds (can be float)
            
        Returns:
            Formatted timestamp string like [00:01:23]
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    
    @staticmethod
    def format_segment_with_timestamp(segment: Dict[str, Any]) -> str:
        """
        Format a single segment with timestamp.
        
        Args:
            segment: Whisper segment dictionary with 'start', 'end', and 'text' keys
            
        Returns:
            Formatted string with timestamp and text
        """
        start_time = segment.get('start', 0)
        text = segment.get('text', '').strip()
        
        timestamp = TimestampFormatter.format_seconds_to_timestamp(start_time)
        return f"{timestamp} {text}"
    
    @staticmethod
    def format_transcript_with_timestamps(result: TranscriptionResult) -> str:
        """
        Format a complete transcript with timestamps for each segment.
        
        Args:
            result: TranscriptionResult object containing segments
            
        Returns:
            Formatted transcript string with timestamps
        """
        if not result.segments:
            # Fallback to plain text if no segments available
            return result.text
        
        formatted_lines = []
        for segment in result.segments:
            formatted_line = TimestampFormatter.format_segment_with_timestamp(segment)
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_transcript_without_timestamps(result: TranscriptionResult) -> str:
        """
        Format a transcript without timestamps (plain text).
        
        Args:
            result: TranscriptionResult object
            
        Returns:
            Plain text transcript
        """
        return result.text
    
    @staticmethod
    def format_transcript(result: TranscriptionResult, include_timestamps: bool = False) -> str:
        """
        Format a transcript with or without timestamps based on configuration.
        
        Args:
            result: TranscriptionResult object
            include_timestamps: Whether to include timestamps
            
        Returns:
            Formatted transcript string
        """
        if include_timestamps:
            return TimestampFormatter.format_transcript_with_timestamps(result)
        else:
            return TimestampFormatter.format_transcript_without_timestamps(result)


def main():
    """Main entry point for the transcription tool with comprehensive lifecycle management."""
    # Set up application metadata
    app_name = "MP3 Transcription Tool"
    app_version = "1.0.0"
    
    parser = argparse.ArgumentParser(
        prog='transcribe',
        description='Convert MP3 audio files to text transcripts using Whisper',
        epilog='''
Examples:
  transcribe audio.mp3                    # Basic transcription
  transcribe -t audio.mp3                 # With timestamps  
  transcribe -o transcript.txt audio.mp3  # Custom output name
  transcribe *.mp3                        # Batch processing
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'{app_name} v{app_version}'
    )
    
    parser.add_argument(
        'files', 
        nargs='+', 
        help='MP3 files to transcribe'
    )
    parser.add_argument(
        '-t', '--timestamps', 
        action='store_true', 
        help='Include timestamps in the transcript'
    )
    parser.add_argument(
        '-o', '--output', 
        help='Output filename (for single file) or concatenated output (for multiple files)'
    )
    parser.add_argument(
        '-m', '--model', 
        default='base', 
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: base)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output with system information'
    )
    
    args = parser.parse_args()
    
    # Set up signal handlers for graceful shutdown
    _setup_signal_handlers()
    
    # Show system information if verbose mode is enabled
    if args.verbose:
        _print_system_info()
        print()
    
    # Validate configuration
    _validate_configuration(args)
    
    # Initialize application components
    file_manager = FileManager()
    
    try:
        # Validate input files
        validated_files = file_manager.validate_input_files(args.files)
        print(f"✓ Validated {len(validated_files)} input file(s)")
        
        # Generate output paths
        output_paths = file_manager.handle_batch_output_paths(validated_files, args.output)
        
        # Create configuration from arguments
        config = TranscriptionConfig(
            model_name=args.model,
            include_timestamps=args.timestamps,
            batch_mode=len(validated_files) > 1,
            custom_output=args.output
        )
        
        # Initialize transcriber
        transcriber = AudioTranscriber(config.model_name)
        
        # Perform transcription
        if config.batch_mode:
            results = transcriber.transcribe_multiple_files(validated_files, config.include_timestamps)
        else:
            result = transcriber.transcribe_file(validated_files[0], config.include_timestamps)
            results = [result]
        
        if not results:
            print("No files were successfully transcribed.", file=sys.stderr)
            sys.exit(1)
        
        # Process and save results
        try:
            if config.custom_output and config.batch_mode:
                # Concatenate all transcripts into single output file
                _save_concatenated_transcript(results, output_paths[0], config.include_timestamps)
            else:
                # Save individual transcript files
                for result, output_path in zip(results, output_paths):
                    result.output_file = output_path
                    _save_individual_transcript(result, config.include_timestamps)
            
            print(f"\n✓ Transcription complete! Generated {len(output_paths)} output file(s).")
            
        except FileOutputError as e:
            print(f"Output error: {e}", file=sys.stderr)
            sys.exit(1)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"File error: {e}", file=sys.stderr)
        print("Suggestion: Check that all input files exist and are valid MP3 files.", file=sys.stderr)
        sys.exit(1)
    except ModelLoadError as e:
        print(f"Model error: {e}", file=sys.stderr)
        print("Suggestion: Try using a smaller model (e.g., -m tiny) or check your internet connection.", file=sys.stderr)
        sys.exit(1)
    except TranscriptionError as e:
        print(f"Transcription error: {e}", file=sys.stderr)
        print("Suggestion: Check that your audio files contain clear speech and are not corrupted.", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.", file=sys.stderr)
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print("Please report this issue if it persists.", file=sys.stderr)
        sys.exit(1)


def _validate_configuration(args):
    """Validate command-line arguments and configuration."""
    # Check for conflicting options
    if len(args.files) > 1 and args.output and not args.output.endswith('.txt'):
        print("Warning: Custom output filename should end with .txt for clarity", file=sys.stderr)
    
    # Validate model choice (already handled by argparse choices, but we can add warnings)
    model_sizes = {
        'tiny': '~39MB',
        'base': '~74MB', 
        'small': '~244MB',
        'medium': '~769MB',
        'large': '~1550MB'
    }
    
    if args.model in model_sizes:
        model_size = model_sizes[args.model]
        if args.model in ['medium', 'large']:
            print(f"Note: Using {args.model} model ({model_size}). This may require significant memory and processing time.", file=sys.stderr)


def _setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    import signal
    
    def signal_handler(signum, frame):
        print(f"\n⚠️  Received signal {signum}. Shutting down gracefully...", file=sys.stderr)
        sys.exit(130)
    
    # Handle common termination signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def _print_system_info():
    """Print system information for debugging purposes."""
    import platform
    
    try:
        print("System Information:")
        print(f"  OS: {platform.system()} {platform.release()}")
        print(f"  Python: {platform.python_version()}")
        print(f"  Architecture: {platform.machine()}")
        
        # Try to get memory and CPU info if psutil is available
        try:
            import psutil
            
            # Memory information
            memory = psutil.virtual_memory()
            print(f"  Available Memory: {memory.available / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB")
            
            # CPU information
            print(f"  CPU Cores: {psutil.cpu_count()}")
            
        except ImportError:
            print("  Memory/CPU Info: (psutil not available)")
        
    except Exception:
        # Any other error, skip silently
        print("System Information: (unavailable)")
        pass


def _save_individual_transcript(result: TranscriptionResult, include_timestamps: bool):
    """Save a single transcript to file with comprehensive error handling."""
    try:
        # Check if output directory exists and is writable
        output_dir = result.output_file.parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                raise FileOutputError(
                    f"Permission denied: Cannot create directory {output_dir}. "
                    f"Please check directory permissions or choose a different output location."
                )
        
        if not os.access(output_dir, os.W_OK):
            raise FileOutputError(
                f"Permission denied: Cannot write to directory {output_dir}. "
                f"Please check directory permissions or choose a different output location."
            )
        
        # Check available disk space
        _, _, free_bytes = shutil.disk_usage(output_dir)
        if free_bytes < 1024 * 1024:  # Less than 1MB free
            raise FileOutputError(
                f"Insufficient disk space to save {result.output_file}. "
                f"Please free up disk space and try again."
            )
        
        # Format and save transcript
        formatted_text = TimestampFormatter.format_transcript(result, include_timestamps)
        
        with open(result.output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        print(f"✓ Saved: {result.output_file}")
        
    except FileOutputError:
        # Re-raise our custom errors
        raise
    except PermissionError as e:
        raise FileOutputError(
            f"Permission denied saving {result.output_file}: {e}. "
            f"Please check file permissions or choose a different output location."
        )
    except OSError as e:
        if "No space left on device" in str(e):
            raise FileOutputError(
                f"Insufficient disk space to save {result.output_file}. "
                f"Please free up disk space and try again."
            )
        else:
            raise FileOutputError(f"File system error saving {result.output_file}: {e}")
    except Exception as e:
        raise FileOutputError(f"Unexpected error saving {result.output_file}: {e}")


def _save_concatenated_transcript(results: List[TranscriptionResult], output_path: Path, include_timestamps: bool):
    """Save multiple transcripts concatenated into a single file with error handling."""
    try:
        # Check if output directory exists and is writable
        output_dir = output_path.parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                raise FileOutputError(
                    f"Permission denied: Cannot create directory {output_dir}. "
                    f"Please check directory permissions or choose a different output location."
                )
        
        if not os.access(output_dir, os.W_OK):
            raise FileOutputError(
                f"Permission denied: Cannot write to directory {output_dir}. "
                f"Please check directory permissions or choose a different output location."
            )
        
        # Prepare combined content
        combined_content = []
        
        for i, result in enumerate(results):
            # Add file header for each transcript
            header = f"\n=== {result.input_file.name} ===\n"
            if i == 0:
                header = header.lstrip('\n')  # Remove leading newline for first file
            
            formatted_text = TimestampFormatter.format_transcript(result, include_timestamps)
            combined_content.append(header + formatted_text)
        
        final_content = '\n\n'.join(combined_content)
        
        # Check available disk space based on content size
        content_size = len(final_content.encode('utf-8'))
        _, _, free_bytes = shutil.disk_usage(output_dir)
        if free_bytes < content_size + 1024 * 1024:  # Content size + 1MB buffer
            raise FileOutputError(
                f"Insufficient disk space to save {output_path}. "
                f"Need ~{content_size / (1024*1024):.1f}MB but only "
                f"{free_bytes / (1024*1024):.1f}MB available."
            )
        
        # Save the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✓ Saved concatenated transcript: {output_path}")
        
    except FileOutputError:
        # Re-raise our custom errors
        raise
    except PermissionError as e:
        raise FileOutputError(
            f"Permission denied saving {output_path}: {e}. "
            f"Please check file permissions or choose a different output location."
        )
    except OSError as e:
        if "No space left on device" in str(e):
            raise FileOutputError(
                f"Insufficient disk space to save {output_path}. "
                f"Please free up disk space and try again."
            )
        else:
            raise FileOutputError(f"File system error saving {output_path}: {e}")
    except Exception as e:
        raise FileOutputError(f"Unexpected error saving {output_path}: {e}")


if __name__ == '__main__':
    main()