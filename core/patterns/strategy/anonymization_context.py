import logging

logger = logging.getLogger(__name__)

class AnonymizationContext:
    """
    Context class for the Strategy pattern implementation of anonymization.
    This class will hold the current anonymization strategy and provide
    methods to execute anonymization.
    
    This is a placeholder that will be integrated with your friend's 
    strategy pattern implementation later.
    """
    
    def __init__(self, strategy=None):
        """
        Initialize with an optional strategy.
        
        Args:
            strategy: AnonymizationStrategy to use (optional)
        """
        self._strategy = strategy
    
    def set_strategy(self, strategy):
        """
        Set the anonymization strategy.
        
        Args:
            strategy: AnonymizationStrategy to use
        """
        self._strategy = strategy
    
    def anonymize_indicator(self, indicator_data):
        """
        Anonymize indicator data using the current strategy.
        
        Args:
            indicator_data: Dictionary containing indicator data
            
        Returns:
            dict: Anonymized indicator data
        """
        if self._strategy is None:
            logger.warning("No anonymization strategy set, returning original data")
            return indicator_data
        
        return self._strategy.anonymize_indicator(indicator_data)
    
    def anonymize_ttp(self, ttp_data):
        """
        Anonymize TTP data using the current strategy.
        
        Args:
            ttp_data: Dictionary containing TTP data
            
        Returns:
            dict: Anonymized TTP data
        """
        if self._strategy is None:
            logger.warning("No anonymization strategy set, returning original data")
            return ttp_data
        
        return self._strategy.anonymize_ttp(ttp_data)