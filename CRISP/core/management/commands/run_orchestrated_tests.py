import sys
from django.core.management.base import BaseCommand
from crisp_unified.main_test_runner import CRISPTestOrchestrator


class Command(BaseCommand):
    """
    Management command to run the advanced test orchestrator
    """
    help = 'Run CRISP tests using the advanced orchestrator'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interactive', 
            action='store_true',
            help='Run in interactive mode'
        )
        parser.add_argument(
            '--suite', 
            type=str,
            choices=['foundation', 'data', 'service', 'integration', 'api'],
            help='Run specific test suite only'
        )
        parser.add_argument(
            '--fast', 
            action='store_true',
            help='Skip environment validation and run tests'
        )
        parser.add_argument(
            '--export-report',
            type=str,
            help='Export detailed report to specified file (JSON format)'
        )
        parser.add_argument(
            '--filter',
            type=str, 
            help='Filter tests by name pattern'
        )
    
    def handle(self, *args, **options):
        """Main entry point for the management command"""
        
        # Create the orchestrator with options
        orchestrator = CRISPTestOrchestrator(
            verbosity=2,
            interactive=options.get('interactive', False),
            debug_mode=False,
            keepdb=False
        )
        
        if options.get('fast'):
            orchestrator.skip_validation = True
        
        if options.get('suite'):
            orchestrator.target_suite = options['suite']
        
        if options.get('filter'):
            orchestrator.test_filter = options['filter']
        
        if options.get('export_report'):
            orchestrator.export_path = options['export_report']
        
        # Run the orchestrated tests
        try:
            result = orchestrator.run_tests(['core'])
            
            if result == 0:
                self.stdout.write(
                    self.style.SUCCESS('🎉 All tests completed successfully!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Some tests failed. Check the detailed report above.')
                )
            
            sys.exit(result)
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\nTest execution interrupted by user')
            )
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Orchestrator error: {str(e)}')
            )
            import traceback
            self.stderr.write(traceback.format_exc())
            sys.exit(1)