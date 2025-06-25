"""
Performance and Stress Tests for Trust Management

These tests ensure the trust management system performs well under load
and maintains acceptable response times even with large datasets.
"""

import uuid
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.test.utils import override_settings
from datetime import timedelta
from unittest.mock import patch

from ..models import (
    TrustLevel, TrustGroup, TrustRelationship, TrustGroupMembership, TrustLog
)
from ..services.trust_service import TrustService
from ..services.trust_group_service import TrustGroupService
from ..validators import validate_trust_operation


class PerformanceBaselineTest(TestCase):
    """Establish performance baselines for trust operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_levels = []
        for i, level in enumerate(['low', 'medium', 'high']):
            trust_level = TrustLevel.objects.create(
                name=f'{level.title()} Performance Test',
                level=level,
                description=f'{level.title()} trust level for performance testing',
                numerical_value=25 + (i * 25),
                default_anonymization_level='partial',
                default_access_level='read',
                created_by='performance_tester'
            )
            self.trust_levels.append(trust_level)
        
        # Create test organizations
        self.organizations = [str(uuid.uuid4()) for _ in range(100)]
        self.test_user = 'performance_test_user'
    
    def measure_operation_time(self, operation_func, *args, **kwargs):
        """Measure the execution time of an operation."""
        start_time = time.time()
        result = operation_func(*args, **kwargs)
        end_time = time.time()
        return result, (end_time - start_time)
    
    def test_trust_relationship_creation_performance(self):
        """Test performance of trust relationship creation."""
        times = []
        
        for i in range(50):  # Create 50 relationships
            source_org = self.organizations[i]
            target_org = self.organizations[i + 50]
            
            _, execution_time = self.measure_operation_time(
                TrustService.create_trust_relationship,
                source_org=source_org,
                target_org=target_org,
                trust_level_name=self.trust_levels[0].name,
                created_by=self.test_user
            )
            times.append(execution_time)
        
        # Performance assertions
        avg_time = statistics.mean(times)
        max_time = max(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
        
        self.assertLess(avg_time, 0.1, f"Average creation time {avg_time:.3f}s exceeds 100ms")
        self.assertLess(max_time, 0.5, f"Maximum creation time {max_time:.3f}s exceeds 500ms")
        self.assertLess(p95_time, 0.2, f"95th percentile time {p95_time:.3f}s exceeds 200ms")
        
        print(f"Trust Relationship Creation - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s, P95: {p95_time:.3f}s")
    
    def test_trust_level_checking_performance(self):
        """Test performance of trust level checking."""
        # Create some relationships first
        relationships = []
        for i in range(20):
            relationship = TrustService.create_trust_relationship(
                source_org=self.organizations[i],
                target_org=self.organizations[i + 20],
                trust_level_name=self.trust_levels[1].name,
                created_by=self.test_user
            )
            relationship.approved_by_source = True
            relationship.approved_by_target = True
            relationship.activate()
            relationships.append(relationship)
        
        # Measure trust checking performance
        times = []
        for i in range(100):  # Check 100 times
            source_org = self.organizations[i % 20]
            target_org = self.organizations[(i % 20) + 20]
            
            _, execution_time = self.measure_operation_time(
                TrustService.check_trust_level,
                source_org, target_org
            )
            times.append(execution_time)
        
        # Performance assertions
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        self.assertLess(avg_time, 0.05, f"Average check time {avg_time:.3f}s exceeds 50ms")
        self.assertLess(max_time, 0.2, f"Maximum check time {max_time:.3f}s exceeds 200ms")
        
        print(f"Trust Level Checking - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
    
    def test_intelligence_access_validation_performance(self):
        """Test performance of intelligence access validation."""
        # Create relationships for testing
        for i in range(10):
            relationship = TrustService.create_trust_relationship(
                source_org=self.organizations[i],
                target_org=self.organizations[i + 10],
                trust_level_name=self.trust_levels[2].name,
                created_by=self.test_user
            )
            relationship.approved_by_source = True
            relationship.approved_by_target = True
            relationship.activate()
        
        # Measure access validation performance
        times = []
        for i in range(100):
            requesting_org = self.organizations[i % 10]
            intelligence_owner = self.organizations[(i % 10) + 10]
            
            _, execution_time = self.measure_operation_time(
                TrustService.can_access_intelligence,
                requesting_org=requesting_org,
                intelligence_owner=intelligence_owner,
                required_access_level='read'
            )
            times.append(execution_time)
        
        avg_time = statistics.mean(times)
        self.assertLess(avg_time, 0.05, f"Average access validation time {avg_time:.3f}s exceeds 50ms")
        
        print(f"Intelligence Access Validation - Avg: {avg_time:.3f}s")
    
    def test_trust_group_operations_performance(self):
        """Test performance of trust group operations."""
        # Create trust group
        group_creation_time = self.measure_operation_time(
            TrustGroupService.create_trust_group,
            name='Performance Test Group',
            description='Group for performance testing',
            creator_org=self.organizations[0],
            default_trust_level_name=self.trust_levels[1].name
        )[1]
        
        self.assertLess(group_creation_time, 0.1, f"Group creation time {group_creation_time:.3f}s exceeds 100ms")
        
        # Get the created group
        group = TrustGroup.objects.get(name='Performance Test Group')
        
        # Test joining performance
        join_times = []
        for i in range(20):
            _, join_time = self.measure_operation_time(
                TrustGroupService.join_trust_group,
                group_id=str(group.id),
                organization=self.organizations[i + 1],
                user=f'user_{i}'
            )
            join_times.append(join_time)
        
        avg_join_time = statistics.mean(join_times)
        self.assertLess(avg_join_time, 0.1, f"Average join time {avg_join_time:.3f}s exceeds 100ms")
        
        print(f"Trust Group Creation: {group_creation_time:.3f}s, Avg Join: {avg_join_time:.3f}s")


class LoadTestingTest(TransactionTestCase):
    """Test system behavior under various load conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Load Test Trust Level',
            level='medium',
            description='Trust level for load testing',
            numerical_value=50,
            default_anonymization_level='partial',
            default_access_level='read',
            created_by='load_tester'
        )
        
        # Create many organizations for load testing
        self.organizations = [str(uuid.uuid4()) for _ in range(500)]
    
    def test_concurrent_relationship_creation(self):
        """Test concurrent creation of trust relationships."""
        def create_relationship(org_pair):
            source_org, target_org, user_id = org_pair
            try:
                start_time = time.time()
                relationship = TrustService.create_trust_relationship(
                    source_org=source_org,
                    target_org=target_org,
                    trust_level_name='Load Test Trust Level',
                    created_by=f'user_{user_id}'
                )
                end_time = time.time()
                return True, end_time - start_time
            except Exception as e:
                return False, str(e)
        
        # Prepare org pairs for testing
        org_pairs = [
            (self.organizations[i], self.organizations[i + 250], i)
            for i in range(100)  # 100 concurrent operations
        ]
        
        # Execute concurrent operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_relationship, pair) for pair in org_pairs]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_ops = [r for r in results if r[0]]
        failed_ops = [r for r in results if not r[0]]
        
        success_rate = len(successful_ops) / len(results)
        self.assertGreater(success_rate, 0.95, f"Success rate {success_rate:.2%} below 95%")
        
        if successful_ops:
            avg_time = statistics.mean([r[1] for r in successful_ops])
            self.assertLess(avg_time, 1.0, f"Average time {avg_time:.3f}s exceeds 1 second")
        
        print(f"Concurrent Creation - Success Rate: {success_rate:.2%}, Failures: {len(failed_ops)}")
    
    def test_bulk_approval_performance(self):
        """Test performance of bulk approval operations."""
        # Create many pending relationships
        relationships = []
        for i in range(50):
            relationship = TrustService.create_trust_relationship(
                source_org=self.organizations[i],
                target_org=self.organizations[i + 50],
                trust_level_name='Load Test Trust Level',
                created_by=f'bulk_user_{i}'
            )
            relationships.append(relationship)
        
        def approve_relationship(rel_and_user):
            relationship, user_id = rel_and_user
            try:
                start_time = time.time()
                # Approve from source
                TrustService.approve_trust_relationship(
                    relationship_id=str(relationship.id),
                    approving_org=relationship.source_organization,
                    approved_by_user=f'approver_{user_id}'
                )
                # Approve from target
                TrustService.approve_trust_relationship(
                    relationship_id=str(relationship.id),
                    approving_org=relationship.target_organization,
                    approved_by_user=f'approver_{user_id}'
                )
                end_time = time.time()
                return True, end_time - start_time
            except Exception as e:
                return False, str(e)
        
        # Execute bulk approvals
        rel_user_pairs = [(rel, i) for i, rel in enumerate(relationships)]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(approve_relationship, pair) for pair in rel_user_pairs]
            results = [future.result() for future in as_completed(futures)]
        
        successful_approvals = [r for r in results if r[0]]
        success_rate = len(successful_approvals) / len(results)
        
        self.assertGreater(success_rate, 0.90, f"Approval success rate {success_rate:.2%} below 90%")
        
        if successful_approvals:
            avg_time = statistics.mean([r[1] for r in successful_approvals])
            self.assertLess(avg_time, 0.5, f"Average approval time {avg_time:.3f}s exceeds 500ms")
        
        print(f"Bulk Approvals - Success Rate: {success_rate:.2%}")
    
    def test_large_dataset_query_performance(self):
        """Test query performance with large datasets."""
        # Create a large number of relationships
        print("Creating large dataset for query testing...")
        relationships = []
        
        # Create relationships in batches for better performance
        batch_size = 50
        for batch_start in range(0, 200, batch_size):
            batch_relationships = []
            for i in range(batch_start, min(batch_start + batch_size, 200)):
                relationship = TrustService.create_trust_relationship(
                    source_org=self.organizations[i],
                    target_org=self.organizations[i + 200],
                    trust_level_name='Load Test Trust Level',
                    created_by=f'query_user_{i}'
                )
                batch_relationships.append(relationship)
            relationships.extend(batch_relationships)
        
        print(f"Created {len(relationships)} relationships")
        
        # Test various query patterns
        query_times = {}
        
        # Test 1: Get relationships for organization
        start_time = time.time()
        org_relationships = TrustService.get_trust_relationships_for_organization(
            self.organizations[0]
        )
        query_times['get_org_relationships'] = time.time() - start_time
        
        # Test 2: Get sharing organizations
        start_time = time.time()
        sharing_orgs = TrustService.get_sharing_organizations(
            source_org=self.organizations[0],
            min_trust_level='low'
        )
        query_times['get_sharing_orgs'] = time.time() - start_time
        
        # Test 3: Check trust levels (multiple)
        start_time = time.time()
        for i in range(10):
            TrustService.check_trust_level(
                self.organizations[i], self.organizations[i + 200]
            )
        query_times['check_trust_levels'] = time.time() - start_time
        
        # Performance assertions
        for query_type, query_time in query_times.items():
            self.assertLess(
                query_time, 1.0, 
                f"{query_type} took {query_time:.3f}s, exceeds 1 second limit"
            )
        
        print(f"Query Performance: {query_times}")
    
    def test_memory_usage_under_load(self):
        """Test memory usage patterns under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        relationships = []
        for i in range(100):
            relationship = TrustService.create_trust_relationship(
                source_org=self.organizations[i],
                target_org=self.organizations[i + 100],
                trust_level_name='Load Test Trust Level',
                created_by=f'memory_user_{i}'
            )
            relationships.append(relationship)
            
            # Force garbage collection periodically
            if i % 20 == 0:
                import gc
                gc.collect()
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        self.assertLess(
            memory_increase, 100,
            f"Memory increase of {memory_increase:.1f}MB exceeds 100MB limit"
        )
        
        print(f"Memory Usage - Initial: {initial_memory:.1f}MB, Peak: {peak_memory:.1f}MB, Increase: {memory_increase:.1f}MB")
    
    def test_database_connection_handling(self):
        """Test database connection handling under load."""
        def database_operation(op_id):
            try:
                # Perform database operations
                relationships = TrustRelationship.objects.filter(
                    source_organization=self.organizations[op_id % 100]
                )
                count = relationships.count()
                
                # Create and query
                relationship = TrustService.create_trust_relationship(
                    source_org=self.organizations[op_id],
                    target_org=self.organizations[op_id + 200],
                    trust_level_name='Load Test Trust Level',
                    created_by=f'db_user_{op_id}'
                )
                
                return True, count
            except Exception as e:
                return False, str(e)
        
        # Execute many concurrent database operations
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(database_operation, i) for i in range(150)]
            results = [future.result() for future in as_completed(futures)]
        
        successful_ops = [r for r in results if r[0]]
        success_rate = len(successful_ops) / len(results)
        
        self.assertGreater(
            success_rate, 0.95,
            f"Database operation success rate {success_rate:.2%} below 95%"
        )
        
        print(f"Database Operations - Success Rate: {success_rate:.2%}")


class StressTestingTest(TransactionTestCase):
    """Stress testing to find system limits and breaking points."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trust_level = TrustLevel.objects.create(
            name='Stress Test Trust Level',
            level='medium',
            description='Trust level for stress testing',
            numerical_value=50,
            created_by='stress_tester'
        )
        
        # Create organizations for stress testing
        self.organizations = [str(uuid.uuid4()) for _ in range(1000)]
    
    def test_maximum_concurrent_operations(self):
        """Test system behavior at maximum concurrency."""
        max_workers = 50  # High concurrency
        operations_per_worker = 10
        
        def stress_operation(worker_id):
            results = []
            for i in range(operations_per_worker):
                try:
                    start_time = time.time()
                    
                    # Mix of different operations
                    if i % 3 == 0:
                        # Create relationship
                        relationship = TrustService.create_trust_relationship(
                            source_org=self.organizations[worker_id * operations_per_worker + i],
                            target_org=self.organizations[worker_id * operations_per_worker + i + 500],
                            trust_level_name='Stress Test Trust Level',
                            created_by=f'stress_worker_{worker_id}'
                        )
                        operation_type = 'create'
                    elif i % 3 == 1:
                        # Check trust level
                        TrustService.check_trust_level(
                            self.organizations[worker_id * 2],
                            self.organizations[worker_id * 2 + 500]
                        )
                        operation_type = 'check'
                    else:
                        # Access validation
                        TrustService.can_access_intelligence(
                            requesting_org=self.organizations[worker_id * 2],
                            intelligence_owner=self.organizations[worker_id * 2 + 500]
                        )
                        operation_type = 'access'
                    
                    end_time = time.time()
                    results.append((True, operation_type, end_time - start_time))
                    
                except Exception as e:
                    results.append((False, 'error', str(e)))
            
            return results
        
        # Execute maximum concurrency test
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(stress_operation, i) for i in range(max_workers)]
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_ops = [r for r in all_results if r[0]]
        failed_ops = [r for r in all_results if not r[0]]
        
        success_rate = len(successful_ops) / len(all_results)
        throughput = len(successful_ops) / total_time
        
        print(f"Stress Test Results:")
        print(f"  Total Operations: {len(all_results)}")
        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Throughput: {throughput:.1f} ops/sec")
        print(f"  Total Time: {total_time:.2f}s")
        
        # System should maintain reasonable performance under stress
        self.assertGreater(success_rate, 0.85, f"Success rate {success_rate:.2%} below 85%")
        self.assertGreater(throughput, 10, f"Throughput {throughput:.1f} ops/sec below 10")
    
    def test_resource_exhaustion_handling(self):
        """Test handling of resource exhaustion scenarios."""
        def resource_intensive_operation(op_id):
            try:
                # Create relationships with large metadata
                large_metadata = {'data': 'x' * 1000}  # 1KB of metadata
                large_notes = 'Large note content. ' * 100  # Large notes
                
                relationship = TrustService.create_trust_relationship(
                    source_org=self.organizations[op_id],
                    target_org=self.organizations[op_id + 500],
                    trust_level_name='Stress Test Trust Level',
                    created_by=f'resource_user_{op_id}',
                    notes=large_notes,
                    sharing_preferences=large_metadata
                )
                return True
            except Exception as e:
                return False, str(e)
        
        # Execute resource-intensive operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(resource_intensive_operation, i) for i in range(100)]
            results = [future.result() for future in as_completed(futures)]
        
        successful_ops = [r for r in results if r is True or (isinstance(r, tuple) and r[0])]
        success_rate = len(successful_ops) / len(results)
        
        # Should handle resource pressure gracefully
        self.assertGreater(success_rate, 0.80, f"Resource handling success rate {success_rate:.2%} below 80%")
        
        print(f"Resource Exhaustion Test - Success Rate: {success_rate:.2%}")
    
    def test_long_running_operations(self):
        """Test system stability with long-running operations."""
        def long_running_operation(duration_seconds):
            start_time = time.time()
            operations_completed = 0
            
            while time.time() - start_time < duration_seconds:
                try:
                    # Perform various operations
                    org_index = operations_completed % len(self.organizations)
                    
                    if operations_completed % 10 == 0:
                        # Create relationship
                        TrustService.create_trust_relationship(
                            source_org=self.organizations[org_index],
                            target_org=self.organizations[(org_index + 1) % len(self.organizations)],
                            trust_level_name='Stress Test Trust Level',
                            created_by=f'long_running_user_{operations_completed}'
                        )
                    else:
                        # Query operations
                        TrustService.check_trust_level(
                            self.organizations[org_index],
                            self.organizations[(org_index + 1) % len(self.organizations)]
                        )
                    
                    operations_completed += 1
                    
                    # Small delay to prevent overwhelming
                    time.sleep(0.01)
                    
                except Exception:
                    pass  # Continue despite errors
            
            return operations_completed
        
        # Run long-running test (30 seconds)
        test_duration = 30
        operations_completed = long_running_operation(test_duration)
        
        # Should complete reasonable number of operations
        min_expected_ops = test_duration * 10  # At least 10 ops/second
        self.assertGreater(
            operations_completed, min_expected_ops,
            f"Only completed {operations_completed} operations in {test_duration}s"
        )
        
        print(f"Long Running Test - Completed {operations_completed} operations in {test_duration}s")
    
    def test_error_recovery_under_stress(self):
        """Test system recovery from errors under stress."""
        def error_prone_operation(op_id):
            results = {'success': 0, 'errors': 0}
            
            for i in range(5):
                try:
                    if i == 2:  # Inject error in middle
                        # Try to create invalid relationship
                        TrustService.create_trust_relationship(
                            source_org=self.organizations[op_id],
                            target_org=self.organizations[op_id],  # Same org (invalid)
                            trust_level_name='Stress Test Trust Level',
                            created_by=f'error_user_{op_id}'
                        )
                    else:
                        # Valid operation
                        TrustService.create_trust_relationship(
                            source_org=self.organizations[op_id],
                            target_org=self.organizations[op_id + 500 + i],
                            trust_level_name='Stress Test Trust Level',
                            created_by=f'recovery_user_{op_id}_{i}'
                        )
                    
                    results['success'] += 1
                    
                except Exception:
                    results['errors'] += 1
            
            return results
        
        # Execute error-prone operations
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(error_prone_operation, i) for i in range(50)]
            all_results = [future.result() for future in as_completed(futures)]
        
        total_success = sum(r['success'] for r in all_results)
        total_errors = sum(r['errors'] for r in all_results)
        
        # Should recover and continue processing after errors
        self.assertGreater(total_success, total_errors, "More errors than successes")
        
        # Each worker should complete some successful operations despite errors
        successful_workers = sum(1 for r in all_results if r['success'] > 0)
        self.assertGreater(successful_workers, 40, "Too few workers completed successful operations")
        
        print(f"Error Recovery Test - Success: {total_success}, Errors: {total_errors}")


class EnduranceTestingTest(TransactionTestCase):
    """Test system endurance over extended periods."""
    
    @override_settings(DEBUG=False)  # Disable debug to reduce memory usage
    def test_memory_leak_detection(self):
        """Test for memory leaks over extended operation."""
        import psutil
        import os
        import gc
        
        process = psutil.Process(os.getpid())
        
        # Create trust level
        trust_level = TrustLevel.objects.create(
            name='Endurance Test Trust Level',
            level='medium',
            description='Trust level for endurance testing',
            numerical_value=50,
            created_by='endurance_tester'
        )
        
        organizations = [str(uuid.uuid4()) for _ in range(200)]
        
        # Measure memory at intervals
        memory_measurements = []
        operations_per_measurement = 50
        
        for cycle in range(10):  # 10 cycles
            cycle_start_memory = process.memory_info().rss / 1024 / 1024
            
            # Perform operations
            for i in range(operations_per_measurement):
                # Create relationship
                try:
                    relationship = TrustService.create_trust_relationship(
                        source_org=organizations[i % 200],
                        target_org=organizations[(i + cycle * 50) % 200],
                        trust_level_name='Endurance Test Trust Level',
                        created_by=f'endurance_user_{cycle}_{i}'
                    )
                except Exception:
                    # Skip if relationship already exists
                    relationship = None
                
                # Query operations
                TrustService.check_trust_level(
                    organizations[i % 200],
                    organizations[(i + cycle * 50) % 200]
                )
                
                # Clean up some data periodically
                if i % 10 == 0:
                    # Delete old relationships to test cleanup
                    old_relationships = TrustRelationship.objects.filter(
                        created_by__startswith=f'endurance_user_{max(0, cycle-2)}'
                    )[:5]
                    for old_rel in old_relationships:
                        old_rel.delete()
            
            # Force garbage collection
            gc.collect()
            
            cycle_end_memory = process.memory_info().rss / 1024 / 1024
            memory_measurements.append(cycle_end_memory)
            
            print(f"Cycle {cycle}: Memory {cycle_end_memory:.1f}MB")
        
        # Analyze memory trend
        if len(memory_measurements) >= 3:
            # Check if memory is continuously growing
            recent_avg = statistics.mean(memory_measurements[-3:])
            early_avg = statistics.mean(memory_measurements[:3])
            memory_growth = recent_avg - early_avg
            
            # Allow some growth but not excessive
            max_allowed_growth = 50  # MB
            self.assertLess(
                memory_growth, max_allowed_growth,
                f"Potential memory leak detected: {memory_growth:.1f}MB growth"
            )
        
        print(f"Memory measurements: {memory_measurements}")
        print(f"Memory growth: {memory_measurements[-1] - memory_measurements[0]:.1f}MB")
    
    def test_database_performance_degradation(self):
        """Test for database performance degradation over time."""
        trust_level = TrustLevel.objects.create(
            name='DB Perf Test Trust Level',
            level='medium',
            description='Trust level for DB performance testing',
            numerical_value=50,
            created_by='db_perf_tester'
        )
        
        organizations = [str(uuid.uuid4()) for _ in range(300)]
        
        # Measure query performance over time
        performance_measurements = []
        
        for batch in range(10):  # 10 batches
            # Create relationships
            for i in range(30):  # 30 per batch
                source_idx = (batch * 30 + i) % len(organizations)
                target_idx = (batch * 30 + i + 50) % len(organizations)
                
                if source_idx != target_idx:  # Avoid self-relationships
                    try:
                        TrustService.create_trust_relationship(
                            source_org=organizations[source_idx],
                            target_org=organizations[target_idx],
                            trust_level_name='DB Perf Test Trust Level',
                            created_by=f'db_user_{batch}_{i}'
                        )
                    except Exception:
                        # Skip if relationship already exists
                        continue
            
            # Measure query performance
            start_time = time.time()
            for i in range(20):  # 20 queries
                TrustService.get_trust_relationships_for_organization(
                    organizations[i % 100]
                )
            end_time = time.time()
            
            avg_query_time = (end_time - start_time) / 20
            performance_measurements.append(avg_query_time)
            
            print(f"Batch {batch}: Avg query time {avg_query_time:.4f}s")
        
        # Check for performance degradation
        if len(performance_measurements) >= 3:
            early_avg = statistics.mean(performance_measurements[:3])
            recent_avg = statistics.mean(performance_measurements[-3:])
            degradation_ratio = recent_avg / early_avg
            
            # Performance shouldn't degrade more than 50%
            self.assertLess(
                degradation_ratio, 1.5,
                f"Performance degraded by {(degradation_ratio-1)*100:.1f}%"
            )
        
        print(f"Performance ratio (recent/early): {degradation_ratio:.2f}")


# Performance monitoring utilities
class PerformanceMonitor:
    """Utility class for monitoring performance during tests."""
    
    def __init__(self):
        self.measurements = {}
    
    def start_measurement(self, operation_name):
        """Start measuring an operation."""
        self.measurements[operation_name] = {'start': time.time()}
    
    def end_measurement(self, operation_name):
        """End measuring an operation."""
        if operation_name in self.measurements:
            self.measurements[operation_name]['end'] = time.time()
            self.measurements[operation_name]['duration'] = (
                self.measurements[operation_name]['end'] - 
                self.measurements[operation_name]['start']
            )
    
    def get_measurement(self, operation_name):
        """Get measurement for an operation."""
        return self.measurements.get(operation_name, {}).get('duration')
    
    def get_summary(self):
        """Get summary of all measurements."""
        summary = {}
        for op_name, data in self.measurements.items():
            if 'duration' in data:
                summary[op_name] = data['duration']
        return summary