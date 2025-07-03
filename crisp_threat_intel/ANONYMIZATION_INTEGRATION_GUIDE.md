# CRISP Anonymization Integration Guide

This guide explains how to combine, extend, and customize the anonymization system within the CRISP threat intelligence publication platform.

## Table of Contents

1. [Anonymization Architecture Overview](#anonymization-architecture-overview)
2. [Integration Points](#integration-points)
3. [Extending Anonymization Strategies](#extending-anonymization-strategies)
4. [Trust Relationship Management](#trust-relationship-management)
5. [Testing Anonymization](#testing-anonymization)
6. [Performance Considerations](#performance-considerations)
7. [Implementation Examples](#implementation-examples)
8. [Best Practices](#best-practices)

---

## Anonymization Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                 CRISP Anonymization System                 │
├─────────────────────────────────────────────────────────────┤
│  Trust Management  │  Strategy Factory  │  Validation      │
│  ┌──────────────┐  │  ┌──────────────┐  │  ┌──────────────┐ │
│  │ Trust        │  │  │ Strategy     │  │  │ Quality      │ │
│  │ Relationships│  │  │ Registry     │  │  │ Assurance    │ │
│  │              │  │  │              │  │  │              │ │
│  └──────────────┘  │  └──────────────┘  │  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                  Integration Layer                          │
├─────────────────────────────────────────────────────────────┤
│  Publication     │  Database        │  TAXII Endpoints     │
│  Workflows       │  Operations      │  Serving             │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

1. **Strategy Pattern**: Flexible anonymization algorithms
2. **Factory Pattern**: Dynamic strategy selection
3. **Observer Pattern**: Anonymization event notifications
4. **Decorator Pattern**: Layered anonymization enhancement

---

## Integration Points

### 1. Model Integration

The anonymization system integrates at the model level through several key methods:

#### `STIXObject` Model Integration
```python
# Location: crisp_threat_intel/models.py
class STIXObject(models.Model):
    # ... other fields ...
    
    def apply_anonymization(self, requesting_org, strategy_name=None):
        """Apply anonymization based on requesting organization"""
        if self.source_organization == requesting_org:
            return self.raw_data  # No anonymization for same org
            
        # Determine trust level
        trust_level = self.get_trust_level(requesting_org)
        
        # Select strategy
        if strategy_name is None:
            strategy_name = self.determine_strategy(trust_level)
            
        strategy = AnonymizationStrategyFactory.get_strategy(strategy_name)
        return strategy.anonymize(self.raw_data, trust_level)
    
    def get_trust_level(self, requesting_org):
        """Get trust level between source and requesting organization"""
        try:
            relationship = TrustRelationship.objects.get(
                source_org=self.source_organization,
                target_org=requesting_org
            )
            return relationship.trust_level
        except TrustRelationship.DoesNotExist:
            return 0.5  # Default medium trust
```

#### `Collection` Model Integration
```python
# Location: crisp_threat_intel/models.py
class Collection(models.Model):
    # ... other fields ...
    
    def generate_bundle(self, requesting_org=None):
        """Generate anonymized bundle for requesting organization"""
        objects = []
        
        for obj in self.stix_objects.all():
            if requesting_org:
                anonymized_data = obj.apply_anonymization(requesting_org)
            else:
                anonymized_data = obj.raw_data
            
            objects.append(anonymized_data)
        
        bundle = {
            'type': 'bundle',
            'id': f'bundle--{uuid.uuid4()}',
            'objects': objects
        }
        
        return bundle
```

### 2. TAXII View Integration

TAXII endpoints integrate anonymization transparently:

#### `TAXIIBaseView` Integration
```python
# Location: crisp_threat_intel/taxii/views.py
class TAXIIBaseView(APIView):
    def apply_anonymization(self, stix_object, requesting_org, source_org):
        """Apply appropriate anonymization based on trust level"""
        if requesting_org == source_org:
            return stix_object
        
        # Get trust level
        trust_level = self.get_trust_level(source_org, requesting_org)
        
        # Select strategy based on trust level
        if trust_level >= 0.8:
            strategy_name = 'none'
        elif trust_level >= 0.4:
            strategy_name = 'domain'
        else:
            strategy_name = 'full'
        
        # Apply anonymization
        strategy = AnonymizationStrategyFactory.get_strategy(strategy_name)
        anonymized = strategy.anonymize(stix_object, trust_level)
        
        return anonymized
```

### 3. Publication Workflow Integration

Feed publication integrates anonymization at multiple levels:

#### Feed Publication Integration
```python
# Location: crisp_threat_intel/utils.py
def publish_feed(feed, target_audiences=None):
    """Publish feed with appropriate anonymization for each audience"""
    results = []
    
    if target_audiences is None:
        # Default to all organizations with access
        target_audiences = get_authorized_organizations(feed)
    
    for org in target_audiences:
        # Generate anonymized bundle for this organization
        bundle = feed.collection.generate_bundle(requesting_org=org)
        
        # Validate anonymized bundle
        validation_result = validate_anonymized_bundle(bundle, org)
        if not validation_result.is_valid:
            continue
        
        # Publish to organization-specific endpoint
        publication_result = publish_to_org(bundle, org)
        results.append(publication_result)
    
    return results
```

---

## Extending Anonymization Strategies

### Creating Custom Strategies

#### 1. Define Strategy Class
```python
# Location: crisp_threat_intel/strategies/custom_anonymization.py
from .anonymization import AnonymizationStrategy
import re

class CustomEducationAnonymizationStrategy(AnonymizationStrategy):
    """Custom anonymization for educational institutions"""
    
    def anonymize(self, data, trust_level):
        """Apply education-specific anonymization"""
        anonymized_data = data.copy()
        
        # Anonymize student identifiers
        if 'description' in anonymized_data:
            anonymized_data['description'] = self.anonymize_student_ids(
                anonymized_data['description']
            )
        
        # Anonymize course codes
        if 'pattern' in anonymized_data:
            anonymized_data['pattern'] = self.anonymize_course_references(
                anonymized_data['pattern']
            )
        
        # Apply base domain anonymization
        anonymized_data = super().anonymize(anonymized_data, trust_level)
        
        return anonymized_data
    
    def anonymize_student_ids(self, text):
        """Anonymize student ID patterns"""
        # Pattern for student IDs (e.g., u12345678)
        student_id_pattern = r'\bu\d{8}\b'
        return re.sub(student_id_pattern, 'uXXXXXXXX', text)
    
    def anonymize_course_references(self, pattern):
        """Anonymize course code references"""
        # Pattern for course codes (e.g., COS301, MAT101)
        course_pattern = r'\b[A-Z]{3}\d{3}\b'
        return re.sub(course_pattern, 'XXXNNN', pattern)
    
    def get_effectiveness(self):
        """Return anonymization effectiveness score"""
        return 0.95  # 95% effective
```

#### 2. Register Strategy
```python
# Location: crisp_threat_intel/strategies/__init__.py
from .anonymization import AnonymizationStrategyFactory
from .custom_anonymization import CustomEducationAnonymizationStrategy

# Register custom strategy
AnonymizationStrategyFactory.register_strategy(
    'education',
    CustomEducationAnonymizationStrategy()
)
```

#### 3. Configure Strategy Usage
```python
# Location: crisp_threat_intel/models.py
class STIXObject(models.Model):
    # ... existing code ...
    
    def determine_strategy(self, trust_level):
        """Determine anonymization strategy with custom logic"""
        # Check for education-specific context
        if self.is_education_context():
            return 'education'
        
        # Default strategy selection
        if trust_level >= 0.8:
            return 'none'
        elif trust_level >= 0.4:
            return 'domain'
        else:
            return 'full'
    
    def is_education_context(self):
        """Check if object contains education-specific data"""
        if 'description' in self.raw_data:
            education_keywords = ['student', 'course', 'university', 'college']
            description = self.raw_data['description'].lower()
            return any(keyword in description for keyword in education_keywords)
        return False
```

### Advanced Strategy Composition

#### Layered Anonymization Strategy
```python
class LayeredAnonymizationStrategy(AnonymizationStrategy):
    """Apply multiple anonymization layers"""
    
    def __init__(self, strategies):
        self.strategies = strategies
    
    def anonymize(self, data, trust_level):
        """Apply strategies in sequence"""
        result = data
        
        for strategy in self.strategies:
            result = strategy.anonymize(result, trust_level)
        
        return result
    
    def get_effectiveness(self):
        """Combined effectiveness of all strategies"""
        if not self.strategies:
            return 0.0
        
        # Calculate combined effectiveness
        combined = 1.0
        for strategy in self.strategies:
            combined *= (1.0 - strategy.get_effectiveness())
        
        return 1.0 - combined

# Usage example
layered_strategy = LayeredAnonymizationStrategy([
    DomainAnonymizationStrategy(),
    CustomEducationAnonymizationStrategy(),
    IPAddressAnonymizationStrategy()
])
```

---

## Trust Relationship Management

### Trust Level Configuration

#### 1. Database Model
```python
# Location: crisp_threat_intel/models.py
class TrustRelationship(models.Model):
    """Manages trust relationships between organizations"""
    
    TRUST_LEVELS = [
        (1.0, 'Full Trust'),
        (0.8, 'High Trust'),
        (0.6, 'Medium Trust'),
        (0.4, 'Low Trust'),
        (0.2, 'Minimal Trust'),
        (0.0, 'No Trust'),
    ]
    
    source_org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='trust_given')
    target_org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='trust_received')
    trust_level = models.FloatField(choices=TRUST_LEVELS, default=0.5)
    anonymization_override = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['source_org', 'target_org']
```

#### 2. Dynamic Trust Calculation
```python
# Location: crisp_threat_intel/utils.py
def calculate_dynamic_trust(source_org, target_org):
    """Calculate trust level based on interaction history"""
    
    # Base trust from explicit relationship
    try:
        relationship = TrustRelationship.objects.get(
            source_org=source_org,
            target_org=target_org
        )
        base_trust = relationship.trust_level
    except TrustRelationship.DoesNotExist:
        base_trust = 0.5  # Default medium trust
    
    # Adjust based on interaction history
    interactions = InteractionHistory.objects.filter(
        source_org=source_org,
        target_org=target_org
    )
    
    if interactions.exists():
        # Calculate trust modifier based on successful interactions
        successful_interactions = interactions.filter(success=True).count()
        total_interactions = interactions.count()
        success_rate = successful_interactions / total_interactions
        
        # Adjust trust level (max ±0.2 adjustment)
        trust_modifier = (success_rate - 0.5) * 0.4
        adjusted_trust = max(0.0, min(1.0, base_trust + trust_modifier))
        
        return adjusted_trust
    
    return base_trust
```

### Community Trust Networks

#### Trust Network Implementation
```python
# Location: crisp_threat_intel/models.py
class TrustNetwork(models.Model):
    """Represents trust networks/communities"""
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    default_trust_level = models.FloatField(default=0.6)
    members = models.ManyToManyField(Organization, through='NetworkMembership')

class NetworkMembership(models.Model):
    """Membership in trust networks"""
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    network = models.ForeignKey(TrustNetwork, on_delete=models.CASCADE)
    membership_level = models.CharField(max_length=50, choices=[
        ('full', 'Full Member'),
        ('associate', 'Associate Member'),
        ('observer', 'Observer')
    ])
    joined_at = models.DateTimeField(auto_now_add=True)
```

---

## Testing Anonymization

### Unit Testing Framework

#### 1. Strategy Testing
```python
# Location: crisp_threat_intel/tests/test_anonymization_strategies.py
import unittest
from crisp_threat_intel.strategies.anonymization import (
    DomainAnonymizationStrategy,
    AnonymizationStrategyFactory
)

class TestAnonymizationStrategies(unittest.TestCase):
    
    def setUp(self):
        self.strategy = DomainAnonymizationStrategy()
        self.sample_data = {
            'type': 'indicator',
            'pattern': "[email-message:sender_ref.value = 'user@malicious.com']",
            'description': 'Malicious email from user@evil.org to victim@university.edu'
        }
    
    def test_email_anonymization(self):
        """Test email domain anonymization"""
        anonymized = self.strategy.anonymize(self.sample_data, 0.5)
        
        # Check that domains are anonymized
        self.assertIn('user@XXX.com', anonymized['pattern'])
        self.assertIn('user@XXX.org', anonymized['description'])
        self.assertIn('victim@XXX.edu', anonymized['description'])
    
    def test_preservation_of_structure(self):
        """Test that STIX structure is preserved"""
        anonymized = self.strategy.anonymize(self.sample_data, 0.5)
        
        # Structure should be preserved
        self.assertEqual(anonymized['type'], self.sample_data['type'])
        self.assertIn('pattern', anonymized)
        self.assertIn('description', anonymized)
    
    def test_effectiveness_measurement(self):
        """Test anonymization effectiveness calculation"""
        effectiveness = self.strategy.get_effectiveness()
        self.assertGreaterEqual(effectiveness, 0.0)
        self.assertLessEqual(effectiveness, 1.0)
```

#### 2. Integration Testing
```python
# Location: crisp_threat_intel/tests/test_anonymization_integration.py
class TestAnonymizationIntegration(TestCase):
    
    def test_end_to_end_anonymization(self):
        """Test complete anonymization workflow"""
        # Create test organizations
        source_org = Organization.objects.create(
            name='Source University',
            identity_class='organization'
        )
        target_org = Organization.objects.create(
            name='Target University',
            identity_class='organization'
        )
        
        # Create trust relationship
        TrustRelationship.objects.create(
            source_org=source_org,
            target_org=target_org,
            trust_level=0.6
        )
        
        # Create STIX object
        stix_obj = STIXObject.objects.create(
            stix_type='indicator',
            raw_data={
                'type': 'indicator',
                'pattern': "[email-message:sender_ref.value = 'attacker@evil.com']",
                'labels': ['malicious-activity']
            },
            source_organization=source_org
        )
        
        # Test anonymization
        anonymized = stix_obj.apply_anonymization(target_org)
        
        # Verify anonymization was applied
        self.assertIn('XXX.com', anonymized['pattern'])
        self.assertEqual(anonymized['type'], 'indicator')
        self.assertEqual(anonymized['labels'], ['malicious-activity'])
```

### Performance Testing

#### Anonymization Performance Tests
```python
# Location: crisp_threat_intel/tests/test_anonymization_performance.py
import time
from django.test import TestCase

class TestAnonymizationPerformance(TestCase):
    
    def test_large_dataset_anonymization(self):
        """Test anonymization performance with large datasets"""
        # Create large number of STIX objects
        objects = []
        for i in range(1000):
            objects.append({
                'type': 'indicator',
                'pattern': f"[file:hashes.MD5 = 'hash{i}@domain{i}.com']",
                'labels': ['malicious-activity']
            })
        
        strategy = DomainAnonymizationStrategy()
        
        # Measure anonymization time
        start_time = time.time()
        
        anonymized_objects = []
        for obj in objects:
            anonymized = strategy.anonymize(obj, 0.5)
            anonymized_objects.append(anonymized)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance assertions
        self.assertLess(processing_time, 10.0)  # Should complete in under 10 seconds
        self.assertEqual(len(anonymized_objects), 1000)
        
        # Verify anonymization quality
        for anonymized in anonymized_objects:
            self.assertIn('XXX.com', anonymized['pattern'])
```

---

## Performance Considerations

### Optimization Strategies

#### 1. Caching Anonymization Results
```python
# Location: crisp_threat_intel/strategies/cached_anonymization.py
from django.core.cache import cache
import hashlib

class CachedAnonymizationStrategy(AnonymizationStrategy):
    """Anonymization strategy with result caching"""
    
    def __init__(self, base_strategy, cache_ttl=3600):
        self.base_strategy = base_strategy
        self.cache_ttl = cache_ttl
    
    def anonymize(self, data, trust_level):
        """Anonymize with caching"""
        # Generate cache key
        cache_key = self.generate_cache_key(data, trust_level)
        
        # Check cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Apply anonymization
        result = self.base_strategy.anonymize(data, trust_level)
        
        # Cache result
        cache.set(cache_key, result, self.cache_ttl)
        
        return result
    
    def generate_cache_key(self, data, trust_level):
        """Generate unique cache key for data and trust level"""
        data_str = str(sorted(data.items()))
        combined = f"{data_str}:{trust_level}"
        return f"anon:{hashlib.md5(combined.encode()).hexdigest()}"
```

#### 2. Batch Anonymization
```python
# Location: crisp_threat_intel/utils.py
def batch_anonymize_objects(objects, requesting_org, batch_size=100):
    """Anonymize objects in batches for better performance"""
    results = []
    
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i + batch_size]
        batch_results = []
        
        # Process batch
        for obj in batch:
            anonymized = obj.apply_anonymization(requesting_org)
            batch_results.append(anonymized)
        
        results.extend(batch_results)
    
    return results
```

#### 3. Asynchronous Anonymization
```python
# Location: crisp_threat_intel/tasks.py
from celery import shared_task

@shared_task
def anonymize_large_collection(collection_id, requesting_org_id):
    """Asynchronously anonymize large collection"""
    collection = Collection.objects.get(id=collection_id)
    requesting_org = Organization.objects.get(id=requesting_org_id)
    
    # Process in background
    bundle = collection.generate_bundle(requesting_org=requesting_org)
    
    # Store result
    AnonymizedBundle.objects.create(
        collection=collection,
        requesting_org=requesting_org,
        bundle_data=bundle
    )
    
    return bundle['id']
```

---

## Implementation Examples

### Complete Integration Example

#### 1. Custom Educational Institution Strategy
```python
# File: crisp_threat_intel/strategies/education_strategy.py
from .anonymization import AnonymizationStrategy
import re

class EducationalInstitutionStrategy(AnonymizationStrategy):
    """Specialized anonymization for educational institutions"""
    
    EDUCATION_PATTERNS = {
        'student_id': r'\b[uU]\d{8}\b',           # u12345678
        'staff_id': r'\b[sS]\d{7}\b',            # s1234567
        'course_code': r'\b[A-Z]{3}\d{3}\b',     # COS301
        'campus_building': r'\bBuilding\s+\d+\b', # Building 12
        'residence': r'\bRes\s+\w+\b',           # Res Maroela
    }
    
    def anonymize(self, data, trust_level):
        """Apply education-specific anonymization"""
        anonymized = data.copy()
        
        # Apply different levels based on trust
        if trust_level >= 0.8:
            # High trust: minimal anonymization
            anonymized = self.apply_minimal_anonymization(anonymized)
        elif trust_level >= 0.5:
            # Medium trust: moderate anonymization
            anonymized = self.apply_moderate_anonymization(anonymized)
        else:
            # Low trust: full anonymization
            anonymized = self.apply_full_anonymization(anonymized)
        
        return anonymized
    
    def apply_minimal_anonymization(self, data):
        """Minimal anonymization for high trust"""
        # Only anonymize student IDs
        if 'description' in data:
            data['description'] = re.sub(
                self.EDUCATION_PATTERNS['student_id'],
                'uXXXXXXXX',
                data['description']
            )
        return data
    
    def apply_moderate_anonymization(self, data):
        """Moderate anonymization for medium trust"""
        for field in ['description', 'pattern']:
            if field in data:
                text = data[field]
                # Anonymize student and staff IDs
                text = re.sub(self.EDUCATION_PATTERNS['student_id'], 'uXXXXXXXX', text)
                text = re.sub(self.EDUCATION_PATTERNS['staff_id'], 'sXXXXXXX', text)
                # Anonymize specific locations
                text = re.sub(self.EDUCATION_PATTERNS['campus_building'], 'Building XX', text)
                data[field] = text
        return data
    
    def apply_full_anonymization(self, data):
        """Full anonymization for low trust"""
        for field in ['description', 'pattern']:
            if field in data:
                text = data[field]
                # Apply all education patterns
                for pattern_name, pattern in self.EDUCATION_PATTERNS.items():
                    replacement = self.get_replacement(pattern_name)
                    text = re.sub(pattern, replacement, text)
                data[field] = text
        return data
    
    def get_replacement(self, pattern_name):
        """Get appropriate replacement for pattern"""
        replacements = {
            'student_id': 'uXXXXXXXX',
            'staff_id': 'sXXXXXXX',
            'course_code': 'XXXNNN',
            'campus_building': 'Building XX',
            'residence': 'Res XXXXX',
        }
        return replacements.get(pattern_name, 'XXXXX')
```

#### 2. Integration Setup
```python
# File: crisp_threat_intel/apps.py
from django.apps import AppConfig

class CrispThreatIntelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crisp_threat_intel'
    
    def ready(self):
        """Setup anonymization strategies on app ready"""
        self.setup_anonymization_strategies()
    
    def setup_anonymization_strategies(self):
        """Register all anonymization strategies"""
        from .strategies.anonymization import AnonymizationStrategyFactory
        from .strategies.education_strategy import EducationalInstitutionStrategy
        
        # Register education strategy
        AnonymizationStrategyFactory.register_strategy(
            'education',
            EducationalInstitutionStrategy()
        )
```

#### 3. Usage in Models
```python
# File: crisp_threat_intel/models.py (addition)
class Organization(models.Model):
    # ... existing fields ...
    
    organization_type = models.CharField(max_length=50, choices=[
        ('university', 'University'),
        ('college', 'College'),
        ('school', 'School'),
        ('government', 'Government'),
        ('commercial', 'Commercial'),
    ], default='university')
    
    def get_preferred_anonymization_strategy(self):
        """Get preferred anonymization strategy for this organization type"""
        if self.organization_type in ['university', 'college', 'school']:
            return 'education'
        else:
            return 'domain'  # Default strategy
```

---

## Best Practices

### 1. Strategy Design Guidelines

#### Principle of Least Exposure
- Only anonymize what is necessary for the trust level
- Preserve maximum analytical value
- Document what is anonymized and why

#### Consistency
- Use consistent anonymization patterns across similar data types
- Maintain referential integrity during anonymization
- Ensure reproducible results for the same input and trust level

#### Validation
- Always validate anonymized objects maintain STIX compliance
- Test anonymization effectiveness regularly
- Monitor for data leakage through correlation

### 2. Trust Management Guidelines

#### Dynamic Trust Adjustment
- Regularly review and update trust relationships
- Consider interaction history in trust calculations
- Implement feedback mechanisms for trust level optimization

#### Community Trust Networks
- Establish trust networks for related organizations
- Use graduated trust levels within networks
- Implement trust inheritance for network hierarchies

### 3. Performance Guidelines

#### Caching Strategy
- Cache frequently anonymized objects
- Use appropriate cache TTL based on data sensitivity
- Monitor cache hit rates and adjust as needed

#### Batch Processing
- Process large datasets in batches
- Use asynchronous processing for large operations
- Implement progress tracking for long-running operations

### 4. Security Guidelines

#### Regular Auditing
- Audit anonymization effectiveness regularly
- Monitor for potential data correlation attacks
- Review trust relationships periodically

#### Error Handling
- Fail securely when anonymization fails
- Log anonymization errors without exposing sensitive data
- Implement fallback anonymization strategies

This guide provides a comprehensive framework for extending and customizing the CRISP anonymization system. The modular design allows for easy integration of new strategies while maintaining the security and effectiveness of the threat intelligence sharing platform.