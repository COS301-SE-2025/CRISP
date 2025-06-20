from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

T = TypeVar('T', bound=models.Model)


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository class
    """
    
    def __init__(self, model_class: type):
        self.model_class = model_class
    
    def save(self, entity: T) -> T:
        """Save an entity"""
        entity.save()
        return entity
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        try:
            return self.model_class.objects.get(id=entity_id)
        except ObjectDoesNotExist:
            return None
    
    def get_all(self) -> List[T]:
        """Get all entities"""
        return list(self.model_class.objects.all())
    
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        try:
            entity = self.model_class.objects.get(id=entity_id)
            entity.delete()
            return True
        except ObjectDoesNotExist:
            return False
    
    def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        return self.model_class.objects.filter(id=entity_id).exists()
    
    def count(self) -> int:
        """Count all entities"""
        return self.model_class.objects.count()
    
    @abstractmethod
    def search(self, query_params: Dict[str, Any]) -> List[T]:
        """Search entities based on query parameters"""
        pass
    
    def filter_by(self, **kwargs) -> List[T]:
        """Filter entities by given criteria"""
        return list(self.model_class.objects.filter(**kwargs))
    
    def get_or_create(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple[T, bool]:
        """Get or create entity"""
        return self.model_class.objects.get_or_create(defaults=defaults, **kwargs)
    
    def bulk_create(self, entities: List[T]) -> List[T]:
        """Bulk create entities"""
        return self.model_class.objects.bulk_create(entities)
    
    def bulk_update(self, entities: List[T], fields: List[str]) -> int:
        """Bulk update entities"""
        return self.model_class.objects.bulk_update(entities, fields)