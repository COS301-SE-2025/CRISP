#!/usr/bin/env python
"""
CRISP Database Population Script
Creates test data with parallel processing for development and testing.
"""

import os
import sys
import random
import uuid
import time
import secrets
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from faker import Faker

# Install tqdm if not available
try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm for progress bars...")
    os.system("pip install tqdm")
    from tqdm import tqdm

from core.models.models import (
    Organization, ThreatFeed, Collection, Feed, SystemActivity, UserProfile
)
from core.user_management.models.user_models import CustomUser, UserSession
from core.user_management.models.invitation_models import UserInvitation
from core.trust_management.models.trust_models import (
    TrustLevel, TrustRelationship, TrustGroup, TrustGroupMembership
)

fake = Faker()

class Command(BaseCommand):
    help = 'Populate database with test data for development and testing'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organizations = []
        self.users = []
        self.trust_levels = []
        self.trust_groups = []
        self.admin_password = None
        self.user_password = None
        
        # Scale parameters for test data generation
        self.NUM_ORGANIZATIONS = 10
        self.USERS_PER_ORG = (5, 15)
        self.NUM_TRUST_RELATIONSHIPS = 30
        self.NUM_TRUST_GROUPS = 5
        self.NUM_USER_SESSIONS = 100
        self.NUM_THREAT_FEEDS = 5
        
        self.MAX_WORKERS = min(cpu_count(), 8)
        self.BATCH_SIZE = 25

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Run without user confirmation',
        )

    def handle(self, *args, **options):
        start_time = time.time()
        self.stdout.write("Starting CRISP Database Population...")

        if not options['no_input']:
            confirm = input("This will clear existing data. Continue? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write("Cancelled.")
                return

        try:
            phases = [
                ("Phase 1/9: Clearing Data", self.clear_existing_data),
                ("Phase 2/9: Trust Levels", self.create_trust_levels),
                ("Phase 3/9: Organizations", self.create_organizations),
                ("Phase 4/9: Super Admins", self.create_super_admin_users),
                ("Phase 5/9: Users", self.create_users),
                ("Phase 6/9: Trust Relationships", self.create_trust_relationships),
                ("Phase 7/9: Trust Groups", self.create_trust_groups),
                ("Phase 8/9: User Sessions", self.create_user_sessions),
                ("Phase 9/9: Threat Feeds", self.create_threat_feeds),
            ]
            
            for phase_name, phase_func in phases:
                self.stdout.write(f"\n{phase_name}")
                phase_func()
            
            self.print_summary()
            
        except Exception as e:
            self.stdout.write(f"Error during population: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _get_password(self, env_var, role_name):
        """Get password from environment or generate a random one."""
        password = os.getenv(env_var)
        if password:
            self.stdout.write(self.style.SUCCESS(f'Using password from {env_var} for {role_name} users.'))
            return password
        
        password = secrets.token_urlsafe(16)
        self.stdout.write(self.style.WARNING(f'{env_var} not set. Generated a random password for {role_name} users.'))
        return password

    def clear_existing_data(self):
        # ... (implementation remains the same)
        pass

    def create_trust_levels(self):
        # ... (implementation remains the same)
        pass

    def create_organizations(self):
        # ... (implementation remains the same)
        pass

    def create_super_admin_users(self):
        self.stdout.write("Creating super admin users...")
        self.admin_password = self._get_password('DEFAULT_ADMIN_PASSWORD', 'super admin')
        
        super_admins = [
            ('demo', 'demo@crisp.com', 'Demo Account'),
            ('test', 'test@crisp.com', 'Test Account'),
        ]
        
        for username, email, first_name in super_admins:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': 'User',
                    'is_superuser': True,
                    'is_staff': True,
                    'role': 'BlueVisionAdmin',
                    'is_active': True,
                }
            )
            if created:
                user.set_password(self.admin_password)
                user.save()
            self.users.append(user)
            
        self.stdout.write(f"Created {len(super_admins)} super admin users")

    def create_user_batch(self, org_user_data):
        org, user_count = org_user_data
        created_users = []
        
        for i in range(user_count):
            try:
                with transaction.atomic():
                    user = CustomUser.objects.create(
                        username=f"{fake.user_name()}{uuid.uuid4().hex[:6]}",
                        email=fake.email(),
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        organization=org,
                        role=random.choice(['viewer', 'publisher']),
                        is_active=True
                    )
                    user.set_password(self.user_password)
                    user.save()
                    created_users.append(user)
            except Exception:
                continue
        return created_users

    def create_users(self):
        self.stdout.write(f"Creating users for {len(self.organizations)} organizations...")
        self.user_password = self._get_password('DEFAULT_USER_PASSWORD', 'regular')
        
        org_user_pairs = [(org, random.randint(*self.USERS_PER_ORG)) for org in self.organizations]
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = [executor.submit(self.create_user_batch, org_data) for org_data in org_user_pairs]
            for future in as_completed(futures):
                self.users.extend(future.result())
                        
        self.stdout.write(f"Created {len(self.users)} users")

    def create_trust_relationships(self):
        # ... (implementation remains the same)
        pass

    def create_trust_groups(self):
        # ... (implementation remains the same)
        pass

    def create_user_sessions(self):
        # ... (implementation remains the same)
        pass

    def create_threat_feeds(self):
        # ... (implementation remains the same)
        pass

    def print_summary(self):
        self.stdout.write("="*100)
        self.stdout.write("DATABASE POPULATION COMPLETE!")
        self.stdout.write("="*100)
        self.stdout.write("Summary of created data:")
        self.stdout.write(f"  Organizations: {len(self.organizations)}")
        self.stdout.write(f"  Users: {len(self.users)}")
        self.stdout.write("Login credentials:")
        if self.admin_password:
            self.stdout.write("  Super Admins (demo, test):")
            self.stdout.write(self.style.SUCCESS(f"    Password: {self.admin_password}"))
        if self.user_password:
            self.stdout.write("  Regular Users:")
            self.stdout.write(self.style.SUCCESS(f"    Password: {self.user_password}"))
        self.stdout.write(self.style.WARNING("Please save these passwords. They will not be shown again."))
        self.stdout.write("="*100)
