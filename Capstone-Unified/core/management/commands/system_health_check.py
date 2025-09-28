"""
Management command to perform comprehensive system health checks
Validates database connectivity, service integrity, and configuration
"""

import os
import sys
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from django.core.mail import send_mail
from core.models.models import (
    Organization, TrustRelationship, ThreatFeed,
    Indicator, TTPData
)
from core.user_management.models.user_models import CustomUser, AuthenticationLog
from core.services.trust_service import TrustService
from core.services.access_control_service import AccessControlService
from core.services.audit_service import AuditService

class Command(BaseCommand):
    help = 'Perform comprehensive system health check'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )
        parser.add_argument(
            '--email-test',
            action='store_true',
            help='Test email configuration',
        )
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Attempt to fix minor issues automatically',
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.email_test = options['email_test']
        self.fix_issues = options['fix_issues']
        
        self.stdout.write(
            self.style.SUCCESS('Starting CRISP System Health Check...')
        )
        
        checks_passed = 0
        checks_failed = 0
        warnings = 0
        
        # Database connectivity check
        result = self._check_database()
        if result['status'] == 'pass':
            checks_passed += 1
        elif result['status'] == 'fail':
            checks_failed += 1
        else:
            warnings += 1
        
        # Model integrity check
        result = self._check_models()
        if result['status'] == 'pass':
            checks_passed += 1
        elif result['status'] == 'fail':
            checks_failed += 1
        else:
            warnings += 1
        
        # Service functionality check
        result = self._check_services()
        if result['status'] == 'pass':
            checks_passed += 1
        elif result['status'] == 'fail':
            checks_failed += 1
        else:
            warnings += 1
        
        # Configuration check
        result = self._check_configuration()
        if result['status'] == 'pass':
            checks_passed += 1
        elif result['status'] == 'fail':
            checks_failed += 1
        else:
            warnings += 1
        
        # File system check
        result = self._check_filesystem()
        if result['status'] == 'pass':
            checks_passed += 1
        elif result['status'] == 'fail':
            checks_failed += 1
        else:
            warnings += 1
        
        # Security check
        result = self._check_security()
        if result['status'] == 'pass':
            checks_passed += 1
        elif result['status'] == 'fail':
            checks_failed += 1
        else:
            warnings += 1
        
        # Email test (optional)
        if self.email_test:
            result = self._check_email()
            if result['status'] == 'pass':
                checks_passed += 1
            elif result['status'] == 'fail':
                checks_failed += 1
            else:
                warnings += 1
        
        # Performance check
        result = self._check_performance()
        if result['status'] == 'pass':
            checks_passed += 1
        elif result['status'] == 'fail':
            checks_failed += 1
        else:
            warnings += 1
        
        # Display summary
        self._display_summary(checks_passed, checks_failed, warnings)
        
        # Exit with appropriate code
        if checks_failed > 0:
            sys.exit(1)
        elif warnings > 0:
            sys.exit(2)
        else:
            sys.exit(0)

    def _check_database(self):
        """Check database connectivity and basic operations"""
        self.stdout.write('Checking database connectivity...')
        
        try:
            # Test basic connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            if result[0] != 1:
                return {
                    'status': 'fail',
                    'message': 'Database query returned unexpected result'
                }
            
            # Test model operations
            user_count = CustomUser.objects.count()
            org_count = Organization.objects.count()
            
            if self.verbose:
                self.stdout.write(f'  - Users: {user_count}')
                self.stdout.write(f'  - Organizations: {org_count}')
            
            self.stdout.write(self.style.SUCCESS('✓ Database connectivity: PASS'))
            return {'status': 'pass', 'message': 'Database is accessible'}
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connectivity: FAIL - {str(e)}'))
            return {'status': 'fail', 'message': str(e)}

    def _check_models(self):
        """Check model integrity and relationships"""
        self.stdout.write('Checking model integrity...')
        
        try:
            issues = []
            
            # Check for users without organizations
            users_without_org = CustomUser.objects.filter(organization__isnull=True).count()
            if users_without_org > 0:
                issues.append(f'{users_without_org} users without organization')
                if self.fix_issues:
                    # Could attempt to fix by assigning to default org
                    pass
            
            # Check for orphaned trust relationships
            orphaned_trusts = TrustRelationship.objects.filter(
                source_organization__isnull=True
            ).count()
            if orphaned_trusts > 0:
                issues.append(f'{orphaned_trusts} orphaned trust relationships')
            
            # Check for invalid trust levels
            invalid_trusts = TrustRelationship.objects.filter(
                trust_level__isnull=True
            ).count()
            if invalid_trusts > 0:
                issues.append(f'{invalid_trusts} trust relationships with invalid levels')
            
            if issues:
                message = '; '.join(issues)
                self.stdout.write(self.style.WARNING(f'⚠ Model integrity: WARNING - {message}'))
                return {'status': 'warning', 'message': message}
            else:
                self.stdout.write(self.style.SUCCESS('✓ Model integrity: PASS'))
                return {'status': 'pass', 'message': 'All models are consistent'}
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Model integrity: FAIL - {str(e)}'))
            return {'status': 'fail', 'message': str(e)}

    def _check_services(self):
        """Check service functionality"""
        self.stdout.write('Checking service functionality...')
        
        try:
            # Test TrustService
            trust_service = TrustService()
            if not hasattr(trust_service, 'get_trust_level'):
                raise Exception('TrustService missing required methods')
            
            # Test AccessControlService
            access_control = AccessControlService()
            if not hasattr(access_control, 'can_view_user'):
                raise Exception('AccessControlService missing required methods')
            
            # Test AuditService
            audit_service = AuditService()
            if not hasattr(audit_service, 'log_security_event'):
                raise Exception('AuditService missing required methods')
            
            self.stdout.write(self.style.SUCCESS('✓ Service functionality: PASS'))
            return {'status': 'pass', 'message': 'All services are functional'}
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Service functionality: FAIL - {str(e)}'))
            return {'status': 'fail', 'message': str(e)}

    def _check_configuration(self):
        """Check system configuration"""
        self.stdout.write('Checking configuration...')
        
        warnings = []
        errors = []
        
        # Check required settings
        required_settings = [
            'SECRET_KEY',
            'DATABASES',
            'AUTH_USER_MODEL',
            'REST_FRAMEWORK',
            'SIMPLE_JWT'
        ]
        
        for setting in required_settings:
            if not hasattr(settings, setting):
                errors.append(f'Missing required setting: {setting}')
        
        # Check environment variables
        env_vars = [
            'DJANGO_SECRET_KEY',
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD'
        ]
        
        for var in env_vars:
            if not os.getenv(var):
                warnings.append(f'Environment variable not set: {var}')
        
        # Check DEBUG setting in production
        if settings.DEBUG and os.getenv('ENVIRONMENT', 'development') == 'production':
            warnings.append('DEBUG is enabled in production environment')
        
        if errors:
            message = '; '.join(errors)
            self.stdout.write(self.style.ERROR(f'✗ Configuration: FAIL - {message}'))
            return {'status': 'fail', 'message': message}
        elif warnings:
            message = '; '.join(warnings)
            self.stdout.write(self.style.WARNING(f'⚠ Configuration: WARNING - {message}'))
            return {'status': 'warning', 'message': message}
        else:
            self.stdout.write(self.style.SUCCESS('✓ Configuration: PASS'))
            return {'status': 'pass', 'message': 'Configuration is valid'}

    def _check_filesystem(self):
        """Check file system permissions and directories"""
        self.stdout.write('Checking file system...')
        
        try:
            issues = []
            
            # Check required directories
            required_dirs = [
                settings.STATIC_ROOT or os.path.join(settings.BASE_DIR, 'static'),
                os.path.join(settings.BASE_DIR, 'logs'),
                os.path.join(settings.BASE_DIR, 'uploads')
            ]
            
            for directory in required_dirs:
                if not os.path.exists(directory):
                    if self.fix_issues:
                        try:
                            os.makedirs(directory, exist_ok=True)
                            self.stdout.write(f'  Created directory: {directory}')
                        except Exception as e:
                            issues.append(f'Cannot create directory {directory}: {str(e)}')
                    else:
                        issues.append(f'Missing directory: {directory}')
                elif not os.access(directory, os.W_OK):
                    issues.append(f'No write permission for directory: {directory}')
            
            # Check log file
            log_file = os.path.join(settings.BASE_DIR, 'crisp_unified.log')
            if os.path.exists(log_file) and not os.access(log_file, os.W_OK):
                issues.append(f'No write permission for log file: {log_file}')
            
            if issues:
                message = '; '.join(issues)
                self.stdout.write(self.style.WARNING(f'⚠ File system: WARNING - {message}'))
                return {'status': 'warning', 'message': message}
            else:
                self.stdout.write(self.style.SUCCESS('✓ File system: PASS'))
                return {'status': 'pass', 'message': 'File system is accessible'}
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ File system: FAIL - {str(e)}'))
            return {'status': 'fail', 'message': str(e)}

    def _check_security(self):
        """Check security configuration"""
        self.stdout.write('Checking security configuration...')
        
        warnings = []
        
        # Check SECRET_KEY
        if settings.SECRET_KEY == 'django-insecure-default-key-for-dev':
            warnings.append('Using default SECRET_KEY')
        
        # Check ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            warnings.append('ALLOWED_HOSTS allows all hosts in production')
        
        # Check CORS settings
        if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
            warnings.append('CORS allows all origins')
        
        # Check middleware
        required_middleware = [
            'core.middleware.audit_middleware.AuditMiddleware',
            'core.middleware.trust_middleware.TrustMiddleware'
        ]
        
        for middleware in required_middleware:
            if middleware not in settings.MIDDLEWARE:
                warnings.append(f'Missing security middleware: {middleware}')
        
        if warnings:
            message = '; '.join(warnings)
            self.stdout.write(self.style.WARNING(f'⚠ Security: WARNING - {message}'))
            return {'status': 'warning', 'message': message}
        else:
            self.stdout.write(self.style.SUCCESS('✓ Security: PASS'))
            return {'status': 'pass', 'message': 'Security configuration is adequate'}

    def _check_email(self):
        """Test email configuration"""
        self.stdout.write('Testing email configuration...')
        
        try:
            test_email = os.getenv('TEST_EMAIL', 'test@example.com')
            
            send_mail(
                'CRISP System Health Check',
                'This is a test email from the CRISP system health check.',
                settings.DEFAULT_FROM_EMAIL,
                [test_email],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Email: PASS'))
            return {'status': 'pass', 'message': f'Test email sent to {test_email}'}
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Email: FAIL - {str(e)}'))
            return {'status': 'fail', 'message': str(e)}

    def _check_performance(self):
        """Check system performance metrics"""
        self.stdout.write('Checking performance metrics...')
        
        try:
            warnings = []
            
            # Check database query performance
            import time
            start_time = time.time()
            CustomUser.objects.count()
            query_time = time.time() - start_time
            
            if query_time > 1.0:
                warnings.append(f'Slow database queries (>{query_time:.2f}s)')
            
            # Check large table sizes
            if ThreatFeed.objects.count() > 10000:
                warnings.append('Large number of threat feeds may impact performance')
            
            if Indicator.objects.count() > 100000:
                warnings.append('Large number of indicators may impact performance')
            
            # Check audit log size
            if AuthenticationLog.objects.count() > 1000000:
                warnings.append('Large audit log may impact performance')
            
            if warnings:
                message = '; '.join(warnings)
                self.stdout.write(self.style.WARNING(f'⚠ Performance: WARNING - {message}'))
                return {'status': 'warning', 'message': message}
            else:
                self.stdout.write(self.style.SUCCESS('✓ Performance: PASS'))
                return {'status': 'pass', 'message': 'Performance metrics are acceptable'}
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Performance: FAIL - {str(e)}'))
            return {'status': 'fail', 'message': str(e)}

    def _display_summary(self, checks_passed, checks_failed, warnings):
        """Display health check summary"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('SYSTEM HEALTH CHECK SUMMARY')
        )
        self.stdout.write('='*50)
        
        total_checks = checks_passed + checks_failed + warnings
        
        self.stdout.write(f'Total Checks: {total_checks}')
        self.stdout.write(self.style.SUCCESS(f'Passed: {checks_passed}'))
        if warnings > 0:
            self.stdout.write(self.style.WARNING(f'Warnings: {warnings}'))
        if checks_failed > 0:
            self.stdout.write(self.style.ERROR(f'Failed: {checks_failed}'))
        
        if checks_failed == 0 and warnings == 0:
            self.stdout.write('\n' + self.style.SUCCESS('✓ All checks passed - System is healthy'))
        elif checks_failed == 0:
            self.stdout.write('\n' + self.style.WARNING('⚠ Some warnings found - Review recommended'))
        else:
            self.stdout.write('\n' + self.style.ERROR('✗ Critical issues found - Immediate attention required'))
        
        self.stdout.write('\n' + '='*50)