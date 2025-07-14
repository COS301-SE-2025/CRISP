import React from 'react';

function Features() {
  const features = [
    {
      icon: "fas fa-shield-alt",
      title: "STIX/TAXII Compliance",
      description: "Full compatibility with industry-standard threat intelligence formats and sharing protocols."
    },
    {
      icon: "fas fa-user-secret",
      title: "Advanced Anonymization",
      description: "Protect sensitive institutional data while preserving analytical value of threat intelligence."
    },
    {
      icon: "fas fa-network-wired",
      title: "Real-time Threat Feeds",
      description: "Automated consumption and distribution of threat intelligence from multiple sources."
    },
    {
      icon: "fas fa-bell",
      title: "Intelligent Alerting",
      description: "Customizable alerts for high-priority threats targeting educational institutions."
    },
    {
      icon: "fas fa-handshake",
      title: "Trust-based Sharing",
      description: "Configurable trust relationships control data sharing levels between institutions."
    },
    {
      icon: "fas fa-chart-line",
      title: "Analytics & Reports",
      description: "Comprehensive threat landscape analysis and trend reporting for informed decision-making."
    }
  ];

  return (
    <section id="features" className="features">
      <div className="container">
        <div className="section-header">
          <h2>Powerful Features for Cyber Defense</h2>
          <p>CRISP provides comprehensive threat intelligence sharing capabilities designed specifically for educational institutions</p>
        </div>
        
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">
                <i className={feature.icon}></i>
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Features;