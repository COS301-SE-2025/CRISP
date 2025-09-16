import React from 'react';
import { useNavigate } from 'react-router-dom';

function CTA() {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/login');
  };

  return (
    <section className="cta">
      <div className="container">
        <div className="cta-content">
          <h2>Ready to Strengthen Your Institution's Security?</h2>
          <p>
            Join the growing network of educational institutions sharing threat intelligence 
            to protect students, faculty, and institutional data.
          </p>
          <div className="cta-actions">
            <button onClick={handleGetStarted} className="btn btn-primary btn-large">
              <i className="fas fa-rocket"></i>
              Get Started Today
            </button>
            <a href="#contact" className="btn btn-outline btn-large">
              <i className="fas fa-phone"></i>
              Contact Sales
            </a>
          </div>
          <div className="cta-features">
            <div className="cta-feature">
              <i className="fas fa-check"></i>
              <span>Free 30-day trial</span>
            </div>
            <div className="cta-feature">
              <i className="fas fa-check"></i>
              <span>No setup fees</span>
            </div>
            <div className="cta-feature">
              <i className="fas fa-check"></i>
              <span>24/7 support</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default CTA;