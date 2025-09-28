"""
Management command to create sample behavior logs for testing
"""

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models.user_behavior_models import UserSession, UserActivityLog, BehaviorAnomaly, BehaviorAlert

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample behavior logs for testing'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7, help='Number of days of sample data to create')
        parser.add_argument('--users', type=int, default=5, help='Number of users to create logs for')

    def handle(self, *args, **options):
        days = options['days']
        num_users = options['users']
        
        self.stdout.write(f'Creating {days} days of sample behavior logs for {num_users} users...')
        
        # Get or create sample users
        users = []
        for i in range(num_users):
            username = f'testuser{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'Test',
                    'last_name': f'User {i+1}',
                    'is_active': True
                }
            )
            users.append(user)
            if created:
                self.stdout.write(f'Created user: {username}')
        
        # Create sample activity logs
        activity_types = ['login', 'logout', 'api_call', 'data_access', 'incident_create', 'export_data']
        endpoints = ['/api/soc/incidents/', '/api/indicators/', '/api/threat-feeds/', '/api/auth/profile/', '/api/alerts/']
        ip_addresses = ['192.168.1.100', '192.168.1.101', '192.168.1.102', '10.0.0.50', '172.16.0.10']
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        created_activities = 0
        created_sessions = 0
        
        for user in users:
            # Create sessions
            for day in range(days):
                date = start_date + timedelta(days=day)
                
                # Random number of sessions per day (1-3)
                sessions_per_day = random.randint(1, 3)
                
                for session_num in range(sessions_per_day):
                    session_start = date.replace(
                        hour=random.randint(8, 18),
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    session_duration = random.randint(30, 480)  # 30 minutes to 8 hours
                    session_end = session_start + timedelta(minutes=session_duration)
                    
                    session = UserSession.objects.create(
                        user=user,
                        session_key=f'sess_{user.id}_{day}_{session_num}',
                        start_time=session_start,
                        end_time=session_end,
                        duration_minutes=session_duration,
                        ip_address=random.choice(ip_addresses),
                        user_agent='Mozilla/5.0 Test Browser',
                        api_calls_count=random.randint(5, 50),
                        endpoints_accessed=random.sample(endpoints, random.randint(2, 4)),
                        data_records_accessed=random.randint(1, 100),
                        incidents_created=random.randint(0, 3),
                        incidents_modified=random.randint(0, 5),
                        is_anomalous=random.choice([True, False]) if random.random() < 0.1 else False
                    )
                    created_sessions += 1
                    
                    # Create activity logs for this session
                    activities_per_session = random.randint(5, 20)
                    
                    for activity_num in range(activities_per_session):
                        activity_time = session_start + timedelta(
                            minutes=random.randint(0, int(session_duration))
                        )
                        
                        UserActivityLog.objects.create(
                            user=user,
                            session=session,
                            action_type=random.choice(activity_types),
                            endpoint=random.choice(endpoints),
                            method=random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                            ip_address=session.ip_address,
                            user_agent=session.user_agent,
                            response_status=random.choice([200, 201, 204, 400, 403, 404, 500]),
                            request_data={},
                            success=random.choice([True, False]) if random.random() < 0.1 else True,
                            duration_ms=random.randint(50, 2000),
                            timestamp=activity_time
                        )
                        created_activities += 1
        
        # Create some sample anomalies
        for user in users:
            if random.random() < 0.3:  # 30% chance of having anomalies
                anomaly_time = start_date + timedelta(
                    days=random.randint(0, days-1),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                BehaviorAnomaly.objects.create(
                    user=user,
                    anomaly_type=random.choice(['login_frequency', 'login_time', 'api_usage', 'data_access']),
                    severity=random.choice(['low', 'medium', 'high', 'critical']),
                    confidence_score=random.randint(60, 95),
                    title=f'Unusual behavior detected for {user.username}',
                    description=f'Sample anomaly detected in user behavior patterns',
                    detection_method='Statistical analysis',
                    baseline_value=random.uniform(1.0, 10.0),
                    observed_value=random.uniform(15.0, 50.0),
                    deviation_percentage=random.uniform(150.0, 500.0),
                    detected_at=anomaly_time
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {created_activities} activity logs\n'
                f'- {created_sessions} user sessions\n'
                f'- Sample anomalies for testing'
            )
        )