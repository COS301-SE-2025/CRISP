import React from 'react';
import { useNavigate } from 'react-router-dom';

function CTA() {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/login');
  };

  const handleScheduleDemo = () => {
    navigate('/construction');
  };

  return (
    <section className="cta">
      <div className="container">
        <div className="cta-content">
          <h2>Ready to Strengthen Your Cybersecurity?</h2>
          <p>Join the growing network of educational institutions sharing threat intelligence to protect against cyber attacks.</p>
          <div className="cta-actions">
            <button onClick={handleGetStarted} className="btn btn-primary btn-large">
              <i className="fas fa-rocket"></i>
              Get Started Today
            </button>
            <button onClick={handleScheduleDemo} className="btn btn-outline btn-large">
              <i className="fas fa-calendar"></i>
              Schedule Demo
            </button>
          </div>
        </div>
        <div className="cta-features">
          <div className="cta-feature">
            <i className="fas fa-check-circle"></i>
            <span>Free 30-day trial</span>
          </div>
          <div className="cta-feature">
            <i className="fas fa-check-circle"></i>
            <span>No setup fees</span>
          </div>
          <div className="cta-feature">
            <i className="fas fa-check-circle"></i>
            <span>24/7 support</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default CTA;