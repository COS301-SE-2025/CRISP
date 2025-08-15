import React from 'react';

function Stats() {
  const stats = [
    {
      number: "99.9%",
      label: "System Uptime",
      icon: "fas fa-server"
    },
    {
      number: "500K+",
      label: "Threat Indicators Shared",
      icon: "fas fa-database"
    },
    {
      number: "50+",
      label: "Educational Institutions",
      icon: "fas fa-graduation-cap"
    },
    {
      number: "24/7",
      label: "Real-time Monitoring",
      icon: "fas fa-eye"
    }
  ];

  return (
    <section className="stats">
      <div className="container">
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-item">
              <div className="stat-icon">
                <i className={stat.icon}></i>
              </div>
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Stats;