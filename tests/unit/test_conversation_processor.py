"""
Unit tests for ConversationProcessor.

This module contains comprehensive unit tests for the ConversationProcessor
class, ensuring it correctly reads and processes Marcus log files.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add the source directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from processors.conversation_processor import (
    ConversationProcessor,
    ConversationStreamProcessor,
    ConversationType
)


class TestConversationProcessor(unittest.TestCase):
    """Test suite for ConversationProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test logs
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir)
        
        # Sample conversation data
        self.sample_conversations = [
            {
                "timestamp": "2024-01-15T10:00:00Z",
                "type": "worker_to_pm",
                "source": "worker_1",
                "message": "Task completed",
                "task_id": "TASK-123"
            },
            {
                "timestamp": "2024-01-15T10:05:00Z",
                "type": "pm_decision",
                "confidence_score": 0.85,
                "message": "Assign next task",
                "metadata": {"task_id": "TASK-124"}
            },
            {
                "timestamp": "2024-01-15T10:10:00Z",
                "type": "blocker",
                "worker_id": "worker_2",
                "message": "Database connection failed",
                "severity": "high"
            }
        ]
        
        # Write sample data to a test log file
        self.log_file = self.log_dir / "test_conversations.jsonl"
        with open(self.log_file, 'w') as f:
            for conv in self.sample_conversations:
                f.write(json.dumps(conv) + '\n')
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_valid_directory(self):
        """Test processor initialization with valid directory."""
        processor = ConversationProcessor(self.log_dir)
        self.assertEqual(processor.log_dir, self.log_dir)
    
    def test_initialization_with_invalid_directory(self):
        """Test processor initialization with non-existent directory."""
        with self.assertRaises(ValueError) as context:
            ConversationProcessor("/non/existent/path")
        
        self.assertIn("Log directory does not exist", str(context.exception))
    
    def test_get_recent_conversations(self):
        """Test retrieving recent conversations."""
        processor = ConversationProcessor(self.log_dir)
        conversations = processor.get_recent_conversations(limit=10)
        
        # Should return all 3 conversations
        self.assertEqual(len(conversations), 3)
        
        # Should be sorted by timestamp (newest first)
        self.assertEqual(conversations[0]["timestamp"], "2024-01-15T10:10:00Z")
        self.assertEqual(conversations[1]["timestamp"], "2024-01-15T10:05:00Z")
        self.assertEqual(conversations[2]["timestamp"], "2024-01-15T10:00:00Z")
    
    def test_get_recent_conversations_with_limit(self):
        """Test retrieving conversations with limit."""
        processor = ConversationProcessor(self.log_dir)
        conversations = processor.get_recent_conversations(limit=2)
        
        # Should return only 2 conversations
        self.assertEqual(len(conversations), 2)
        
        # Should be the 2 most recent
        self.assertEqual(conversations[0]["type"], "blocker")
        self.assertEqual(conversations[1]["type"], "pm_decision")
    
    def test_get_conversations_in_range(self):
        """Test retrieving conversations within time range."""
        processor = ConversationProcessor(self.log_dir)
        
        # Set time range to include only middle conversation
        start_time = datetime(2024, 1, 15, 10, 3, 0)
        end_time = datetime(2024, 1, 15, 10, 7, 0)
        
        conversations = processor.get_conversations_in_range(
            start_time=start_time,
            end_time=end_time
        )
        
        # Should return only the pm_decision
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]["type"], "pm_decision")
    
    def test_get_conversations_with_type_filter(self):
        """Test filtering conversations by type."""
        processor = ConversationProcessor(self.log_dir)
        
        start_time = datetime(2024, 1, 15, 9, 0, 0)
        end_time = datetime(2024, 1, 15, 11, 0, 0)
        
        conversations = processor.get_conversations_in_range(
            start_time=start_time,
            end_time=end_time,
            conversation_type="worker_to_pm"
        )
        
        # Should return only worker_to_pm conversations
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]["type"], "worker_to_pm")
        self.assertEqual(conversations[0]["source"], "worker_1")
    
    def test_get_agent_conversations(self):
        """Test retrieving conversations for specific agent."""
        processor = ConversationProcessor(self.log_dir)
        
        # Get conversations for worker_1
        conversations = processor.get_agent_conversations("worker_1", limit=10)
        
        # Should return only conversations involving worker_1
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]["source"], "worker_1")
        
        # Get conversations for worker_2
        conversations = processor.get_agent_conversations("worker_2", limit=10)
        
        # Should return only conversations involving worker_2
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]["worker_id"], "worker_2")
    
    def test_get_conversation_analytics(self):
        """Test conversation analytics calculation."""
        processor = ConversationProcessor(self.log_dir)
        
        # Use a large time window to include test data from 2024
        analytics = processor.get_conversation_analytics(hours=24*365*2)  # 2 years
        
        # Check structure
        self.assertIn("total_conversations", analytics)
        self.assertIn("conversations_by_type", analytics)
        self.assertIn("active_agents", analytics)
        self.assertIn("average_confidence", analytics)
        self.assertIn("blockers", analytics)
        self.assertIn("time_range", analytics)
        
        # Check values
        self.assertEqual(analytics["total_conversations"], 3)
        self.assertEqual(analytics["conversations_by_type"]["worker_to_pm"], 1)
        self.assertEqual(analytics["conversations_by_type"]["pm_decision"], 1)
        self.assertEqual(analytics["conversations_by_type"]["blocker"], 1)
        self.assertEqual(analytics["active_agents"], 2)  # worker_1 and worker_2
        self.assertEqual(analytics["average_confidence"], 0.85)
        self.assertEqual(analytics["blockers"]["total"], 1)
        self.assertEqual(analytics["blockers"]["by_severity"]["high"], 1)
    
    def test_handle_invalid_json_lines(self):
        """Test handling of invalid JSON lines in log files."""
        # Create a log file with some invalid JSON
        invalid_log = self.log_dir / "invalid.jsonl"
        with open(invalid_log, 'w') as f:
            f.write('{"valid": "json"}\n')
            f.write('invalid json line\n')
            f.write('{"another": "valid"}\n')
        
        processor = ConversationProcessor(self.log_dir)
        conversations = processor.get_recent_conversations()
        
        # Should skip invalid lines and return valid ones
        # We have 3 from setup + 2 valid from this test
        self.assertEqual(len(conversations), 5)
    
    def test_handle_missing_timestamps(self):
        """Test handling of conversations without timestamps."""
        # Create conversations without timestamps
        no_timestamp_log = self.log_dir / "no_timestamp.jsonl"
        with open(no_timestamp_log, 'w') as f:
            f.write('{"type": "test", "message": "no timestamp"}\n')
            f.write('{"type": "test2", "timestamp": "2024-01-15T12:00:00Z"}\n')
        
        processor = ConversationProcessor(self.log_dir)
        
        # Time range query should skip entries without timestamps
        start_time = datetime(2024, 1, 15, 11, 0, 0)
        end_time = datetime(2024, 1, 15, 13, 0, 0)
        
        conversations = processor.get_conversations_in_range(
            start_time=start_time,
            end_time=end_time
        )
        
        # Should only return the one with valid timestamp
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]["type"], "test2")
    
    def test_empty_log_directory(self):
        """Test behavior with empty log directory."""
        # Create empty directory
        empty_dir = Path(self.temp_dir) / "empty"
        empty_dir.mkdir()
        
        processor = ConversationProcessor(empty_dir)
        conversations = processor.get_recent_conversations()
        
        # Should return empty list
        self.assertEqual(len(conversations), 0)
        
        # Analytics should handle empty data gracefully
        analytics = processor.get_conversation_analytics()
        self.assertEqual(analytics["total_conversations"], 0)
        self.assertEqual(analytics["active_agents"], 0)
        self.assertEqual(analytics["average_confidence"], 0.0)


class TestConversationStreamProcessor(unittest.TestCase):
    """Test suite for ConversationStreamProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir)
        
        # Create initial log file
        self.log_file = self.log_dir / "stream_test.jsonl"
        self.initial_data = [
            {"timestamp": "2024-01-15T10:00:00Z", "type": "test1"},
            {"timestamp": "2024-01-15T10:01:00Z", "type": "test2"}
        ]
        
        with open(self.log_file, 'w') as f:
            for data in self.initial_data:
                f.write(json.dumps(data) + '\n')
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_stream_processor_initialization(self):
        """Test stream processor initialization."""
        processor = ConversationStreamProcessor(self.log_dir)
        self.assertEqual(processor.log_dir, self.log_dir)
        self.assertIsInstance(processor.processor, ConversationProcessor)
        self.assertEqual(len(processor._last_read_positions), 0)
    
    def test_get_new_conversations_first_read(self):
        """Test getting new conversations on first read."""
        processor = ConversationStreamProcessor(self.log_dir)
        
        # First read should return all existing conversations
        new_convs = processor.get_new_conversations()
        self.assertEqual(len(new_convs), 2)
        self.assertEqual(new_convs[0]["type"], "test1")
        self.assertEqual(new_convs[1]["type"], "test2")
    
    def test_get_new_conversations_incremental(self):
        """Test incremental reading of new conversations."""
        processor = ConversationStreamProcessor(self.log_dir)
        
        # First read
        processor.get_new_conversations()
        
        # Add new conversations to the file
        with open(self.log_file, 'a') as f:
            f.write('{"timestamp": "2024-01-15T10:02:00Z", "type": "test3"}\n')
            f.write('{"timestamp": "2024-01-15T10:03:00Z", "type": "test4"}\n')
        
        # Second read should only return new conversations
        new_convs = processor.get_new_conversations()
        self.assertEqual(len(new_convs), 2)
        self.assertEqual(new_convs[0]["type"], "test3")
        self.assertEqual(new_convs[1]["type"], "test4")
    
    def test_handle_file_rotation(self):
        """Test handling when log files are rotated."""
        processor = ConversationStreamProcessor(self.log_dir)
        
        # First read
        processor.get_new_conversations()
        
        # Simulate file rotation - create new file
        new_log = self.log_dir / "stream_test_new.jsonl"
        with open(new_log, 'w') as f:
            f.write('{"timestamp": "2024-01-15T10:04:00Z", "type": "rotated"}\n')
        
        # Touch the new file to make it newer
        import time
        time.sleep(0.01)
        new_log.touch()
        
        # Should read from the newest file
        new_convs = processor.get_new_conversations()
        self.assertEqual(len(new_convs), 1)
        self.assertEqual(new_convs[0]["type"], "rotated")
    
    def test_handle_io_errors(self):
        """Test handling of I/O errors during reading."""
        processor = ConversationStreamProcessor(self.log_dir)
        
        # Make the file unreadable (on Unix-like systems)
        if os.name != 'nt':  # Skip on Windows
            os.chmod(self.log_file, 0o000)
            
            # Should handle the error gracefully
            new_convs = processor.get_new_conversations()
            self.assertEqual(len(new_convs), 0)
            
            # Restore permissions
            os.chmod(self.log_file, 0o644)


class TestConversationType(unittest.TestCase):
    """Test suite for ConversationType enum."""
    
    def test_conversation_type_values(self):
        """Test ConversationType enum values."""
        self.assertEqual(ConversationType.WORKER_TO_PM.value, "worker_to_pm")
        self.assertEqual(ConversationType.PM_TO_WORKER.value, "pm_to_worker")
        self.assertEqual(ConversationType.PM_TO_KANBAN.value, "pm_to_kanban")
        self.assertEqual(ConversationType.KANBAN_TO_PM.value, "kanban_to_pm")
        self.assertEqual(ConversationType.INTERNAL_THINKING.value, "internal_thinking")
        self.assertEqual(ConversationType.DECISION.value, "decision")
        self.assertEqual(ConversationType.ERROR.value, "error")
    
    def test_conversation_type_membership(self):
        """Test ConversationType enum membership."""
        # Valid types
        self.assertIn(ConversationType.WORKER_TO_PM, ConversationType)
        self.assertIn(ConversationType.DECISION, ConversationType)
        
        # String values are not members - use try/except for Python 3.11 compatibility
        try:
            # In Python < 3.12, this raises TypeError
            result = "worker_to_pm" in ConversationType
            # In Python >= 3.12, it returns False
            self.assertFalse(result)
        except TypeError:
            # This is expected in Python < 3.12
            pass


if __name__ == '__main__':
    unittest.main()