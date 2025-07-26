#!/usr/bin/env python3
"""
MP3 Transcription Tool (GPU Optimized)
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
import torch


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
    """Handles audio transcription using OpenAI's Whisper model with GPU acceleration."""
    
    def __init__(self, model_name: str = 'base', device: Optional[str] = None):
        """
        Initialize the transcriber with a Whisper model.
        
        Args:
            model_name: Name of the Whisper model to use
            device: Device to use ('mps', 'cuda', 'cpu', or None for auto-detect)
        """
        self.model_name = model_name
        self.device = device or self._get_optimal_device()
        self.model = None
        self._load_model()
    
    def _get_optimal_device(self) -> str:
        """Determine the best device for transcription on this system."""
        # CUDA is most stable for Whisper
        if torch.cuda.is_available():
            return "cuda"  # NVIDIA GPU
        # MPS has some compatibility issues with Whisper, but we'll try it with fallback
        elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
            return "mps"  # Apple Silicon GPU (with CPU fallback if needed)
        else:
            return "cpu"   # CPU fallback
    
    def _load_model(self):
        """Load the Whisper model with comprehensive error handling and hardware acceleration."""
        original_device = self.device
        
        try:
            device_name = {
                "mps": "Apple Silicon GPU (Metal)",
                "cuda": "NVIDIA GPU (CUDA)", 
                "cpu": "CPU"
            }.get(self.device, self.device)
            
            print(f"Loading Whisper model '{self.model_name}' on {device_name}...")
            
            # Check available disk space for model download
            self._check_disk_space()
            
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"✓ Model '{self.model_name}' loaded successfully on {device_name}")
            
        except MemoryError:
            raise ModelLoadError(
                f"Insufficient memory to load model '{self.model_name}' on {self.device}. "
                f"Try using a smaller model like 'tiny' or 'base', or use CPU with --device cpu."
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
            # Check if it's an MPS compatibility issue
            elif self.device == "mps" and ("sparse" in str(e).lower() or "mps" in str(e).lower()):
                print(f"⚠️  MPS compatibility issue detected. Falling back to CPU...")
                self.device = "cpu"
                try:
                    self.model = whisper.load_model(self.model_name, device=self.device)
                    print(f"✓ Model '{self.model_name}' loaded successfully on CPU (MPS fallback)")
                except Exception as fallback_error:
                    raise ModelLoadError(f"Failed to load model on both MPS and CPU: {fallback_error}")
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
  
    def transcribe_file(self, input_path: Path, include_timestamps: bool = False) -> TranscriptionResult:
        """
        Transcribe a single audio file.
        
        Args:
            input_path: Path to the input audio file
            include_timestamps: Whether to include timestamp information
            
        Returns:
            TranscriptionResult object containing transcription data
            
        Raises:
            TranscriptionError: If transcription fails
        """
        if not self.model:
            raise TranscriptionError("Model not loaded. Cannot perform transcription.")
        
        try:
            print(f"Transcribing: {input_path.name}")
            
            # Perform transcription
            result = self.model.transcribe(str(input_path))
            
            # Extract relevant information
            text = result['text'].strip()
            segments = result.get('segments', []) if include_timestamps else []
            language = result.get('language', 'unknown')
            
            return TranscriptionResult(
                text=text,
                segments=segments,
                language=language,
                input_file=input_path,
                output_file=Path()  # Will be set by caller
            )
            
        except Exception as e:
            raise TranscriptionError(f"Failed to transcribe {input_path.name}: {e}")


class TranscriptionService:
    """Main service class that orchestrates the transcription process."""
    
    def __init__(self, config: TranscriptionConfig):
        """Initialize the transcription service with configuration."""
        self.config = config
        self.file_manager = FileManager()
        self.transcriber = AudioTranscriber(config.model_name, config.device)
    
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
        # Validate input files
        validated_files = self.file_manager.validate_input_files(input_files)
        
        # Generate output paths
        if self.config.batch_mode and self.config.custom_output:
            output_paths = [Path(self.config.custom_output)]
        else:
            output_paths = [
                self.file_manager.generate_output_path(path, self.config.custom_output)
                for path in validated_files
            ]
        
        results = []
        
        # Process each file
        for i, input_path in enumerate(validated_files):
            try:
                result = self.transcriber.transcribe_file(
                    input_path, 
                    self.config.include_timestamps
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
                
                print(f"✓ Saved: {result.output_file}")
                
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
            
            print(f"✓ Saved concatenated results: {output_file}")
            
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
  %(prog)s audio.mp3                    # Basic transcription
  %(prog)s -m large audio.mp3           # Use large model for better accuracy
  %(prog)s --device mps audio.mp3       # Force Apple Silicon GPU
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
        help='Enable verbose output'
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
            device=None if args.device == 'auto' else args.device
        )
        
        if args.verbose:
            print(f"Configuration:")
            print(f"  Model: {config.model_name}")
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
        service = TranscriptionService(config)
        results = service.process_files(args.files)
        
        if results:
            service.save_results(results)
            print(f"\n✓ Successfully processed {len(results)} file(s)")
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