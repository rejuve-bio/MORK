#!/usr/bin/env python3

"""
Enhanced MORK Dataset Loader Script

This script loads MeTTa files from a specified path into a MORK server.
It can also clear spaces without loading data.

Usage: 
  python enhanced_mork_loader.py --path /path/to/metta/files --port 8431
  python enhanced_mork_loader.py --clear --port 8431 --space annotation
"""

import argparse
import os
import sys
import glob
import time
from pathlib import Path
from client import ManagedMORK


def load_metta_dataset(dataset_path, mork_port, space, clear_before_load=True):
    """
    Load MeTTa dataset into MORK server
    
    Args:
        dataset_path (str): Path to directory containing .metta files
        mork_port (int): MORK server port
        space (str): MORK space to load into
        clear_before_load (bool): Whether to clear before loading
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Validate dataset path
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset path '{dataset_path}' does not exist.")
        return False
    
    # Find .metta files
    metta_files = glob.glob(os.path.join(dataset_path, "**/*.metta"), recursive=True)
    if not metta_files:
        print(f"Error: No .metta files found in '{dataset_path}'")
        return False
    
    print(f"Found {len(metta_files)} .metta files in {dataset_path}")
    
    try:
        # Connect to MORK server
        mork_url = f"http://localhost:{mork_port}"
        print(f"Connecting to MORK server at {mork_url}...")
        
        server = ManagedMORK.connect(url=mork_url)
        print("Connected to MORK server successfully")
        
        # Clear existing data if requested
        if clear_before_load:
            print("Clearing existing data...")
            server.clear()
        
        # Load files
        print(f"Loading files into '{space}' space...")
        start_time = time.time()
        
        failed_files = []
        successful_files = 0
        
        with server.work_at(space) as workspace:
            for i, file_path in enumerate(metta_files, 1):
                if "dbsnp" in file_path:
                    print(f"Skiping {file_path}")
                    continue
                path_obj = Path(file_path)
                file_url = path_obj.resolve().as_uri()
                
                # Docker volume mount adjustments
                file_url = file_url.replace("/mnt/hdd_1/abdu/metta_out_v5", "/shared/output")
                file_url = file_url.replace("/mnt/hdd_1/dawit/metta_sample/output", "/shared/output")
                
                print(f"  [{i:3d}/{len(metta_files)}] Loading: {file_path}")
                
                try:
                    workspace.sexpr_import_(file_url).block()
                    successful_files += 1
                except Exception as e:
                    print(f"    Warning: Error loading {file_path}: {e}")
                    failed_files.append((file_path, str(e)))
                    continue
        
        # Calculate loading time
        end_time = time.time()
        loading_time = end_time - start_time
        
        print(f"\nDataset loading completed!")
        print(f"   Files found: {len(metta_files)}")
        print(f"   Files loaded successfully: {successful_files}")
        print(f"   Files failed: {len(failed_files)}")
        print(f"   Loading time: {loading_time:.2f} seconds")
        print(f"   Target space: {space}")
        print(f"   MORK server: {mork_url}")
        
        if failed_files:
            print(f"\nFailed files:")
            for filename, error in failed_files:
                print(f"   - {filename}: {error}")
        
        return successful_files > 0
        
    except Exception as e:
        print(f"Error: Failed to load dataset: {e}")
        return False

def clear_mork_space(mork_port, space=None):
    """
    Clear MORK space or entire server
    
    Args:
        mork_port (int): MORK server port
        space (str): MORK space to clear, if None clears entire server
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        mork_url = f"http://localhost:{mork_port}"
        print(f"Connecting to MORK server at {mork_url}...")
        
        server = ManagedMORK.connect(url=mork_url)
        print("Connected to MORK server successfully")
        
        if space:
            print(f"Clearing space '{space}'...")
            with server.work_at(space) as workspace:
                workspace.clear()
            print(f"Space '{space}' cleared successfully")
        else:
            print("Clearing entire MORK server...")
            server.clear()
            print("Entire MORK server cleared successfully")
        
        return True
        
    except Exception as e:
        print(f"Error: Failed to clear: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced MORK Dataset Loader - Load MeTTa files or clear MORK spaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load dataset without clearing (default behavior)
  python enhanced_mork_loader.py --path /path/to/metta/files --port 8431 --space annotation
  
  # Load dataset with clearing first
  python enhanced_mork_loader.py --path /path/to/metta/files --port 8431 --space annotation --clear
  
  # Clear specific space only (no loading)
  python enhanced_mork_loader.py --clear --space annotation --port 8431
  
  # Clear entire MORK server (no loading) 
  python enhanced_mork_loader.py --clear --space all --port 8431
  
  # Verbose output
  python enhanced_mork_loader.py --path /path/to/metta/files --port 8431 --space annotation --verbose
        """
    )
    
    # Main arguments
    parser.add_argument(
        '--path', '-p',
        help='Path to directory containing .metta files (for loading)'
    )
    
    # Configuration options
    parser.add_argument(
        '--port',
        type=int,
        help='MORK server port (required)'
    )
    
    parser.add_argument(
        '--space', '-s',
        help='MORK space to use (required)'
    )
    
    parser.add_argument(
        '--clear', '-c',
        action='store_true',
        help='Clear before loading (when used with --path) or clear-only mode (when used alone)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate required arguments
    if not args.port:
        parser.error("--port is required")
    
    if not args.space:
        parser.error("--space is required")
    
    if not args.path and not args.clear:
        parser.error("Either --path (to load data) or --clear (clear-only mode) is required")
    
    # Print header
    print("=" * 60)
    print("Enhanced MORK Dataset Loader")
    print("=" * 60)
    
    if args.verbose:
        print(f"Configuration:")
        if args.path:
            print(f"   Mode: Load dataset")
            print(f"   Dataset path: {args.path}")
            print(f"   Clear before load: {args.clear}")
        else:
            print(f"   Mode: Clear space only")
        print(f"   MORK port: {args.port}")
        print(f"   Target space: {args.space}")
        print()
    
    success = False
    
    if args.path:
        # Load mode (with optional clearing)
        success = load_metta_dataset(
            dataset_path=args.path,
            mork_port=args.port,
            space=args.space,
            clear_before_load=args.clear
        )
    else:
        # Clear-only mode
        if args.space.lower() == 'all':
            success = clear_mork_space(args.port, space=None)
        else:
            success = clear_mork_space(args.port, space=args.space)
    
    print("=" * 60)
    
    if success:
        print("Operation completed successfully!")
        sys.exit(0)
    else:
        print("Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()