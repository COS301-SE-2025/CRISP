import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CountUp from 'react-countup';
import blueVLogo from '/src/assets/BlueV.png';

const dashboardStats = [
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    number: 247,
    suffix: '',
    label: 'Active Threats',
    className: 'threat-icon',
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    ),
    number: 45,
    suffix: '',
    label: 'Institutions',
    className: 'institution-icon',
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12s-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.368a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
      </svg>
    ),
    number: 1.2,
    suffix: 'K',
    label: 'Shared IoCs',
    className: 'sharing-icon',
  },
];

function Hero() {
  const navigate = useNavigate();
  const [startAnimation, setStartAnimation] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setStartAnimation(true);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  const handleLogin = () => {
    navigate('/login');
  };

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
            <button onClick={handleLogin} className="btn btn-primary btn-large">
              <i className="fas fa-sign-in-alt"></i>
              Login to Dashboard
            </button>
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
                <img src={blueVLogo} alt="BlueV Logo" style={{ height: '24px', width: 'auto' }} />
                <span>CRISP Dashboard</span>
              </div>
              <div className="dashboard-status">
                <span className="status-dot"></span>
                <span>System Online</span>
              </div>
            </div>
            <div className="dashboard-stats">
              {dashboardStats.map((stat, index) => (
                <div key={index} className="stat-card">
                  <div className={`stat-icon ${stat.className}`}>
                    {stat.icon}
                  </div>
                  <div className="stat-info">
                    <div className="stat-number">
                      {startAnimation ? (
                        <CountUp
                          end={stat.number}
                          duration={2.5}
                          decimals={stat.suffix === 'K' ? 1 : 0}
                          suffix={stat.suffix}
                        />
                      ) : (
                        '0'
                      )}
                    </div>
                    <div className="stat-label">{stat.label}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;