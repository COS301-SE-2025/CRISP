from core.patterns.decorator.stix_decorator import StixDecorator
import logging

logger = logging.getLogger(__name__)

class StixValidationDecorator(StixDecorator):
    """
    Concrete decorator that adds enhanced validation to STIX objects.
    This decorator can validate STIX objects against additional business rules
    or compliance requirements.
    """
    
    def __init__(self, component, validation_rules=None):
        """
        Initialize the validation decorator
        
        Args:
            component: StixObjectComponent to decorate
            validation_rules: List of validation rules to apply
        """
        super().__init__(component)
        self.validation_rules = validation_rules or []
        self.validation_errors = []
        
    def validate(self):
        """
        Validate the STIX object against the wrapped component's validation
        and additional validation rules.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Clear previous validation errors
        self.validation_errors = []
        
        # First, validate using the wrapped component
        is_valid = self._component.validate()
        
        if not is_valid:
            logger.warning("Base validation failed for STIX object")
            return False
        
        # Apply additional validation rules
        stix_obj = self._component.get_stix_object()
        
        for rule in self.validation_rules:
            try:
                rule_result = rule.validate(stix_obj)
                if not rule_result['valid']:
                    self.validation_errors.append(rule_result['message'])
                    is_valid = False
            except Exception as e:
                logger.error(f"Error applying validation rule: {str(e)}")
                self.validation_errors.append(f"Validation error: {str(e)}")
                is_valid = False
        
        if not is_valid:
            logger.warning(f"Validation failed with {len(self.validation_errors)} errors")
            for error in self.validation_errors:
                logger.warning(f"Validation error: {error}")
        
        return is_valid
    
    def get_validation_errors(self):
        """
        Get the validation errors from the last validation run.
        
        Returns:
            list: List of validation error messages
        """
        return self.validation_errors