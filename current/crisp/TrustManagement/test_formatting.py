#!/usr/bin/env python3
"""
Test Output Formatting Utility for CRISP User Management System

This module provides consistent, visually clear formatting for all test outputs
to make pass/fail status easy to scan and understand at a glance.
"""

import sys
from typing import List, Tuple, Dict, Any
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    # Main colors
    GREEN = '\033[92m'    # Success/Pass
    RED = '\033[91m'      # Failure/Error
    YELLOW = '\033[93m'   # Warning/Skip
    BLUE = '\033[94m'     # Info
    CYAN = '\033[96m'     # Headers
    MAGENTA = '\033[95m'  # Special
    WHITE = '\033[97m'    # Emphasis
    GRAY = '\033[90m'     # Subdued
    
    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'     # Reset to default


class TestFormatter:
    """Enhanced test output formatter with visual clarity"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and self._supports_color()
        self.results: List[Tuple[str, bool, str]] = []  # (test_name, passed, details)
        self.start_time = None
        self.section_level = 0
        
    def _supports_color(self) -> bool:
        """Check if the terminal supports ANSI colors"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if self.use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def print_header(self, title: str, subtitle: str = None, char: str = "="):
        """Print a formatted test suite header"""
        self.start_time = datetime.now()
        
        width = max(60, len(title) + 4)
        border = char * width
        
        print()
        print(self._colorize(border, Colors.CYAN))
        print(self._colorize(f"🛡️  {title.center(width - 4)}", Colors.CYAN + Colors.BOLD))
        if subtitle:
            print(self._colorize(f"   {subtitle.center(width - 4)}", Colors.CYAN))
        print(self._colorize(border, Colors.CYAN))
        print()
    
    def print_section(self, section_name: str, level: int = 1):
        """Print a test section header"""
        self.section_level = level
        
        if level == 1:
            icon = "📋"
            color = Colors.BLUE + Colors.BOLD
            char = "-"
        else:
            icon = "  📝"
            color = Colors.BLUE
            char = "·"
        
        width = 50
        border = char * width
        
        print(self._colorize(f"{icon} {section_name}", color))
        print(self._colorize(border, Colors.GRAY))
    
    def print_test_start(self, test_name: str):
        """Print test start indicator"""
        indent = "  " * self.section_level
        print(f"{indent}🔄 {test_name}...", end=" ", flush=True)
    
    def print_test_result(self, test_name: str, passed: bool, details: str = None, time_ms: int = None):
        """Print formatted test result"""
        # Store result for summary
        self.results.append((test_name, passed, details or ""))
        
        # Print result with clear pass/fail indicator
        if passed:
            status = self._colorize("✅ PASS", Colors.GREEN + Colors.BOLD)
        else:
            status = self._colorize("❌ FAIL", Colors.RED + Colors.BOLD)
        
        time_str = f" ({time_ms}ms)" if time_ms else ""
        print(f"{status}{time_str}")
        
        # Print details if provided
        if details:
            indent = "  " * (self.section_level + 1)
            if passed:
                detail_color = Colors.GREEN
            else:
                detail_color = Colors.RED
            
            # Split multi-line details
            for line in details.split('\n'):
                if line.strip():
                    print(f"{indent}  {self._colorize(line.strip(), detail_color)}")
    
    def print_test_inline(self, test_name: str, passed: bool, details: str = None):
        """Print test result inline (start and result together)"""
        indent = "  " * self.section_level
        
        if passed:
            status = self._colorize("✅ PASS", Colors.GREEN + Colors.BOLD)
        else:
            status = self._colorize("❌ FAIL", Colors.RED + Colors.BOLD)
        
        print(f"{indent}{status} {test_name}")
        
        # Store result
        self.results.append((test_name, passed, details or ""))
        
        # Print details if provided
        if details:
            detail_indent = indent + "      "
            if passed:
                detail_color = Colors.GREEN
            else:
                detail_color = Colors.RED
            
            for line in details.split('\n'):
                if line.strip():
                    print(f"{detail_indent}{self._colorize(line.strip(), detail_color)}")
    
    def print_warning(self, message: str):
        """Print a warning message"""
        indent = "  " * self.section_level
        print(f"{indent}⚠️  {self._colorize(message, Colors.YELLOW)}")
    
    def print_info(self, message: str):
        """Print an info message"""
        indent = "  " * self.section_level
        print(f"{indent}ℹ️  {self._colorize(message, Colors.BLUE)}")
    
    def print_error(self, message: str):
        """Print an error message"""
        indent = "  " * self.section_level
        print(f"{indent}💥 {self._colorize(message, Colors.RED + Colors.BOLD)}")
    
    def print_summary(self, additional_info: Dict[str, Any] = None):
        """Print comprehensive test summary"""
        if not self.results:
            print(self._colorize("No test results to summarize", Colors.YELLOW))
            return
        
        passed_count = sum(1 for _, passed, _ in self.results if passed)
        total_count = len(self.results)
        failed_count = total_count - passed_count
        success_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        
        # Calculate duration
        duration = ""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            duration = f" in {elapsed.total_seconds():.2f}s"
        
        print()
        print(self._colorize("═" * 60, Colors.CYAN))
        print(self._colorize("📊 TEST RESULTS SUMMARY", Colors.CYAN + Colors.BOLD))
        print(self._colorize("═" * 60, Colors.CYAN))
        print()
        
        # Overall statistics
        if success_rate == 100:
            overall_color = Colors.GREEN + Colors.BOLD
            overall_icon = "🎉"
            overall_status = "ALL TESTS PASSED"
        elif success_rate >= 80:
            overall_color = Colors.YELLOW + Colors.BOLD
            overall_icon = "⚠️"
            overall_status = "MOSTLY SUCCESSFUL"
        else:
            overall_color = Colors.RED + Colors.BOLD
            overall_icon = "🚨"
            overall_status = "TESTS FAILED"
        
        print(f"{overall_icon} {self._colorize(overall_status, overall_color)}")
        print()
        
        # Detailed statistics
        print(f"📈 Results: {self._colorize(str(passed_count), Colors.GREEN + Colors.BOLD)} passed, "
              f"{self._colorize(str(failed_count), Colors.RED + Colors.BOLD)} failed")
        print(f"📊 Success Rate: {self._colorize(f'{success_rate:.1f}%', Colors.WHITE + Colors.BOLD)}")
        if duration:
            print(f"⏱️  Duration: {self._colorize(duration[4:], Colors.GRAY)}")  # Remove " in "
        
        # Additional info
        if additional_info:
            print()
            for key, value in additional_info.items():
                print(f"📋 {key}: {self._colorize(str(value), Colors.WHITE)}")
        
        print()
        
        # Detailed results table
        if total_count > 0:
            print(self._colorize("📋 Detailed Results:", Colors.BLUE + Colors.BOLD))
            print(self._colorize("─" * 60, Colors.GRAY))
            
            for i, (test_name, passed, details) in enumerate(self.results, 1):
                status_icon = "✅" if passed else "❌"
                status_color = Colors.GREEN if passed else Colors.RED
                
                # Truncate long test names for table formatting
                display_name = test_name if len(test_name) <= 35 else test_name[:32] + "..."
                
                print(f"{status_icon} {self._colorize(display_name.ljust(38), status_color)} "
                      f"{self._colorize('PASS' if passed else 'FAIL', status_color + Colors.BOLD)}")
                
                # Show critical details inline
                if not passed and details:
                    # Show only first line of details to keep summary concise
                    first_detail = details.split('\n')[0].strip()
                    if first_detail:
                        print(f"    {self._colorize(first_detail[:50] + ('...' if len(first_detail) > 50 else ''), Colors.RED)}")
        
        print(self._colorize("─" * 60, Colors.GRAY))
        print()
        
        # Final recommendation
        if success_rate == 100:
            print(self._colorize("🎯 System is fully operational and ready for use!", Colors.GREEN + Colors.BOLD))
        elif success_rate >= 80:
            print(self._colorize("⚠️  System is mostly functional but has some issues to address.", Colors.YELLOW + Colors.BOLD))
        else:
            print(self._colorize("🔧 System has significant issues that need to be resolved.", Colors.RED + Colors.BOLD))
    
    def get_exit_code(self) -> int:
        """Get appropriate exit code based on test results"""
        if not self.results:
            return 1  # No tests run
        
        passed_count = sum(1 for _, passed, _ in self.results if passed)
        return 0 if passed_count == len(self.results) else 1


# Convenience functions for quick usage
def create_formatter(use_colors: bool = True) -> TestFormatter:
    """Create a new test formatter instance"""
    return TestFormatter(use_colors)


def print_quick_result(test_name: str, passed: bool, details: str = None):
    """Quick function to print a single test result"""
    formatter = TestFormatter()
    formatter.print_test_inline(test_name, passed, details)


def print_quick_summary(results: List[Tuple[str, bool]], title: str = "Test Results"):
    """Quick function to print a test summary"""
    formatter = TestFormatter()
    formatter.results = [(name, passed, "") for name, passed in results]
    formatter.print_header(title)
    formatter.print_summary()
    return formatter.get_exit_code()


if __name__ == "__main__":
    # Demo/test the formatter
    formatter = TestFormatter()
    
    formatter.print_header("CRISP Test Formatting Demo", "Demonstrating enhanced test output")
    
    formatter.print_section("Authentication Tests")
    formatter.print_test_inline("User Login", True, "Admin user authenticated successfully")
    formatter.print_test_inline("Password Validation", False, "Weak password rejected")
    formatter.print_test_inline("Session Management", True)
    
    formatter.print_section("API Tests", level=2)
    formatter.print_test_inline("Profile Endpoint", True, "User profile retrieved")
    formatter.print_test_inline("Rate Limiting", False, "Rate limit exceeded - 429 status")
    
    formatter.print_warning("Database connection slow")
    formatter.print_info("Using test database")
    formatter.print_error("Critical security issue detected")
    
    formatter.print_summary({
        "Environment": "Test",
        "Database": "PostgreSQL",
        "Cache": "In-Memory"
    })
    
    print(f"\nExit code would be: {formatter.get_exit_code()}")
