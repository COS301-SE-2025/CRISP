import React, { useEffect } from 'react';
import './assets/construction.css';
import BlueVLogo from './assets/BlueV.png';

function Construction({ onBackToLogin }) {
  
  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  
  return (
    <div className="construction-page">
      <div className="construction-container">
        
        {/* Header with logo and login link */}
        <header className="construction-header">
          <div className="logo-section">
            <div className="crisp-logo">
              <img src={BlueVLogo} alt="CRISP Logo" className="logo-image" />
              <span className="logo-subtitle">Cyber Risk Information Sharing Platform</span>
            </div>
          </div>
          <button 
            className="login-link" 
            onClick={() => {
              if (typeof onBackToLogin === 'function') {
                onBackToLogin();
              } else {
                window.location.href = '/login';
              }
            }}
            title="Back to Login"
          >
            Login
          </button>
        </header>

        {/* Main content */}
        <main className="construction-main">
          <div className="construction-content">
            <div className="construction-icon">
              🚧
            </div>
            <h1>Under Construction</h1>
            <p>CRISP (Cyber Risk Information Sharing Platform) is currently being developed.</p>
          </div>
        </main>

        {/* Contact section */}
        <footer className="construction-footer">
          <div className="contact-info">
            <h3>Contact Information</h3>
            <div className="contact-details">
              <p>
                <strong>Email:</strong> 
                <a href="mailto:ib@bitm.co.za">ib@bitm.co.za</a>
              </p>
              <p>
                <strong>Company:</strong> BlueVision ITM
              </p>
              <p>
                <strong>Website:</strong> 
                <a href="https://bitm.co.za/" target="_blank" rel="noopener noreferrer">
                  bluevision-itm.com
                </a>
              </p>
            </div>
          </div>
        </footer>

      </div>
    </div>
  );
}

export default Construction;