/**
 * K6 COMPREHENSIVE LOAD TEST - CRISP System
 * Tests all 46+ API endpoints with detailed metrics and monitoring
 * 
 * Usage:
 *   Smoke Test:  k6 run --env TEST_TYPE=smoke scripts/testing/k6-load-test.js
 *   Load Test:   k6 run --env TEST_TYPE=load scripts/testing/k6-load-test.js
 *   Stress Test: k6 run --env TEST_TYPE=stress scripts/testing/k6-load-test.js
 *   Spike Test:  k6 run --env TEST_TYPE=spike scripts/testing/k6-load-test.js
 *   Soak Test:   k6 run --env TEST_TYPE=soak scripts/testing/k6-load-test.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// ==================== CUSTOM METRICS ====================
const errorRate = new Rate('errors');
const successRate = new Rate('success');
const authErrors = new Counter('auth_errors');
const socEndpoints = new Counter('soc_endpoints_called');
const threatEndpoints = new Counter('threat_endpoints_called');
const cacheHitEstimate = new Rate('cache_hit_estimate');
const fastResponses = new Rate('fast_responses'); // < 200ms

// ==================== TEST SCENARIOS ====================
const scenarios = {
  smoke: {
    executor: 'constant-vus',
    vus: 1,
    duration: '1m',
  },
  load: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '2m', target: 10 },  // Ramp up to 10 users
      { duration: '5m', target: 10 },  // Stay at 10 for 5 minutes
      { duration: '2m', target: 30 },  // Ramp to 30 users
      { duration: '5m', target: 30 },  // Stay at 30 for 5 minutes
      { duration: '2m', target: 0 },   // Ramp down to 0
    ],
  },
  stress: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '2m', target: 20 },   // Ramp up to 20
      { duration: '5m', target: 20 },   // Stay at 20
      { duration: '2m', target: 50 },   // Ramp to 50
      { duration: '5m', target: 50 },   // Stay at 50
      { duration: '2m', target: 100 },  // Ramp to 100
      { duration: '5m', target: 100 },  // Stay at 100
      { duration: '5m', target: 0 },    // Ramp down
    ],
  },
  spike: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '30s', target: 10 },  // Gradual ramp
      { duration: '1m', target: 10 },   // Stay low
      { duration: '10s', target: 100 }, // SPIKE!
      { duration: '3m', target: 100 },  // Stay at spike
      { duration: '10s', target: 10 },  // Drop
      { duration: '1m', target: 10 },   // Recover
      { duration: '30s', target: 0 },   // End
    ],
  },
  soak: {
    executor: 'constant-vus',
    vus: 20,
    duration: '30m', // 30 minute soak test
  },
};

// ==================== TEST CONFIGURATION ====================
const testType = __ENV.TEST_TYPE || 'load';
const baseURL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  scenarios: {
    [testType]: scenarios[testType],
  },
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    'http_req_failed': ['rate<0.05'],                 // Error rate < 5%
    'errors': ['rate<0.1'],                           // Custom error rate < 10%
    'success': ['rate>0.9'],                          // Success rate > 90%
    'fast_responses': ['rate>0.7'],                   // 70% of responses < 200ms
  },
  summaryTrendStats: ['min', 'med', 'avg', 'p(90)', 'p(95)', 'p(99)', 'max'],
};

// ==================== SETUP: LOGIN & GET TOKEN ====================
export function setup() {
  console.log(`🚀 Starting ${testType.toUpperCase()} test against ${baseURL}`);
  
  const loginPayload = JSON.stringify({
    username: 'admin',
    password: 'admin123',
  });

  const loginRes = http.post(`${baseURL}/api/auth/login/`, loginPayload, {
    headers: { 'Content-Type': 'application/json' },
  });

  const loginCheck = check(loginRes, {
    '✅ Login successful': (r) => r.status === 200,
    '✅ Token received': (r) => r.json('access') !== undefined,
  });

  if (!loginCheck) {
    console.error('❌ LOGIN FAILED! Cannot proceed with tests.');
    authErrors.add(1);
    return { token: null };
  }

  const token = loginRes.json('access');
  console.log('✅ Authentication successful, token acquired');
  return { token };
}

// ==================== MAIN TEST FUNCTION ====================
export default function (data) {
  if (!data.token) {
    console.error('❌ No token available, skipping tests');
    return;
  }

  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  // ==================== SOC ENDPOINTS ====================
  group('🔒 SOC Endpoints', () => {
    // High priority SOC dashboard
    let res = http.get(`${baseURL}/api/soc/dashboard/`, { headers, tags: { name: 'SOC_Dashboard' } });
    validateResponse(res, 'SOC Dashboard', 200);
    socEndpoints.add(1);
    checkCachePerformance(res, 300);

    // Incidents list
    res = http.get(`${baseURL}/api/soc/incidents/`, { headers, tags: { name: 'SOC_Incidents' } });
    validateResponse(res, 'SOC Incidents', 200);
    socEndpoints.add(1);

    // Threat map
    res = http.get(`${baseURL}/api/soc/threat-map/`, { headers, tags: { name: 'SOC_ThreatMap' } });
    validateResponse(res, 'SOC Threat Map', 200, 400);
    socEndpoints.add(1);

    // System health
    res = http.get(`${baseURL}/api/soc/system-health/`, { headers, tags: { name: 'SOC_SystemHealth' } });
    validateResponse(res, 'SOC System Health', 200);
    socEndpoints.add(1);
    checkCachePerformance(res, 200);

    // Top threats
    res = http.get(`${baseURL}/api/soc/top-threats/`, { headers, tags: { name: 'SOC_TopThreats' } });
    validateResponse(res, 'SOC Top Threats', 200);
    socEndpoints.add(1);

    // MITRE tactics
    res = http.get(`${baseURL}/api/soc/mitre-tactics/`, { headers, tags: { name: 'SOC_MITRE' } });
    validateResponse(res, 'SOC MITRE Tactics', 200);
    socEndpoints.add(1);

    // Threat intelligence
    res = http.get(`${baseURL}/api/soc/threat-intelligence/`, { headers, tags: { name: 'SOC_ThreatIntel' } });
    validateResponse(res, 'SOC Threat Intelligence', 200);
    socEndpoints.add(1);

    // IOC alerts
    res = http.get(`${baseURL}/api/soc/live-ioc-alerts/`, { headers, tags: { name: 'SOC_IOC' } });
    validateResponse(res, 'SOC IOC Alerts', 200);
    socEndpoints.add(1);
  });

  // ==================== THREAT INTELLIGENCE ====================
  group('🎯 Threat Intelligence', () => {
    // Indicators
    let res = http.get(`${baseURL}/api/indicators/`, { headers, tags: { name: 'Threat_Indicators' } });
    validateResponse(res, 'Indicators List', 200);
    threatEndpoints.add(1);
    checkCachePerformance(res, 250);

    // Threat feeds
    res = http.get(`${baseURL}/api/threat-feeds/`, { headers, tags: { name: 'Threat_Feeds' } });
    validateResponse(res, 'Threat Feeds', 200);
    threatEndpoints.add(1);
    checkCachePerformance(res, 200);

    // TTPs
    res = http.get(`${baseURL}/api/ttps/`, { headers, tags: { name: 'Threat_TTPs' } });
    validateResponse(res, 'TTPs List', 200);
    threatEndpoints.add(1);

    // MITRE matrix
    res = http.get(`${baseURL}/api/ttps/mitre-matrix/`, { headers, tags: { name: 'Threat_MITRE' } });
    validateResponse(res, 'MITRE Matrix', 200);
    threatEndpoints.add(1);

    // TTP trends
    res = http.get(`${baseURL}/api/ttps/trends/`, { headers, tags: { name: 'Threat_Trends' } });
    validateResponse(res, 'TTP Trends', 200);
    threatEndpoints.add(1);

    // Recent activities
    res = http.get(`${baseURL}/api/recent-activities/`, { headers, tags: { name: 'Threat_Activities' } });
    validateResponse(res, 'Recent Activities', 200);
    threatEndpoints.add(1);
    checkCachePerformance(res, 200);

    // Threat activity chart
    res = http.get(`${baseURL}/api/threat-activity-chart/`, { headers, tags: { name: 'Threat_Chart' } });
    validateResponse(res, 'Activity Chart', 200);
    threatEndpoints.add(1);

    // System health
    res = http.get(`${baseURL}/api/system-health/`, { headers, tags: { name: 'System_Health' } });
    validateResponse(res, 'System Health', 200);
    threatEndpoints.add(1);

    // Dashboard stats
    res = http.get(`${baseURL}/api/dashboard-stats/`, { headers, tags: { name: 'Dashboard_Stats' } });
    validateResponse(res, 'Dashboard Stats', 200);
    threatEndpoints.add(1);

    // Technique frequencies
    res = http.get(`${baseURL}/api/ttps/technique-frequencies/`, { headers, tags: { name: 'TTP_TechFreq' } });
    validateResponse(res, 'Technique Frequencies', 200);
    threatEndpoints.add(1);

    // Tactic frequencies
    res = http.get(`${baseURL}/api/ttps/tactic-frequencies/`, { headers, tags: { name: 'TTP_TacticFreq' } });
    validateResponse(res, 'Tactic Frequencies', 200);
    threatEndpoints.add(1);

    // Shared indicators
    res = http.get(`${baseURL}/api/shared-indicators/`, { headers, tags: { name: 'Shared_Indicators' } });
    validateResponse(res, 'Shared Indicators', 200);
    threatEndpoints.add(1);
  });

  // ==================== USER MANAGEMENT ====================
  group('👥 User Management', () => {
    // Users list
    let res = http.get(`${baseURL}/api/users/`, { headers, tags: { name: 'Users_List' } });
    validateResponse(res, 'Users List', 200);
    checkCachePerformance(res, 200);

    // Auth profile
    res = http.get(`${baseURL}/api/auth/profile/`, { headers, tags: { name: 'Auth_Profile' } });
    validateResponse(res, 'User Profile', 200);
    checkCachePerformance(res, 200);

    // User invitations
    res = http.get(`${baseURL}/api/users/invitations/`, { headers, tags: { name: 'User_Invitations' } });
    validateResponse(res, 'User Invitations', 200);
  });

  // ==================== ORGANIZATIONS ====================
  group('🏢 Organizations', () => {
    // Organizations list
    let res = http.get(`${baseURL}/api/organizations/`, { headers, tags: { name: 'Org_List' } });
    validateResponse(res, 'Organizations List', 200);

    // Organization types
    res = http.get(`${baseURL}/api/organizations/types/`, { headers, tags: { name: 'Org_Types' } });
    validateResponse(res, 'Organization Types', 200);

    // Connected organizations
    res = http.get(`${baseURL}/api/organizations/connected/`, { headers, tags: { name: 'Org_Connected' } });
    validateResponse(res, 'Connected Orgs', 200);
  });

  // ==================== TRUST MANAGEMENT ====================
  group('🤝 Trust Management', () => {
    // Trust dashboard
    let res = http.get(`${baseURL}/api/trust/dashboard/`, { headers, tags: { name: 'Trust_Dashboard' } });
    validateResponse(res, 'Trust Dashboard', 200);

    // Trust levels
    res = http.get(`${baseURL}/api/trust/levels/`, { headers, tags: { name: 'Trust_Levels' } });
    validateResponse(res, 'Trust Levels', 200);

    // Bilateral trust
    res = http.get(`${baseURL}/api/trust/bilateral/`, { headers, tags: { name: 'Trust_Bilateral' } });
    validateResponse(res, 'Bilateral Trust', 200);

    // Community trust
    res = http.get(`${baseURL}/api/trust/community/`, { headers, tags: { name: 'Trust_Community' } });
    validateResponse(res, 'Community Trust', 200);
  });

  // ==================== ASSETS ====================
  group('💻 Asset Management', () => {
    // Asset inventory
    let res = http.get(`${baseURL}/api/assets/inventory/`, { headers, tags: { name: 'Asset_Inventory' } });
    validateResponse(res, 'Asset Inventory', 200);

    // Asset alerts
    res = http.get(`${baseURL}/api/assets/alerts/`, { headers, tags: { name: 'Asset_Alerts' } });
    validateResponse(res, 'Asset Alerts', 200);

    // Asset statistics
    res = http.get(`${baseURL}/api/assets/statistics/`, { headers, tags: { name: 'Asset_Stats' } });
    validateResponse(res, 'Asset Statistics', 200);

    // Asset alert feed
    res = http.get(`${baseURL}/api/assets/alerts/feed/`, { headers, tags: { name: 'Asset_Feed' } });
    validateResponse(res, 'Asset Alert Feed', 200);
  });

  // ==================== BEHAVIOR ANALYTICS ====================
  group('📊 Behavior Analytics', () => {
    // Behavior dashboard
    let res = http.get(`${baseURL}/api/behavior-analytics/dashboard/`, { headers, tags: { name: 'Behavior_Dashboard' } });
    validateResponse(res, 'Behavior Dashboard', 200);

    // Anomalies
    res = http.get(`${baseURL}/api/behavior-analytics/anomalies/`, { headers, tags: { name: 'Behavior_Anomalies' } });
    validateResponse(res, 'Behavior Anomalies', 200);

    // Behavior alerts
    res = http.get(`${baseURL}/api/behavior-analytics/alerts/`, { headers, tags: { name: 'Behavior_Alerts' } });
    validateResponse(res, 'Behavior Alerts', 200);

    // Behavior logs
    res = http.get(`${baseURL}/api/behavior-analytics/logs/`, { headers, tags: { name: 'Behavior_Logs' } });
    validateResponse(res, 'Behavior Logs', 200);
  });

  // ==================== REPORTS & SYNC ====================
  group('📄 Reports & Sync', () => {
    // Reports list
    let res = http.get(`${baseURL}/api/reports/`, { headers, tags: { name: 'Reports_List' } });
    validateResponse(res, 'Reports List', 200);

    // Reports status
    res = http.get(`${baseURL}/api/reports/status/`, { headers, tags: { name: 'Reports_Status' } });
    validateResponse(res, 'Reports Status', 200);

    // Sync check updates
    res = http.get(`${baseURL}/api/sync/check-updates/`, { headers, tags: { name: 'Sync_Updates' } });
    validateResponse(res, 'Sync Check Updates', 200);

    // Sync last seen
    res = http.get(`${baseURL}/api/sync/last-seen/`, { headers, tags: { name: 'Sync_LastSeen' } });
    validateResponse(res, 'Sync Last Seen', 200);

    // API status
    res = http.get(`${baseURL}/api/`, { headers, tags: { name: 'API_Status' } });
    validateResponse(res, 'API Status', 200);
  });

  sleep(1); // Think time between iterations
}

// ==================== HELPER FUNCTIONS ====================
function validateResponse(response, name, expectedStatus = 200, maxDuration = 1000) {
  const checks = check(response, {
    [`${name}: status ${expectedStatus}`]: (r) => r.status === expectedStatus,
    [`${name}: response time OK`]: (r) => r.timings.duration < maxDuration,
  });

  if (checks) {
    successRate.add(1);
  } else {
    errorRate.add(1);
    console.error(`❌ ${name} failed: status=${response.status}, duration=${response.timings.duration}ms`);
  }

  // Track fast responses
  if (response.timings.duration < 200) {
    fastResponses.add(1);
  } else {
    fastResponses.add(0);
  }
}

function checkCachePerformance(response, cacheThreshold = 200) {
  // If response is very fast, likely cached
  if (response.timings.duration < cacheThreshold) {
    cacheHitEstimate.add(1);
  } else {
    cacheHitEstimate.add(0);
  }
}

// ==================== TEARDOWN & REPORTS ====================
export function teardown(data) {
  console.log('🏁 Test completed, generating reports...');
}

export function handleSummary(data) {
  return {
    'scripts/testing/k6-results.html': htmlReport(data),
    'scripts/testing/k6-summary.json': JSON.stringify(data),
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
  };
}
