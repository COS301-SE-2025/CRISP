import React, { useState } from 'react';

function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="header">
      <div className="container header-container">
        <a href="#" className="logo">
          <div className="logo-icon"><i className="fas fa-shield-alt"></i></div>
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
          <a href="#demo" className="btn btn-outline">Request Demo</a>
          <a href="#contact" className="btn btn-primary">Get Started</a>
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