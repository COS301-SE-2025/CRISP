/**
 * Global Refresh Manager - Coordinates all refresh operations across the app
 * Prevents excessive server calls while ensuring real-time updates
 */

class RefreshManager {
  constructor() {
    this.subscribers = new Map();
    this.isActive = true;
    this.lastActivity = Date.now();
    this.globalInterval = null;
    this.refreshQueue = new Set();
    this.isProcessing = false;

    // Track user activity to pause refreshing when inactive
    this.setupActivityTracking();

    // Start smart background refresh (300s instead of multiple 5-30s timers)
    this.startGlobalRefresh();
  }

  setupActivityTracking() {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];

    const updateActivity = () => {
      this.lastActivity = Date.now();
      this.isActive = true;
    };

    events.forEach(event => {
      document.addEventListener(event, updateActivity, true);
    });

    // Check if user is inactive (5 minutes of no activity)
    setInterval(() => {
      const inactiveTime = Date.now() - this.lastActivity;
      this.isActive = inactiveTime < 300000; // 5 minutes
    }, 60000); // Check less frequently
  }

  startGlobalRefresh() {
    // PERFORMANCE RESTORED: Global refresh enabled with 10-minute interval
    this.globalInterval = setInterval(() => {
      if (this.isActive && !this.isProcessing && this.subscribers.size > 0) {
        this.processBackgroundRefresh();
      }
    }, 600000); // 10 minutes - much less frequent than before
  }

  async processBackgroundRefresh() {
    if (this.isProcessing) return;

    this.isProcessing = true;
    try {
      // Check for backend refresh triggers first
      await this.checkRefreshTriggers();

      // Only refresh components that are visible and need background updates
      for (const [key, subscriber] of this.subscribers) {
        if (subscriber.backgroundRefresh && subscriber.isVisible && subscriber.isVisible()) {
          await this.safeRefresh(subscriber);
          await this.delay(100); // Small delay between refreshes
        }
      }
    } finally {
      this.isProcessing = false;
    }
  }

  async checkRefreshTriggers() {
    try {
      // Skip backend polling if user is inactive to reduce server load
      if (!this.isActive) {
        return;
      }

      // Import the API function dynamically to avoid circular dependencies
      const response = await fetch('http://localhost:8000/api/threat-feeds/check_refresh_triggers/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('crisp_auth_token')}`,
        },
        // Add timeout to prevent hanging requests
        signal: AbortSignal.timeout(5000)
      });

      if (!response.ok) return;

      const data = await response.json();
      if (data.success && data.triggers && data.triggers.length > 0) {

        // Process each trigger
        for (const trigger of data.triggers) {
          if (trigger.components && trigger.components.length > 0) {
            await this.triggerRefresh(trigger.components, `backend_trigger:${trigger.type}`);
          }
        }
      }
    } catch (error) {
      // Silently fail to avoid spam in logs
      console.debug('RefreshManager: Error checking triggers:', error);
    }
  }

  subscribe(key, refreshFunction, options = {}) {
    this.subscribers.set(key, {
      refresh: refreshFunction,
      backgroundRefresh: options.backgroundRefresh !== false, // default true
      isVisible: options.isVisible || (() => true),
      lastRefresh: 0,
      ...options
    });

    // Reduce console spam for better performance
    // console.debug(`RefreshManager: Subscribed ${key}`);
  }

  unsubscribe(key) {
    this.subscribers.delete(key);
    // console.debug(`RefreshManager: Unsubscribed ${key}`);
  }

  // Immediate refresh triggered by user actions
  async triggerRefresh(keys, reason = 'user_action') {
    if (!Array.isArray(keys)) keys = [keys];

    // console.debug(`🔄 RefreshManager: Triggering refresh for [${keys.join(', ')}] - ${reason}`);

    for (const key of keys) {
      const subscriber = this.subscribers.get(key);
      if (subscriber) {
        // console.debug(`✅ RefreshManager: Refreshing '${key}'`);
        await this.safeRefresh(subscriber);
        subscriber.lastRefresh = Date.now();
      } else {
        // No subscriber found for key
      }
    }
  }

  // Refresh related components after data changes
  async triggerRelated(triggerKey, reason = 'data_change') {
    const relatedKeys = this.getRelatedComponents(triggerKey);
    if (relatedKeys.length > 0) {
      await this.triggerRefresh(relatedKeys, reason);
    } else {
      // No related components found
    }
  }

  getRelatedComponents(triggerKey) {
    // Define component relationships
    const relationships = {
      'threat-feeds': ['indicators', 'dashboard', 'notifications', 'assets'],
      'indicators': ['dashboard', 'threat-analysis', 'assets'],
      'organizations': ['users', 'trust-management', 'notifications'],
      'users': ['notifications', 'trust-management', 'organizations'],
      'assets': ['alerts', 'dashboard', 'notifications', 'threat-feeds'],
      'alerts': ['dashboard', 'notifications', 'assets']
    };

    return relationships[triggerKey] || [];
  }

  async safeRefresh(subscriber) {
    try {
      await subscriber.refresh();
    } catch (error) {
      // Silently handle refresh error
    }
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Batch multiple refresh requests to prevent spam
  queueRefresh(key, delay = 500) {
    this.refreshQueue.add(key);

    setTimeout(() => {
      if (this.refreshQueue.has(key)) {
        this.refreshQueue.delete(key);
        this.triggerRefresh([key], 'queued');
      }
    }, delay);
  }

  // Manual refresh all visible components
  async refreshAll() {
    const visibleKeys = Array.from(this.subscribers.entries())
      .filter(([key, subscriber]) => subscriber.isVisible())
      .map(([key]) => key);

    await this.triggerRefresh(visibleKeys, 'manual_all');
  }

  destroy() {
    if (this.globalInterval) {
      clearInterval(this.globalInterval);
    }
    this.subscribers.clear();
  }
}

// Global singleton instance
const refreshManager = new RefreshManager();

// React hook for easy component integration
// Note: This hook should be imported and used directly in React components
// Import React hooks directly in the component file instead of using this

export default refreshManager;