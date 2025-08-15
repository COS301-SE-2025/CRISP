import React from 'react';

function Footer() {
  return (
    <footer id="contact" className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-main">
            <div className="footer-logo">
              <i className="fas fa-shield-alt logo-icon"></i>
              <span>CRISP</span>
            </div>
            <p className="footer-description">
              Empowering educational institutions with secure, collaborative threat intelligence 
              sharing to build stronger cybersecurity defenses together.
            </p>
            <div className="footer-social">
              <a href="#" aria-label="Twitter">
                <i className="fab fa-twitter"></i>
              </a>
              <a href="#" aria-label="LinkedIn">
                <i className="fab fa-linkedin"></i>
              </a>
              <a href="#" aria-label="GitHub">
                <i className="fab fa-github"></i>
              </a>
            </div>
          </div>
          
          <div className="footer-section">
            <h4>Product</h4>
            <ul>
              <li><a href="#features">Features</a></li>
              <li><a href="#pricing">Pricing</a></li>
              <li><a href="#security">Security</a></li>
              <li><a href="#integrations">Integrations</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Resources</h4>
            <ul>
              <li><a href="#documentation">Documentation</a></li>
              <li><a href="#api">API Reference</a></li>
              <li><a href="#guides">User Guides</a></li>
              <li><a href="#support">Support Center</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Company</h4>
            <ul>
              <li><a href="#about">About Us</a></li>
              <li><a href="#careers">Careers</a></li>
              <li><a href="#blog">Blog</a></li>
              <li><a href="#contact">Contact</a></li>
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <div className="footer-legal">
            <p>&copy; 2024 CRISP. All rights reserved.</p>
            <div className="footer-links">
              <a href="#privacy">Privacy Policy</a>
              <a href="#terms">Terms of Service</a>
              <a href="#cookies">Cookie Policy</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;