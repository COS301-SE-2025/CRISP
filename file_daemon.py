#!/usr/bin/env python3
"""
File-based CRISP Anonymization Daemon

Watches input directory for JSON files, processes them, and outputs anonymized versions.
"""

import json
import os
import time
import signal
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging
import shutil

from crisp_anonymization import (
    AnonymizationContext,
    AnonymizationLevel,
    DataType,
    AnonymizationError
)


class FileAnonymizationDaemon:
    """File-based anonymization daemon"""
    
    def __init__(self, input_dir: str, output_dir: str, error_dir: str = None, 
                 trust_level: str = "medium", poll_interval: float = 1.0,
                 log_level: str = "INFO"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.error_dir = Path(error_dir) if error_dir else self.output_dir / "errors"
        self.processed_dir = self.output_dir / "processed"
        
        # Create directories
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.error_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        self.trust_level = trust_level
        self.poll_interval = poll_interval
        self.running = False
        
        # Setup logging
        self.logger = self._setup_logging(log_level)
        
        # Anonymization context
        self.anonymization_context = AnonymizationContext()
        
        # Trust level mapping
        self.trust_levels = {
            "high": AnonymizationLevel.LOW,
            "medium": AnonymizationLevel.MEDIUM,
            "low": AnonymizationLevel.HIGH,
            "untrusted": AnonymizationLevel.FULL
        }
        
        # Stats
        self.stats = {
            'processed': 0,
            'errors': 0,
            'start_time': None
        }
    
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('file_anonymization_daemon')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _get_trust_level_from_filename(self, filename: str) -> str:
        """Extract trust level from filename if specified"""
        # Check for trust level in filename (e.g., stix_data_high.json)
        filename_lower = filename.lower()
        for level in ["high", "medium", "low", "untrusted"]:
            if f"_{level}" in filename_lower or f"-{level}" in filename_lower:
                return level
        return self.trust_level
    
    def _process_file(self, file_path: Path) -> bool:
        """Process a single JSON file"""
        try:
            self.logger.info(f"Processing file: {file_path.name}")
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determine trust level
            trust_level = self._get_trust_level_from_filename(file_path.name)
            anonymization_level = self.trust_levels.get(trust_level, AnonymizationLevel.MEDIUM)
            
            start_time = time.time()
            
            # Check if it's a STIX bundle or single object
            if isinstance(data, dict) and data.get('type') == 'bundle':
                # Process STIX bundle
                processed_objects = []
                for obj in data.get('objects', []):
                    try:
                        anonymized_json = self.anonymization_context.anonymize_stix_object(
                            obj, anonymization_level
                        )
                        processed_objects.append(json.loads(anonymized_json))
                    except Exception as e:
                        self.logger.error(f"Error processing object {obj.get('id', 'unknown')}: {e}")
                        processed_objects.append(obj)  # Keep original on error
                
                anonymized_data = {
                    **data,
                    'objects': processed_objects
                }
            else:
                # Process single STIX object
                anonymized_json = self.anonymization_context.anonymize_stix_object(
                    data, anonymization_level
                )
                anonymized_data = json.loads(anonymized_json)
            
            processing_time = time.time() - start_time
            
            # Add metadata
            metadata = {
                'original_file': file_path.name,
                'trust_level': trust_level,
                'anonymization_level': anonymization_level.value,
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'processing_time': processing_time
            }
            
            # Create output filename
            output_filename = f"anonymized_{file_path.name}"
            output_path = self.output_dir / output_filename
            
            # Write anonymized data
            output_data = {
                'anonymized_data': anonymized_data,
                'metadata': metadata
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Move original to processed directory
            processed_path = self.processed_dir / file_path.name
            shutil.move(str(file_path), str(processed_path))
            
            self.stats['processed'] += 1
            self.logger.info(f"Successfully processed {file_path.name} -> {output_filename} "
                           f"(trust: {trust_level}, time: {processing_time:.3f}s)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path.name}: {e}")
            
            # Move to error directory
            error_path = self.error_dir / file_path.name
            try:
                shutil.move(str(file_path), str(error_path))
                
                # Create error report
                error_report = {
                    'error': str(e),
                    'file': file_path.name,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                error_report_path = self.error_dir / f"error_{file_path.name}"
                with open(error_report_path, 'w', encoding='utf-8') as f:
                    json.dump(error_report, f, indent=2)
                    
            except Exception as move_error:
                self.logger.error(f"Failed to move error file: {move_error}")
            
            self.stats['errors'] += 1
            return False
    
    def _scan_input_directory(self) -> List[Path]:
        """Scan input directory for JSON files"""
        json_files = []
        try:
            for file_path in self.input_dir.glob("*.json"):
                if file_path.is_file():
                    json_files.append(file_path)
        except Exception as e:
            self.logger.error(f"Error scanning input directory: {e}")
        
        return sorted(json_files)  # Process in alphabetical order
    
    def start(self):
        """Start the daemon"""
        self.logger.info("Starting File Anonymization Daemon")
        self.logger.info(f"Input directory: {self.input_dir}")
        self.logger.info(f"Output directory: {self.output_dir}")
        self.logger.info(f"Error directory: {self.error_dir}")
        self.logger.info(f"Default trust level: {self.trust_level}")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        self.logger.info("Daemon started, watching for files...")
        
        # Main processing loop
        while self.running:
            try:
                # Scan for files
                files_to_process = self._scan_input_directory()
                
                if files_to_process:
                    self.logger.info(f"Found {len(files_to_process)} files to process")
                    
                    for file_path in files_to_process:
                        if not self.running:
                            break
                        self._process_file(file_path)
                
                # Sleep before next scan
                time.sleep(self.poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying
        
        self.logger.info("Daemon stopped")
    
    def stop(self):
        """Stop the daemon"""
        self.logger.info("Stopping daemon...")
        self.running = False
        self._log_stats()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}")
        self.stop()
    
    def _log_stats(self):
        """Log processing statistics"""
        if self.stats['start_time']:
            uptime = time.time() - self.stats['start_time']
            rate = self.stats['processed'] / uptime if uptime > 0 else 0
            
            self.logger.info(
                f"Final Stats - Processed: {self.stats['processed']}, "
                f"Errors: {self.stats['errors']}, "
                f"Rate: {rate:.2f} files/sec, "
                f"Uptime: {uptime:.0f}s"
            )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='File-based CRISP Anonymization Daemon')
    parser.add_argument('--input-dir', '-i', required=True, 
                       help='Input directory to watch for JSON files')
    parser.add_argument('--output-dir', '-o', required=True,
                       help='Output directory for anonymized files')
    parser.add_argument('--error-dir', '-e',
                       help='Error directory (defaults to output_dir/errors)')
    parser.add_argument('--trust-level', '-t', default='medium',
                       choices=['high', 'medium', 'low', 'untrusted'],
                       help='Default trust level for anonymization')
    parser.add_argument('--poll-interval', '-p', type=float, default=1.0,
                       help='Polling interval in seconds')
    parser.add_argument('--log-level', '-l', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Log level')
    parser.add_argument('--one-shot', action='store_true',
                       help='Process existing files once and exit')
    
    args = parser.parse_args()
    
    # Create daemon
    daemon = FileAnonymizationDaemon(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        error_dir=args.error_dir,
        trust_level=args.trust_level,
        poll_interval=args.poll_interval,
        log_level=args.log_level
    )
    
    if args.one_shot:
        # Process existing files once and exit
        daemon.logger.info("Running in one-shot mode")
        files_to_process = daemon._scan_input_directory()
        
        if files_to_process:
            daemon.logger.info(f"Processing {len(files_to_process)} files")
            for file_path in files_to_process:
                daemon._process_file(file_path)
        else:
            daemon.logger.info("No files found to process")
        
        daemon._log_stats()
    else:
        # Run as daemon
        try:
            daemon.start()
        except KeyboardInterrupt:
            daemon.stop()


if __name__ == "__main__":
    main()