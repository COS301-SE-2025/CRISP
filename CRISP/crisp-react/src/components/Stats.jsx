import React from 'react';

function Stats() {
  return (
    <section className="stats">
      <div className="container">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-icon">
              <i className="fas fa-university"></i>
            </div>
            <div className="stat-number">150+</div>
            <div className="stat-label">Educational Institutions</div>
          </div>
          <div className="stat-item">
            <div className="stat-icon">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="stat-number">10K+</div>
            <div className="stat-label">Threats Detected</div>
          </div>
          <div className="stat-item">
            <div className="stat-icon">
              <i className="fas fa-share-alt"></i>
            </div>
            <div className="stat-number">50K+</div>
            <div className="stat-label">Indicators Shared</div>
          </div>
          <div className="stat-item">
            <div className="stat-icon">
              <i className="fas fa-clock"></i>
            </div>
            <div className="stat-number">99.9%</div>
            <div className="stat-label">Uptime Reliability</div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Stats;