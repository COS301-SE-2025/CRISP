from locust import HttpUser, task, between
import json
import random


class CRISPUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Called when a user starts"""
        # Try to login and get a token
        self.login()

    def login(self):
        """Authenticate user and get JWT token"""
        response = self.client.post("/api/auth/login/", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access", "")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def view_admin_page(self):
        """Test admin page load"""
        self.client.get("/admin/")

    @task(2)
    def api_health_check(self):
        """Test API health endpoint"""
        self.client.get("/api/health/")

    @task(4)
    def list_threat_feeds(self):
        """Test threat feeds listing"""
        self.client.get("/api/threat-feeds/")

    @task(3)
    def list_indicators(self):
        """Test indicators listing"""
        self.client.get("/api/indicators/")

    @task(2)
    def get_user_profile(self):
        """Test user profile endpoint"""
        if self.token:
            self.client.get("/api/user/profile/")

    @task(1)
    def create_test_data(self):
        """Test creating test data"""
        if self.token:
            test_data = {
                "name": f"Test Feed {random.randint(1000, 9999)}",
                "description": "Performance test feed",
                "feed_type": "test"
            }
            self.client.post("/api/threat-feeds/", json=test_data)

    @task(1)
    def search_indicators(self):
        """Test searching indicators"""
        search_terms = ["malware", "phishing", "trojan", "apt"]
        term = random.choice(search_terms)
        self.client.get(f"/api/indicators/?search={term}")

    @task(1)
    def get_trust_relationships(self):
        """Test trust relationships endpoint"""
        if self.token:
            self.client.get("/api/trust/relationships/")


class AdminUser(HttpUser):
    """Heavy admin operations"""
    wait_time = between(2, 5)
    weight = 1  # Lower weight than regular users

    def on_start(self):
        """Admin login"""
        response = self.client.post("/api/auth/login/", json={
            "username": "admin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access", "")
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(2)
    def admin_dashboard(self):
        """Test admin dashboard"""
        self.client.get("/admin/")

    @task(1)
    def bulk_operations(self):
        """Test bulk operations"""
        self.client.get("/api/admin/bulk-operations/")

    @task(1)
    def system_metrics(self):
        """Test system metrics"""
        self.client.get("/api/admin/metrics/")


class APIOnlyUser(HttpUser):
    """API-focused user for testing API performance"""
    wait_time = between(0.5, 2)
    weight = 3

    @task(5)
    def api_endpoints(self):
        """Test various API endpoints"""
        endpoints = [
            "/api/indicators/",
            "/api/threat-feeds/",
            "/api/taxii/collections/",
            "/api/health/",
        ]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)

    @task(2)
    def pagination_test(self):
        """Test pagination performance"""
        page = random.randint(1, 10)
        self.client.get(f"/api/indicators/?page={page}&page_size=50")

    @task(1)
    def filtering_test(self):
        """Test filtering performance"""
        filters = [
            "?type=ip",
            "?confidence=high",
            "?created_date__gte=2024-01-01",
            "?status=active"
        ]
        filter_param = random.choice(filters)
        self.client.get(f"/api/indicators/{filter_param}")


# Custom task for stress testing specific endpoints
class StressTestUser(HttpUser):
    """High-frequency requests for stress testing"""
    wait_time = between(0.1, 0.5)
    weight = 1

    @task
    def rapid_fire_requests(self):
        """Rapid requests to test system under load"""
        self.client.get("/api/health/")
        self.client.get("/api/threat-feeds/")
        self.client.get("/api/indicators/?page_size=10")