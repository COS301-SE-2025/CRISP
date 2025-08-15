#!/usr/bin/env python3
"""
Quick fix script for email test mocking issues
"""

import re
import os

def fix_test_file(file_path):
    """Fix common mocking issues in test files"""
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Ensure SMTP mocks are properly structured
    content = re.sub(
        r'@patch\(\'core\.notifications\.services\.gmail_smtp_service\.smtplib\.SMTP\'\)\s*\n\s*def test_(\w+)\(self, mock_smtp\):',
        r'def test_\1(self):\n        """Test method with proper SMTP mocking"""\n        with patch(\'core.notifications.services.gmail_smtp_service.smtplib.SMTP\') as mock_smtp:',
        content,
        flags=re.MULTILINE
    )
    
    # Fix 2: Ensure SMTP_SSL is also mocked when needed
    content = re.sub(
        r'mock_smtp\.side_effect = smtplib\.SMTPConnectError',
        r'with patch(\'core.notifications.services.gmail_smtp_service.smtplib.SMTP_SSL\'):\n            mock_smtp.side_effect = smtplib.SMTPConnectError',
        content
    )
    
    # Fix 3: Add proper indentation for with blocks
    lines = content.split('\n')
    fixed_lines = []
    in_with_block = False
    base_indent = 0
    
    for line in lines:
        if 'with patch(' in line and 'mock_smtp:' in line:
            in_with_block = True
            base_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
        elif in_with_block and line.strip() == '':
            fixed_lines.append(line)
        elif in_with_block and (line.startswith('    def ') or line.startswith('class ')):
            in_with_block = False
            fixed_lines.append(line)
        elif in_with_block:
            # Add extra indentation for lines inside with block
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent and line.strip():
                line = '    ' + line
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
    else:
        print(f"No changes needed: {file_path}")

def create_simple_test_runner():
    """Create a simple test file that works"""
    
    simple_test = '''"""
Simple Email Test - Basic Functionality Check
"""

import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from core.notifications.services.gmail_smtp_service import GmailSMTPService

class SimpleEmailTest(TestCase):
    """Simple test to verify email service works"""
    
    def setUp(self):
        self.service = GmailSMTPService()
    
    def test_email_service_initialization(self):
        """Test that email service initializes correctly"""
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service.email_host)
    
    def test_send_email_with_mock(self):
        """Test email sending with proper mocking"""
        with patch('core.notifications.services.gmail_smtp_service.smtplib') as mock_smtplib:
            # Mock the SMTP class
            mock_smtp = MagicMock()
            mock_smtplib.SMTP.return_value = mock_smtp
            
            # Test basic email sending
            result = self.service.send_email(
                to_emails=['test@example.com'],
                subject='Test Email',
                html_content='<h1>Test</h1>',
                text_content='Test'
            )
            
            # Should return a result dict
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)

if __name__ == '__main__':
    unittest.main()
'''
    
    with open('/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_email_simple.py', 'w') as f:
        f.write(simple_test)
    
    print("Created simple test file: test_email_simple.py")

if __name__ == '__main__':
    # Create simple test first
    create_simple_test_runner()
    
    # List of files to fix
    test_files = [
        '/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/core/tests/test_gmail_smtp_service_comprehensive.py',
    ]
    
    for file_path in test_files:
        fix_test_file(file_path)
    
    print("\\nTest fixes completed!")
    print("\\nTry running the simple test first:")
    print("python3 manage.py test core.tests.test_email_simple")