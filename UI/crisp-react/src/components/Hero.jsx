import React from 'react';

function Hero() {
  return (
    <section className="hero">
      <div className="container hero-container">
        <div className="hero-content">
          <h1 className="hero-title">
            Secure <span className="highlight">Cyber Threat Intelligence</span> Sharing for Educational Institutions
          </h1>
          <p className="hero-description">
            CRISP enables educational institutions to share anonymized threat intelligence, 
            protecting student data while strengthening cybersecurity defenses across the education sector.
          </p>
          <div className="hero-actions">
            <a href="#demo" className="btn btn-primary btn-large">
              <i className="fas fa-play"></i>
              Watch Demo
            </a>
            <a href="#features" className="btn btn-outline btn-large">
              <i className="fas fa-info-circle"></i>
              Learn More
            </a>
          </div>
        </div>
        
        <div className="hero-visual">
          <div className="dashboard-preview">
            <div className="dashboard-header">
              <div className="dashboard-logo">
                <i className="fas fa-shield-alt"></i>
                <span>CRISP Dashboard</span>
              </div>
              <div className="dashboard-status">
                <span className="status-dot"></span>
                <span>System Online</span>
              </div>
            </div>
            <div className="dashboard-stats">
              <div className="stat-card">
                <div className="stat-icon threat-icon">
                  <i className="fas fa-exclamation-triangle"></i>
                </div>
                <div className="stat-info">
                  <div className="stat-number">247</div>
                  <div className="stat-label">Active Threats</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon institution-icon">
                  <i className="fas fa-building"></i>
                </div>
                <div className="stat-info">
                  <div className="stat-number">45</div>
                  <div className="stat-label">Institutions</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon sharing-icon">
                  <i className="fas fa-share-alt"></i>
                </div>
                <div className="stat-info">
                  <div className="stat-number">1.2K</div>
                  <div className="stat-label">Shared IoCs</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;