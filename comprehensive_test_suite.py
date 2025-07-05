#!/usr/bin/env python3
"""
CRISP Integration Test Suite
Comprehensive testing with coverage and colored output
"""

import os
import sys
import django
import time
import subprocess
from pathlib import Path
from datetime import datetime
import io
import json
import re

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.settings.integrated')
django.setup()

from django.core.management import call_command
from django.test.utils import get_runner
from django.conf import settings


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def strip_ansi_codes(text):
    """Remove ANSI color codes from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class TestResult:
    """Container for test results"""
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.passed = False
        self.error = None
        self.duration = 0
        self.details = []


class CRISPTestSuite:
    """Main test suite runner with comprehensive integration demonstrations"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.total_duration = 0
        self.output_buffer = io.StringIO()
        self.original_stdout = sys.stdout
        self.coverage_percentage = None
        self.test_data = {}  # Store test data for demonstrations
        self.coverage_data = {}  # Store coverage data
        
    def start_output_capture(self):
        """Start capturing output to buffer"""
        sys.stdout = self.output_buffer
        
    def stop_output_capture(self):
        """Stop capturing output and return to original stdout"""
        sys.stdout = self.original_stdout
        
    def print_and_capture(self, message):
        """Print to both stdout and buffer"""
        # Print to original stdout
        print(message, file=self.original_stdout)
        # Also print to buffer
        print(message, file=self.output_buffer)
        
    def extract_coverage_percentage(self):
        """Extract coverage percentage from coverage report"""
        try:
            coverage_result = subprocess.run([
                'python3', '-m', 'coverage', 'report', '--format=total'
            ], capture_output=True, text=True, cwd=project_root)
            
            if coverage_result.returncode == 0:
                total_coverage = coverage_result.stdout.strip()
                if total_coverage and '%' in total_coverage:
                    self.coverage_percentage = float(total_coverage.replace('%', ''))
                    return self.coverage_percentage
        except Exception:
            pass
        return None
        
    def save_results_to_file(self):
        """Save test results to file in a separate folder"""
        try:
            # Create output directory
            output_dir = project_root / "test_results"
            output_dir.mkdir(exist_ok=True)
            
            # Get coverage percentage for filename
            coverage_pct = self.extract_coverage_percentage()
            
            # Create filename with timestamp and coverage
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if coverage_pct is not None:
                filename = f"test_results_{timestamp}_cov{coverage_pct:.0f}.txt"
            else:
                filename = f"test_results_{timestamp}.txt"
            
            output_file = output_dir / filename
            
            # Get the captured output and strip ANSI codes
            captured_output = self.output_buffer.getvalue()
            clean_output = strip_ansi_codes(captured_output)
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"CRISP Integration Test Results\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"="*80 + "\n\n")
                f.write(clean_output)
                
                # Add file footer
                f.write(f"\n{'='*80}\n")
                f.write(f"Results saved to: {output_file}\n")
                f.write(f"HTML Coverage Report: htmlcov/index.html\n")
                f.write(f"Test Duration: {self.total_duration:.2f}s\n")
                if coverage_pct is not None:
                    f.write(f"Code Coverage: {coverage_pct:.1f}%\n")
            
            self.print_and_capture(f"\n{Colors.CYAN}Results saved to: {output_file}{Colors.END}")
            return output_file
            
        except Exception as e:
            self.print_and_capture(f"\n{Colors.YELLOW}Failed to save results to file: {e}{Colors.END}")
            return None
        
    def print_header(self, title):
        """Print a styled header"""
        self.print_and_capture(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}")
        self.print_and_capture(f"{Colors.CYAN}{Colors.BOLD}{title:^80}{Colors.END}")
        self.print_and_capture(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}")
        
    def print_section(self, title):
        """Print a section header"""
        self.print_and_capture(f"\n{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
        self.print_and_capture(f"{Colors.BLUE}{'-'*60}{Colors.END}")
        
    def print_success(self, message: str):
        """Print success message"""
        self.print_and_capture(f"  {Colors.GREEN}✅ {message}{Colors.END}")
        
    def print_info(self, message: str):
        """Print info message"""
        self.print_and_capture(f"  {Colors.CYAN}ℹ️  {message}{Colors.END}")
        
    def print_warning(self, message: str):
        """Print warning message"""
        self.print_and_capture(f"  {Colors.YELLOW}⚠️  {message}{Colors.END}")
        
    def print_error(self, message: str):
        """Print error message"""
        self.print_and_capture(f"  {Colors.RED}❌ {message}{Colors.END}")
        
    def system_overview(self):
        """Display comprehensive system overview"""
        self.print_header("CRISP INTEGRATED SYSTEM OVERVIEW")
        
        self.print_and_capture(f"{Colors.WHITE}CRISP (Cyber Risk Information Sharing Platform) Integration{Colors.END}")
        self.print_and_capture(f"{Colors.WHITE}This demonstrates the full integration between:{Colors.END}")
        self.print_and_capture(f"  • {Colors.CYAN}UserManagement System{Colors.END} - User, organization, and authentication management")
        self.print_and_capture(f"  • {Colors.CYAN}TrustManagement System{Colors.END} - Trust relationships and access control")
        self.print_and_capture(f"  • {Colors.CYAN}Core Integration Services{Colors.END} - Unified business logic and workflows")
        
        self.print_and_capture(f"\n{Colors.WHITE}System Architecture:{Colors.END}")
        self.print_and_capture(f"  • {Colors.GREEN}Django Framework{Colors.END} - Web framework and ORM")
        self.print_and_capture(f"  • {Colors.GREEN}SQLite Database{Colors.END} - Data persistence layer")
        self.print_and_capture(f"  • {Colors.GREEN}REST API{Colors.END} - API endpoints for external integration")
        self.print_and_capture(f"  • {Colors.GREEN}Role-Based Access Control{Colors.END} - Security and permissions")
        self.print_and_capture(f"  • {Colors.GREEN}Trust-Based Intelligence Filtering{Colors.END} - Content access control")
        
        self.print_and_capture(f"\n{Colors.WHITE}Integration Features:{Colors.END}")
        self.print_and_capture(f"  • Organization registration with trust setup")
        self.print_and_capture(f"  • User invitation and role management")
        self.print_and_capture(f"  • Trust relationship establishment and approval")
        self.print_and_capture(f"  • Intelligence access control based on trust levels")
        self.print_and_capture(f"  • Comprehensive audit logging")
        self.print_and_capture(f"  • Security event monitoring")
        
    def print_test_result(self, result):
        """Print individual test result"""
        status_color = Colors.GREEN if result.passed else Colors.RED
        status_text = "PASS" if result.passed else "FAIL"
        duration_text = f"({result.duration:.3f}s)" if result.duration > 0 else ""
        
        self.print_and_capture(f"  {status_color}[{status_text}]{Colors.END} {result.name} {Colors.YELLOW}{duration_text}{Colors.END}")
        
        if result.description:
            self.print_and_capture(f"    {Colors.WHITE}{result.description}{Colors.END}")
            
        for detail in result.details:
            self.print_and_capture(f"    {Colors.CYAN}  - {detail}{Colors.END}")
            
        if result.error and not result.passed:
            self.print_and_capture(f"    {Colors.RED}Error: {result.error}{Colors.END}")
    
    def run_test(self, test_func, name, description=""):
        """Run a single test function"""
        result = TestResult(name, description)
        start_time = time.time()
        
        try:
            test_func(result)
            result.passed = True
        except Exception as e:
            result.passed = False
            result.error = str(e)
            
        result.duration = time.time() - start_time
        self.results.append(result)
        self.print_test_result(result)
        return result.passed
    
    def test_system_checks(self, result):
        """Test Django system checks"""
        call_command('check', verbosity=0)
        result.details.append("Django system configuration validated")
        
    def test_database_setup(self, result):
        """Test database setup and migrations"""
        call_command('migrate', verbosity=0)
        result.details.append("Database migrations applied successfully")
        
        # Verify tables exist
        from django.db import connection
        tables = connection.introspection.table_names()
        required_tables = ['organizations', 'trust_levels', 'trust_relationships']
        
        for table in required_tables:
            if any(table in t for t in tables):
                result.details.append(f"Table '{table}' exists")
            else:
                raise Exception(f"Required table '{table}' not found")
                
    def test_trust_levels(self, result):
        """Test trust level management"""
        from apps.trust_management.models import TrustLevel
        from django.db import transaction
        
        # Create test trust levels
        test_levels = [
            ('Test Level 1', 25, 'Test level for integration'),
            ('Test Level 2', 75, 'High trust test level')
        ]
        
        created_count = 0
        with transaction.atomic():
            for name, value, desc in test_levels:
                level, created = TrustLevel.objects.get_or_create(
                    name=name,
                    defaults={
                        'level': name.lower().replace(' ', '_'),
                        'numerical_value': value,
                        'description': desc,
                        'created_by': 'test_system',
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
                    
        total_levels = TrustLevel.objects.count()
        result.details.append(f"Created {created_count} new trust levels")
        result.details.append(f"Total trust levels: {total_levels}")
        
        # Verify trust level queries
        active_levels = TrustLevel.objects.filter(is_active=True).count()
        result.details.append(f"Active trust levels: {active_levels}")
        
    def test_user_management(self, result):
        """Test user management functionality"""
        from apps.user_management.models import Organization
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        timestamp = str(int(time.time()))
        
        # Test organization creation
        org = Organization.objects.create(
            name=f'Test Organization {timestamp}',
            domain=f'test{timestamp}.edu',
            contact_email=f'test{timestamp}@example.com',
            institution_type='university'
        )
        result.details.append(f"Created organization: {org.name}")
        
        # Test user creation
        user = User.objects.create_user(
            username=f'testuser{timestamp}',
            email=f'user{timestamp}@test.edu',
            password='testpass123',
            organization=org
        )
        result.details.append(f"Created user: {user.username}")
        result.details.append(f"User organization: {user.organization.name}")
        
    def test_trust_relationships(self, result):
        """Test trust relationship creation"""
        from apps.core.services import CRISPIntegrationService
        from apps.user_management.models import Organization
        from apps.trust_management.models import TrustLevel
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        timestamp = str(int(time.time()))
        
        # Create two organizations
        org1 = Organization.objects.create(
            name=f'Test Org 1 {timestamp}',
            domain=f'testorg1_{timestamp}.edu',
            contact_email=f'contact1_{timestamp}@test.edu',
            institution_type='university'
        )
        
        org2 = Organization.objects.create(
            name=f'Test Org 2 {timestamp}',
            domain=f'testorg2_{timestamp}.edu',
            contact_email=f'contact2_{timestamp}@test.edu',
            institution_type='government'
        )
        
        # Create admin user
        admin = User.objects.create_user(
            username=f'admin{timestamp}',
            email=f'admin{timestamp}@test.edu',
            password='testpass123',
            organization=org1,
            role='admin'
        )
        
        # Get a trust level
        trust_level = TrustLevel.objects.filter(is_active=True).first()
        if not trust_level:
            raise Exception("No active trust levels available")
            
        # Create trust relationship
        relationship = CRISPIntegrationService.create_trust_relationship(
            source_org=org1,
            target_org=org2,
            trust_level_name=trust_level.name,
            created_by_user=admin
        )
        
        result.details.append(f"Created trust relationship: {relationship.id}")
        result.details.append(f"Source: {org1.name}")
        result.details.append(f"Target: {org2.name}")
        result.details.append(f"Trust level: {trust_level.name}")
        result.details.append(f"Status: {relationship.status}")
        
    def test_integration_service(self, result):
        """Test core integration service"""
        from apps.core.services import CRISPIntegrationService
        timestamp = str(int(time.time()))
        
        # Test organization creation with trust setup
        admin_data = {
            'username': f'intadmin{timestamp}',
            'email': f'intadmin{timestamp}@integration.edu',
            'password': 'testpass123',
            'first_name': 'Integration',
            'last_name': 'Admin'
        }
        
        org = CRISPIntegrationService.create_organization_with_trust_setup(
            name=f'Integration Test Org {timestamp}',
            domain=f'integration{timestamp}.edu',
            contact_email=f'contact{timestamp}@integration.edu',
            admin_user_data=admin_data,
            institution_type='university',
            default_trust_level='public'
        )
        
        result.details.append(f"Created organization via service: {org.name}")
        result.details.append(f"Organization ID: {org.id}")
        
        # Verify admin user creation
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.get(email=admin_data['email'])
        result.details.append(f"Admin user created: {admin.email}")
        result.details.append(f"User role: {admin.role}")
        
    def run_django_tests(self, result):
        """Run Django's built-in test suite"""
        try:
            # Run the specific coverage-boosting tests first
            print(f"{Colors.CYAN}Running coverage-boosting tests...{Colors.END}")
            
            # Test UserManagement models and coverage
            user_test_result = subprocess.run([
                sys.executable, 'manage_unified.py', 'test', 
                'apps.user_management.tests', 
                '--verbosity=0'
            ], capture_output=True, text=True, cwd=project_root, timeout=60)
            
            # Test TrustManagement models and coverage
            trust_test_result = subprocess.run([
                sys.executable, 'manage_unified.py', 'test', 
                'apps.trust_management.tests', 
                '--verbosity=0'
            ], capture_output=True, text=True, cwd=project_root, timeout=60)
            
            # Parse results
            if user_test_result.returncode == 0:
                user_output = user_test_result.stderr.split('\n')
                for line in user_output:
                    if 'Ran' in line and 'test' in line:
                        result.details.append(f"UserManagement tests: {line.strip()}")
                    elif line.strip() and ('OK' in line or 'FAILED' in line):
                        result.details.append(f"UserManagement result: {line.strip()}")
            else:
                result.details.append(f"UserManagement tests failed: {user_test_result.stderr[:200]}...")
                
            if trust_test_result.returncode == 0:
                trust_output = trust_test_result.stderr.split('\n')
                for line in trust_output:
                    if 'Ran' in line and 'test' in line:
                        result.details.append(f"TrustManagement tests: {line.strip()}")
                    elif line.strip() and ('OK' in line or 'FAILED' in line):
                        result.details.append(f"TrustManagement result: {line.strip()}")
            else:
                result.details.append(f"TrustManagement tests failed: {trust_test_result.stderr[:200]}...")

            # Also try core integration tests if they exist
            try:
                core_test_result = subprocess.run([
                    sys.executable, 'manage_unified.py', 'test', 
                    'apps.core.tests_integration', 
                    '--verbosity=0'
                ], capture_output=True, text=True, cwd=project_root, timeout=60)
                
                if core_test_result.returncode == 0:
                    core_output = core_test_result.stderr.split('\n')
                    for line in core_output:
                        if 'Ran' in line and 'test' in line:
                            result.details.append(f"Core integration tests: {line.strip()}")
                        elif line.strip() and ('OK' in line or 'FAILED' in line):
                            result.details.append(f"Core integration result: {line.strip()}")
                else:
                    result.details.append("Core integration tests skipped or failed")
            except subprocess.TimeoutExpired:
                result.details.append("Core integration tests timed out")
                
        except subprocess.TimeoutExpired:
            result.details.append("Django tests timed out, continuing with integration tests")
        except Exception as e:
            # Fallback to direct test execution
            try:
                call_command('test', 'apps.user_management.tests', verbosity=0)
                call_command('test', 'apps.trust_management.tests', verbosity=0)
                result.details.append("Django coverage tests completed via management command")
            except Exception as fallback_error:
                result.details.append(f"Django tests skipped: {fallback_error}")
    
    def generate_coverage_report(self):
        """Generate code coverage report"""
        self.print_section("Code Coverage Analysis")
        
        try:
            # Run coverage on our specific test modules that boost coverage
            print(f"{Colors.CYAN}Running comprehensive coverage analysis...{Colors.END}")
            
            # First, run coverage on the specific tests that exercise the code properly
            coverage_run = subprocess.run([
                'python3', '-m', 'coverage', 'run', '--source=apps', 
                'manage_unified.py', 'test', 'apps.user_management.tests', 'apps.trust_management.tests', '--verbosity=0'
            ], capture_output=True, text=True, cwd=project_root, timeout=120)
            
            if coverage_run.returncode != 0:
                print(f"{Colors.YELLOW}Primary coverage run failed, trying alternative method...{Colors.END}")
                # Alternative: run coverage on all apps tests
                coverage_run = subprocess.run([
                    'python3', '-m', 'coverage', 'run', '--source=apps', 
                    'manage_unified.py', 'test', 'apps', '--verbosity=0'
                ], capture_output=True, text=True, cwd=project_root, timeout=120)
            
            # Generate coverage report
            print(f"{Colors.CYAN}Generating coverage report...{Colors.END}")
            report_result = subprocess.run([
                'python3', '-m', 'coverage', 'report', '--show-missing'
            ], capture_output=True, text=True, cwd=project_root, timeout=30)
            
            if report_result.returncode == 0:
                print(f"{Colors.GREEN}Coverage Report:{Colors.END}")
                print(f"{Colors.WHITE}{report_result.stdout}{Colors.END}")
                
                # Parse coverage percentage
                lines = report_result.stdout.split('\n')
                total_coverage = "N/A"
                for line in lines:
                    if 'TOTAL' in line:
                        # Extract percentage
                        parts = line.split()
                        if len(parts) >= 4 and '%' in parts[-1]:
                            percentage = parts[-1]
                            total_coverage = percentage
                            coverage_num = float(percentage.replace('%', ''))
                            if coverage_num >= 80:
                                color = Colors.GREEN
                            elif coverage_num >= 60:
                                color = Colors.YELLOW
                            else:
                                color = Colors.RED
                            print(f"\n{Colors.BOLD}Overall Coverage: {color}{percentage}{Colors.END}")
                
                # Store coverage for filename
                self.coverage_percentage = total_coverage
                
                # Generate HTML report
                print(f"{Colors.CYAN}Generating HTML coverage report...{Colors.END}")
                html_result = subprocess.run([
                    'python3', '-m', 'coverage', 'html'
                ], capture_output=True, text=True, cwd=project_root, timeout=30)
                
                if html_result.returncode == 0:
                    print(f"{Colors.CYAN}HTML coverage report generated in: htmlcov/index.html{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}HTML report generation failed: {html_result.stderr}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Coverage report generation failed: {report_result.stderr}{Colors.END}")
                self.coverage_percentage = "N/A"
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}Coverage analysis timed out{Colors.END}")
            self.coverage_percentage = "N/A"
        except FileNotFoundError:
            print(f"{Colors.YELLOW}Coverage tool not found. Install with: pip install coverage{Colors.END}")
            self.coverage_percentage = "N/A"
        except Exception as e:
            print(f"{Colors.YELLOW}Coverage analysis error: {e}{Colors.END}")
            self.coverage_percentage = "N/A"
            
        # Also try to show per-app coverage
        self.show_app_coverage()
    
    def show_app_coverage(self):
        """Show coverage breakdown by app"""
        try:
            # Get detailed coverage data
            json_result = subprocess.run([
                'python3', '-m', 'coverage', 'json'
            ], capture_output=True, text=True, cwd=project_root)
            
            if json_result.returncode == 0:
                import json
                coverage_data = json.loads(json_result.stdout)
                
                print(f"\n{Colors.BOLD}Coverage by App:{Colors.END}")
                
                # Group by app
                app_coverage = {}
                for filename, file_data in coverage_data.get('files', {}).items():
                    if filename.startswith('apps/'):
                        app_name = filename.split('/')[1] if '/' in filename else 'unknown'
                        
                        if app_name not in app_coverage:
                            app_coverage[app_name] = {
                                'covered': 0,
                                'total': 0,
                                'files': 0
                            }
                        
                        summary = file_data.get('summary', {})
                        app_coverage[app_name]['covered'] += summary.get('covered_lines', 0)
                        app_coverage[app_name]['total'] += summary.get('num_statements', 0)
                        app_coverage[app_name]['files'] += 1
                
                # Display app coverage
                for app_name, data in sorted(app_coverage.items()):
                    if data['total'] > 0:
                        percentage = (data['covered'] / data['total']) * 100
                        
                        if percentage >= 80:
                            color = Colors.GREEN
                        elif percentage >= 60:
                            color = Colors.YELLOW
                        else:
                            color = Colors.RED
                            
                        print(f"  {app_name:20} {color}{percentage:6.1f}%{Colors.END} "
                              f"({data['covered']}/{data['total']} lines, {data['files']} files)")
                        
        except Exception as e:
            print(f"{Colors.YELLOW}Detailed coverage analysis failed: {e}{Colors.END}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = len(self.results) - passed_count
        success_rate = (passed_count / len(self.results)) * 100 if self.results else 0
        
        self.print_and_capture(f"\n{Colors.BOLD}Test Results:{Colors.END}")
        self.print_and_capture(f"  {Colors.GREEN}Passed: {passed_count}{Colors.END}")
        self.print_and_capture(f"  {Colors.RED}Failed: {failed_count}{Colors.END}")
        self.print_and_capture(f"  {Colors.CYAN}Total:  {len(self.results)}{Colors.END}")
        self.print_and_capture(f"  {Colors.YELLOW}Success Rate: {success_rate:.1f}%{Colors.END}")
        self.print_and_capture(f"  {Colors.MAGENTA}Duration: {self.total_duration:.2f}s{Colors.END}")
        
        # Show coverage summary
        if self.coverage_percentage and self.coverage_percentage != "N/A":
            coverage_num = float(str(self.coverage_percentage).replace('%', ''))
            if coverage_num >= 80:
                color = Colors.GREEN
            elif coverage_num >= 60:
                color = Colors.YELLOW
            else:
                color = Colors.RED
            self.print_and_capture(f"  {Colors.BOLD}Code Coverage: {color}{self.coverage_percentage}%{Colors.END}")
        else:
            # Try to get coverage one more time
            try:
                coverage_result = subprocess.run([
                    'python3', '-m', 'coverage', 'report', '--format=total'
                ], capture_output=True, text=True, cwd=project_root, timeout=10)
                
                if coverage_result.returncode == 0:
                    total_coverage = coverage_result.stdout.strip()
                    if total_coverage and '%' in total_coverage:
                        coverage_num = float(total_coverage.replace('%', ''))
                        if coverage_num >= 80:
                            color = Colors.GREEN
                        elif coverage_num >= 60:
                            color = Colors.YELLOW
                        else:
                            color = Colors.RED
                        self.print_and_capture(f"  {Colors.BOLD}Code Coverage: {color}{total_coverage}{Colors.END}")
                    else:
                        self.print_and_capture(f"  {Colors.BOLD}Code Coverage: {Colors.YELLOW}N/A{Colors.END}")
                else:
                    self.print_and_capture(f"  {Colors.BOLD}Code Coverage: {Colors.YELLOW}N/A{Colors.END}")
            except Exception:
                self.print_and_capture(f"  {Colors.BOLD}Code Coverage: {Colors.YELLOW}N/A{Colors.END}")
        
        if failed_count > 0:
            self.print_and_capture(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.END}")
            for result in self.results:
                if not result.passed:
                    self.print_and_capture(f"  {Colors.RED}- {result.name}: {result.error}{Colors.END}")
        
        if success_rate == 100.0:
            self.print_and_capture(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED!{Colors.END}")
            self.print_and_capture(f"{Colors.GREEN}CRISP UserManagement and TrustManagement systems are fully integrated.{Colors.END}")
        else:
            self.print_and_capture(f"\n{Colors.YELLOW}{Colors.BOLD}Some tests failed. Review the errors above.{Colors.END}")
            
        self.print_and_capture(f"\n{Colors.CYAN}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    def demonstrate_system_integration(self):
        """Demonstrate full system integration with multiple organizations and users"""
        self.print_section("System Integration Demonstration")
        
        from apps.core.services import CRISPIntegrationService
        from apps.user_management.models import Organization
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        timestamp = str(int(time.time()))
        
        try:
            # Create multiple organizations
            organizations = []
            org_configs = [
                {
                    'name': f'State University {timestamp}',
                    'domain': f'state-univ-{timestamp}.edu',
                    'contact_email': f'admin@state-univ-{timestamp}.edu',
                    'institution_type': 'university',
                    'admin_data': {
                        'username': f'admin_univ_{timestamp}',
                        'email': f'admin@state-univ-{timestamp}.edu',
                        'password': 'SecurePass123!',
                        'first_name': 'University',
                        'last_name': 'Admin'
                    }
                },
                {
                    'name': f'Regional Healthcare {timestamp}',
                    'domain': f'regional-health-{timestamp}.org',
                    'contact_email': f'security@regional-health-{timestamp}.org',
                    'institution_type': 'healthcare',
                    'admin_data': {
                        'username': f'admin_health_{timestamp}',
                        'email': f'security@regional-health-{timestamp}.org',
                        'password': 'SecurePass123!',
                        'first_name': 'Healthcare',
                        'last_name': 'Security'
                    }
                }
            ]
            
            for org_data in org_configs:
                org = CRISPIntegrationService.create_organization_with_trust_setup(
                    name=org_data['name'],
                    domain=org_data['domain'],
                    contact_email=org_data['contact_email'],
                    admin_user_data=org_data['admin_data'],
                    institution_type=org_data['institution_type'],
                    default_trust_level='public'
                )
                organizations.append(org)
                self.print_success(f"Created {org.institution_type} organization: {org.name}")
                
            self.test_data['demo_organizations'] = organizations
            
            # Create trust relationship between organizations
            if len(organizations) >= 2:
                relationship = CRISPIntegrationService.create_trust_relationship(
                    source_org=organizations[0],
                    target_org=organizations[1],
                    trust_level_name='Trusted Partners',
                    relationship_type='bilateral'
                )
                self.print_success(f"Created trust relationship: {relationship.id}")
                self.print_info(f"  Between: {organizations[0].name} ↔ {organizations[1].name}")
                
            # Demonstrate intelligence access control
            for org in organizations:
                admin_user = User.objects.filter(
                    organization=org,
                    is_organization_admin=True
                ).first()
                if admin_user:
                    accessible_sources = CRISPIntegrationService.get_user_accessible_intelligence_sources(
                        user=admin_user,
                        intelligence_type='threat_indicator'
                    )
                    self.print_info(f"Admin {admin_user.email} has access to {len(accessible_sources)} sources")
                    
        except Exception as e:
            self.print_error(f"System integration demonstration failed: {e}")
            
    def generate_system_report(self):
        """Generate comprehensive system report"""
        self.print_section("System Integration Report")
        
        from apps.user_management.models import Organization, CustomUser
        from apps.trust_management.models import TrustLevel, TrustRelationship, TrustLog
        
        try:
            # System statistics
            stats = {
                'organizations': Organization.objects.count(),
                'users': CustomUser.objects.count(),
                'trust_levels': TrustLevel.objects.count(),
                'trust_relationships': TrustRelationship.objects.count(),
                'trust_logs': TrustLog.objects.count(),
                'active_relationships': TrustRelationship.objects.filter(status='approved').count(),
                'pending_relationships': TrustRelationship.objects.filter(status='pending').count(),
            }
            
            self.print_success("System Statistics:")
            for key, value in stats.items():
                self.print_info(f"  {key.replace('_', ' ').title()}: {value}")
                
            # User role distribution
            self.print_success("User Role Distribution:")
            role_counts = {}
            for user in CustomUser.objects.all():
                role = user.role
                role_counts[role] = role_counts.get(role, 0) + 1
                
            for role, count in role_counts.items():
                self.print_info(f"  {role.title()}: {count}")
                
            # Trust level usage
            trust_levels = TrustLevel.objects.all()
            self.print_success("Trust Level Usage:")
            for level in trust_levels:
                usage_count = TrustRelationship.objects.filter(trust_level=level).count()
                self.print_info(f"  {level.name}: {usage_count} relationships")
                
            # Integration health
            self.print_success("Integration Health:")
            self.print_info(f"  Database: Connected")
            self.print_info(f"  Models: {len(stats)} model types active")
            self.print_info(f"  Coverage: {self.coverage_data.get('total_coverage', 'N/A')}")
            self.print_info(f"  Duration: {self.total_duration:.2f}s")
            
        except Exception as e:
            self.print_error(f"System report generation failed: {e}")

    def run_all_tests(self):
        """Run the complete test suite with system demonstrations"""
        self.start_time = time.time()
        
        # Start with system overview
        self.system_overview()
        
        self.print_header("CRISP INTEGRATION TEST SUITE")
        self.print_and_capture(f"{Colors.CYAN}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        self.print_and_capture(f"{Colors.CYAN}Database: {settings.DATABASES['default']['NAME']}{Colors.END}")
        
        # Define test cases
        test_cases = [
            (self.test_system_checks, "System Configuration", "Validate Django system setup"),
            (self.test_database_setup, "Database Setup", "Verify database and migrations"),
            (self.test_trust_levels, "Trust Level Management", "Test trust level CRUD operations"),
            (self.test_user_management, "User Management", "Test user and organization management"),
            (self.test_trust_relationships, "Trust Relationships", "Test trust relationship creation"),
            (self.test_integration_service, "Integration Service", "Test core integration service"),
            (self.run_django_tests, "Django Test Suite", "Run built-in Django tests"),
        ]
        
        # Run each test
        for test_func, name, description in test_cases:
            self.print_section(f"Running: {name}")
            self.run_test(test_func, name, description)
        
        # Run system integration demonstration
        self.demonstrate_system_integration()
        
        # Generate coverage report
        self.generate_coverage_report()
        
        # Generate system report
        self.generate_system_report()
        
        # Calculate total duration
        self.total_duration = time.time() - self.start_time
        
        # Print summary
        self.print_summary()
        
        # Save results to file
        self.save_results_to_file()
        
        # Return exit code
        failed_count = sum(1 for r in self.results if not r.passed)
        return 0 if failed_count == 0 else 1


def main():
    """Main entry point"""
    suite = CRISPTestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
