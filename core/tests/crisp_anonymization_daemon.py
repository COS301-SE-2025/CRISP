#!/usr/bin/env python3
"""
CRISP Anonymization Daemon

A daemon service that consumes STIX threat intelligence data from input queues,
applies anonymization based on trust levels, and outputs to feed components.

Architecture:
- Consumes from Redis/RabbitMQ queues
- Applies anonymization strategies based on trust levels
- Outputs anonymized STIX data to output queues
- Supports batch processing for high throughput
- Integrates with Django/Celery consumption component
"""

import json
import logging
import signal
import sys
import time
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import os

# Import Redis for queue management
try:
    import redis
except ImportError:
    redis = None

# Import RabbitMQ/AMQP support
try:
    import pika
except ImportError:
    pika = None

# Import the anonymization system
from crisp_anonymization import (
    AnonymizationContext,
    AnonymizationLevel,
    DataType,
    AnonymizationError
)


@dataclass
class DaemonConfig:
    """Configuration for the anonymization daemon"""
    # Queue configuration
    input_queue: str = "stix_input"
    output_queue: str = "stix_anonymized"
    error_queue: str = "stix_errors"
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # RabbitMQ configuration
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"
    
    # Processing configuration
    batch_size: int = 10
    max_retries: int = 3
    retry_delay: int = 5
    poll_interval: float = 1.0
    
    # Anonymization configuration
    default_trust_level: str = "medium"
    trust_mapping: Dict[str, str] = None
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Daemon configuration
    pidfile: Optional[str] = None
    daemon_mode: bool = False
    
    def __post_init__(self):
        if self.trust_mapping is None:
            self.trust_mapping = {
                "high": "low",
                "medium": "medium", 
                "low": "high",
                "untrusted": "full"
            }


@dataclass
class ProcessingResult:
    """Result of processing a STIX object"""
    success: bool
    original_id: str
    anonymized_data: Optional[Dict] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    trust_level: Optional[str] = None
    anonymization_level: Optional[str] = None


class AnonymizationDaemon:
    """Main daemon class for STIX anonymization"""
    
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.running = False
        self.logger = self._setup_logging()
        self.anonymization_context = AnonymizationContext()
        self.stats = {
            'processed': 0,
            'errors': 0,
            'start_time': None,
            'last_activity': None
        }
        
        # Queue connections
        self.redis_client = None
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        
        # Trust level mapping
        self.trust_levels = {
            "high": AnonymizationLevel.LOW,
            "medium": AnonymizationLevel.MEDIUM,
            "low": AnonymizationLevel.HIGH,
            "untrusted": AnonymizationLevel.FULL
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('crisp_anonymization_daemon')
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _connect_redis(self) -> bool:
        """Connect to Redis"""
        if not redis:
            self.logger.error("Redis library not available. Install with: pip install redis")
            return False
        
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.logger.info("Connected to Redis")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    def _connect_rabbitmq(self) -> bool:
        """Connect to RabbitMQ"""
        if not pika:
            self.logger.error("Pika library not available. Install with: pip install pika")
            return False
        
        try:
            credentials = pika.PlainCredentials(
                self.config.rabbitmq_user,
                self.config.rabbitmq_password
            )
            parameters = pika.ConnectionParameters(
                host=self.config.rabbitmq_host,
                port=self.config.rabbitmq_port,
                virtual_host=self.config.rabbitmq_vhost,
                credentials=credentials
            )
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            
            # Declare queues
            self.rabbitmq_channel.queue_declare(queue=self.config.input_queue, durable=True)
            self.rabbitmq_channel.queue_declare(queue=self.config.output_queue, durable=True)
            self.rabbitmq_channel.queue_declare(queue=self.config.error_queue, durable=True)
            
            self.logger.info("Connected to RabbitMQ")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def _get_trust_level_from_message(self, message: Dict) -> str:
        """Extract trust level from message metadata"""
        # Check message headers/metadata for trust level
        if 'metadata' in message and 'trust_level' in message['metadata']:
            return message['metadata']['trust_level']
        
        # Check for institution-based trust mapping
        if 'metadata' in message and 'institution' in message['metadata']:
            institution = message['metadata']['institution']
            return self.config.trust_mapping.get(institution, self.config.default_trust_level)
        
        # Default trust level
        return self.config.default_trust_level
    
    def _process_stix_object(self, stix_data: Dict, trust_level: str) -> ProcessingResult:
        """Process a single STIX object"""
        start_time = time.time()
        
        try:
            # Get anonymization level based on trust
            anonymization_level = self.trust_levels.get(trust_level, AnonymizationLevel.MEDIUM)
            
            # Extract STIX ID for tracking
            stix_id = stix_data.get('id', 'unknown')
            
            # Anonymize the STIX object
            anonymized_json = self.anonymization_context.anonymize_stix_object(
                stix_data, anonymization_level
            )
            
            # Parse back to dict
            anonymized_data = json.loads(anonymized_json)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                original_id=stix_id,
                anonymized_data=anonymized_data,
                processing_time=processing_time,
                trust_level=trust_level,
                anonymization_level=anonymization_level.value
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Failed to process STIX object: {str(e)}"
            self.logger.error(error_msg)
            
            return ProcessingResult(
                success=False,
                original_id=stix_data.get('id', 'unknown'),
                error_message=error_msg,
                processing_time=processing_time,
                trust_level=trust_level
            )
    
    def _process_batch_redis(self) -> List[ProcessingResult]:
        """Process a batch of messages from Redis"""
        results = []
        
        for _ in range(self.config.batch_size):
            try:
                # Pop message from input queue
                message_data = self.redis_client.lpop(self.config.input_queue)
                if not message_data:
                    break
                
                message = json.loads(message_data)
                trust_level = self._get_trust_level_from_message(message)
                
                # Process the STIX data
                stix_data = message.get('stix_data', message)
                result = self._process_stix_object(stix_data, trust_level)
                
                if result.success:
                    # Push to output queue
                    output_message = {
                        'original_id': result.original_id,
                        'stix_data': result.anonymized_data,
                        'metadata': {
                            'trust_level': result.trust_level,
                            'anonymization_level': result.anonymization_level,
                            'processed_at': datetime.now(timezone.utc).isoformat(),
                            'processing_time': result.processing_time
                        }
                    }
                    self.redis_client.rpush(
                        self.config.output_queue,
                        json.dumps(output_message)
                    )
                    self.stats['processed'] += 1
                else:
                    # Push to error queue
                    error_message = {
                        'original_id': result.original_id,
                        'error': result.error_message,
                        'trust_level': result.trust_level,
                        'failed_at': datetime.now(timezone.utc).isoformat()
                    }
                    self.redis_client.rpush(
                        self.config.error_queue,
                        json.dumps(error_message)
                    )
                    self.stats['errors'] += 1
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                self.stats['errors'] += 1
        
        return results
    
    def _process_batch_rabbitmq(self) -> List[ProcessingResult]:
        """Process a batch of messages from RabbitMQ"""
        results = []
        
        for _ in range(self.config.batch_size):
            try:
                method, properties, body = self.rabbitmq_channel.basic_get(
                    queue=self.config.input_queue
                )
                
                if not method:
                    break
                
                message = json.loads(body.decode('utf-8'))
                trust_level = self._get_trust_level_from_message(message)
                
                # Process the STIX data
                stix_data = message.get('stix_data', message)
                result = self._process_stix_object(stix_data, trust_level)
                
                if result.success:
                    # Publish to output queue
                    output_message = {
                        'original_id': result.original_id,
                        'stix_data': result.anonymized_data,
                        'metadata': {
                            'trust_level': result.trust_level,
                            'anonymization_level': result.anonymization_level,
                            'processed_at': datetime.now(timezone.utc).isoformat(),
                            'processing_time': result.processing_time
                        }
                    }
                    self.rabbitmq_channel.basic_publish(
                        exchange='',
                        routing_key=self.config.output_queue,
                        body=json.dumps(output_message),
                        properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
                    )
                    self.stats['processed'] += 1
                else:
                    # Publish to error queue
                    error_message = {
                        'original_id': result.original_id,
                        'error': result.error_message,
                        'trust_level': result.trust_level,
                        'failed_at': datetime.now(timezone.utc).isoformat()
                    }
                    self.rabbitmq_channel.basic_publish(
                        exchange='',
                        routing_key=self.config.error_queue,
                        body=json.dumps(error_message),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    self.stats['errors'] += 1
                
                # Acknowledge the message
                self.rabbitmq_channel.basic_ack(delivery_tag=method.delivery_tag)
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                self.stats['errors'] += 1
                # Reject the message
                if method:
                    self.rabbitmq_channel.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=False
                    )
        
        return results
    
    def _log_stats(self):
        """Log processing statistics"""
        if self.stats['start_time']:
            uptime = time.time() - self.stats['start_time']
            rate = self.stats['processed'] / uptime if uptime > 0 else 0
            
            self.logger.info(
                f"Stats - Processed: {self.stats['processed']}, "
                f"Errors: {self.stats['errors']}, "
                f"Rate: {rate:.2f} msg/sec, "
                f"Uptime: {uptime:.0f}s"
            )
    
    def start(self):
        """Start the daemon"""
        self.logger.info("Starting CRISP Anonymization Daemon")
        
        # Connect to message queues (skip if running in local mode)
        if not hasattr(self, 'local_mode') or not self.local_mode:
            if self.redis_client is None and not self._connect_redis():
                if not self._connect_rabbitmq():
                    self.logger.error("Failed to connect to any message queue")
                    return False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        self.logger.info("Daemon started successfully")
        
        # Main processing loop
        last_stats_log = time.time()
        
        while self.running:
            try:
                # Process batch of messages
                if self.redis_client:
                    results = self._process_batch_redis()
                else:
                    results = self._process_batch_rabbitmq()
                
                if results:
                    self.stats['last_activity'] = time.time()
                    self.logger.debug(f"Processed batch of {len(results)} messages")
                
                # Log stats periodically
                if time.time() - last_stats_log > 60:  # Every minute
                    self._log_stats()
                    last_stats_log = time.time()
                
                # Sleep if no messages were processed
                if not results:
                    time.sleep(self.config.poll_interval)
                    
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(self.config.retry_delay)
        
        self.logger.info("Daemon stopped")
        return True
    
    def stop(self):
        """Stop the daemon"""
        self.logger.info("Stopping daemon...")
        self.running = False
        
        # Close connections
        if self.rabbitmq_connection:
            self.rabbitmq_connection.close()
        
        self._log_stats()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}")
        self.stop()


def load_config_from_file(config_file: str) -> DaemonConfig:
    """Load configuration from file"""
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_path, 'r') as f:
        if config_path.suffix.lower() == '.json':
            config_data = json.load(f)
        else:
            # Assume it's a simple key=value format
            config_data = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config_data[key.strip()] = value.strip()
    
    return DaemonConfig(**config_data)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='CRISP Anonymization Daemon')
    parser.add_argument('--config', '-c', help='Configuration file')
    parser.add_argument('--daemon', '-d', action='store_true', help='Run as daemon')
    parser.add_argument('--pidfile', '-p', help='PID file location')
    parser.add_argument('--log-level', '-l', default='INFO', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Log level')
    parser.add_argument('--log-file', help='Log file location')
    
    # Queue configuration
    parser.add_argument('--input-queue', default='stix_input', help='Input queue name')
    parser.add_argument('--output-queue', default='stix_anonymized', help='Output queue name')
    parser.add_argument('--error-queue', default='stix_errors', help='Error queue name')
    
    # Redis configuration
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')
    parser.add_argument('--redis-db', type=int, default=0, help='Redis database')
    
    # Processing configuration
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    parser.add_argument('--poll-interval', type=float, default=1.0, help='Poll interval in seconds')
    parser.add_argument('--default-trust', default='medium', 
                        choices=['high', 'medium', 'low', 'untrusted'],
                        help='Default trust level')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = DaemonConfig()
    
    # Override with command line arguments
    if args.daemon:
        config.daemon_mode = True
    if args.pidfile:
        config.pidfile = args.pidfile
    if args.log_level:
        config.log_level = args.log_level
    if args.log_file:
        config.log_file = args.log_file
    if args.input_queue:
        config.input_queue = args.input_queue
    if args.output_queue:
        config.output_queue = args.output_queue
    if args.error_queue:
        config.error_queue = args.error_queue
    if args.redis_host:
        config.redis_host = args.redis_host
    if args.redis_port:
        config.redis_port = args.redis_port
    if args.redis_db:
        config.redis_db = args.redis_db
    if args.batch_size:
        config.batch_size = args.batch_size
    if args.poll_interval:
        config.poll_interval = args.poll_interval
    if args.default_trust:
        config.default_trust_level = args.default_trust
    
    # Create and start daemon
    daemon = AnonymizationDaemon(config)
    
    # Write PID file if specified
    if config.pidfile:
        with open(config.pidfile, 'w') as f:
            f.write(str(os.getpid()))
    
    try:
        daemon.start()
    except KeyboardInterrupt:
        daemon.stop()
    finally:
        # Clean up PID file
        if config.pidfile and Path(config.pidfile).exists():
            Path(config.pidfile).unlink()


if __name__ == "__main__":
    main()