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

    // Start smart background refresh (60s instead of multiple 5-30s timers)
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
    }, 30000);
  }

  startGlobalRefresh() {
    // Single 60-second timer replaces all the 5-30 second timers
    this.globalInterval = setInterval(() => {
      if (this.isActive && !this.isProcessing && this.subscribers.size > 0) {
        this.processBackgroundRefresh();
      }
    }, 60000); // 60 seconds - much more reasonable than current 5-30s intervals
  }

  async processBackgroundRefresh() {
    if (this.isProcessing) return;

    this.isProcessing = true;
    try {
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

  subscribe(key, refreshFunction, options = {}) {
    this.subscribers.set(key, {
      refresh: refreshFunction,
      backgroundRefresh: options.backgroundRefresh !== false, // default true
      isVisible: options.isVisible || (() => true),
      lastRefresh: 0,
      ...options
    });

    console.log(`RefreshManager: Subscribed ${key}`);
  }

  unsubscribe(key) {
    this.subscribers.delete(key);
    console.log(`RefreshManager: Unsubscribed ${key}`);
  }

  // Immediate refresh triggered by user actions
  async triggerRefresh(keys, reason = 'user_action') {
    if (!Array.isArray(keys)) keys = [keys];

    console.log(`🔄 RefreshManager: Triggering refresh for [${keys.join(', ')}] - ${reason}`);

    for (const key of keys) {
      const subscriber = this.subscribers.get(key);
      if (subscriber) {
        console.log(`✅ RefreshManager: Refreshing '${key}'`);
        await this.safeRefresh(subscriber);
        subscriber.lastRefresh = Date.now();
      } else {
        console.warn(`⚠️ RefreshManager: No subscriber found for '${key}' (available: [${Array.from(this.subscribers.keys()).join(', ')}])`);
      }
    }
  }

  // Refresh related components after data changes
  async triggerRelated(triggerKey, reason = 'data_change') {
    const relatedKeys = this.getRelatedComponents(triggerKey);
    console.log(`🔄 RefreshManager: triggerRelated('${triggerKey}') -> [${relatedKeys.join(', ')}]`);
    if (relatedKeys.length > 0) {
      await this.triggerRefresh(relatedKeys, reason);
    } else {
      console.warn(`⚠️ RefreshManager: No related components found for '${triggerKey}'`);
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
      console.warn('RefreshManager: Error during refresh:', error);
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
    console.log('RefreshManager: Manual refresh all');
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
export const useRefresh = (key, refreshFunction, options = {}) => {
  const { useEffect, useCallback, useRef } = window.React || require('react');

  const optionsRef = useRef(options);
  optionsRef.current = options;

  const stableRefreshFunction = useCallback(refreshFunction, []);

  useEffect(() => {
    refreshManager.subscribe(key, stableRefreshFunction, optionsRef.current);

    return () => {
      refreshManager.unsubscribe(key);
    };
  }, [key, stableRefreshFunction]);

  return {
    refreshNow: () => refreshManager.triggerRefresh([key], 'manual'),
    refreshRelated: () => refreshManager.triggerRelated(key),
    queueRefresh: (delay) => refreshManager.queueRefresh(key, delay)
  };
};

export default refreshManager;