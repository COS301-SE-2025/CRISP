import React from 'react';

function Features() {
  return (
    <section id="features" className="features">
      <div className="container">
        <div className="section-header">
          <h2>Powerful Features for Educational Cybersecurity</h2>
          <p>Discover how CRISP transforms threat intelligence sharing across educational institutions</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-shield-alt"></i>
            </div>
            <h3 className="feature-title">Secure Intelligence Sharing</h3>
            <p className="feature-description">
              Share threat intelligence securely between institutions while maintaining complete data anonymization and privacy protection.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-users"></i>
            </div>
            <h3 className="feature-title">Trust Management</h3>
            <p className="feature-description">
              Build and manage trust relationships between educational institutions with granular access controls and verification systems.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <h3 className="feature-title">Advanced Analytics</h3>
            <p className="feature-description">
              Gain insights from shared threat data with powerful analytics tools and real-time monitoring capabilities.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-bell"></i>
            </div>
            <h3 className="feature-title">Real-time Alerts</h3>
            <p className="feature-description">
              Receive instant notifications about emerging threats relevant to your institution's security posture.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-cog"></i>
            </div>
            <h3 className="feature-title">Automated Processing</h3>
            <p className="feature-description">
              Streamline threat intelligence workflows with automated data processing and standardized formats.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <i className="fas fa-lock"></i>
            </div>
            <h3 className="feature-title">Privacy First</h3>
            <p className="feature-description">
              Built with privacy-by-design principles to protect sensitive educational data while enabling effective collaboration.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Features;