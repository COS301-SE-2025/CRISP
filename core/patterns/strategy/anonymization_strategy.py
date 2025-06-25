from abc import ABC, abstractmethod

class AnonymizationStrategy(ABC):
    """
    Abstract base class defining the interface for anonymization strategies.
    This is part of the Strategy pattern implementation.
    
    Your friend will implement concrete strategies that inherit from this class.
    """
    
    @abstractmethod
    def anonymize_indicator(self, indicator_data):
        """
        Anonymize indicator data.
        
        Args:
            indicator_data: Dictionary containing indicator data
            
        Returns:
            dict: Anonymized indicator data
        """
        pass
    
    @abstractmethod
    def anonymize_ttp(self, ttp_data):
        """
        Anonymize TTP data.
        
        Args:
            ttp_data: Dictionary containing TTP data
            
        Returns:
            dict: Anonymized TTP data
        """
        pass


class NoAnonymizationStrategy(AnonymizationStrategy):
    """
    A concrete strategy that performs no anonymization.
    This is a default/fallback strategy.
    """
    
    def anonymize_indicator(self, indicator_data):
        """
        Return the indicator data unchanged.
        
        Args:
            indicator_data: Dictionary containing indicator data
            
        Returns:
            dict: The original indicator data
        """
        return indicator_data
    
    def anonymize_ttp(self, ttp_data):
        """
        Return the TTP data unchanged.
        
        Args:
            ttp_data: Dictionary containing TTP data
            
        Returns:
            dict: The original TTP data
        """
        return ttp_data