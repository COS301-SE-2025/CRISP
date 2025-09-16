import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/login');
  };

  const handleRequestDemo = () => {
    // For now, just scroll to features or show a message
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
      featuresSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="header">
      <div className="container header-container">
        <a href="#" className="logo" onClick={(e) => { e.preventDefault(); navigate('/'); }}>
          <i className="fas fa-shield-alt logo-icon"></i>
          <div className="logo-text">CRISP</div>
        </a>
        
        <nav className={`nav ${isMenuOpen ? 'nav-open' : ''}`}>
          <ul className="nav-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#benefits">Benefits</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </nav>

        <div className="header-actions">
          <button onClick={handleRequestDemo} className="btn btn-outline">Request Demo</button>
          <button onClick={handleGetStarted} className="btn btn-primary">Get Started</button>
        </div>

        <button 
          className="mobile-menu-toggle"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <i className="fas fa-bars"></i>
        </button>
      </div>
    </header>
  );
}

export default Header;