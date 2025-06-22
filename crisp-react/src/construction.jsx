import React, { useState, useEffect } from 'react';
import './assets/construction.css';
import BlueVLogo from './assets/BlueV.png';
import CrispHelp from './crisp_help.jsx';

function Construction() {
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  });

  // Initialize Feather icons when component mounts
  useEffect(() => {
    if (!window.feather) {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.29.0/feather.min.js';
      script.onload = () => {
        if (window.feather) {
          window.feather.replace();
        }
      };
      document.head.appendChild(script);
    } else {
      window.feather.replace();
    }
  }, []);

  // Re-run feather.replace() when help modal state changes
  useEffect(() => {
    if (window.feather) {
      setTimeout(() => window.feather.replace(), 100);
    }
  }, [isHelpOpen]);

  // Countdown timer effect
  useEffect(() => {
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + 30); // 30 days from now

    const timer = setInterval(() => {
      const now = new Date().getTime();
      const distance = targetDate.getTime() - now;

      if (distance > 0) {
        setTimeLeft({
          days: Math.floor(distance / (1000 * 60 * 60 * 24)),
          hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((distance % (1000 * 60)) / 1000)
        });
      }
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const openHelp = () => {
    setIsHelpOpen(true);
  };

  const closeHelp = () => {
    setIsHelpOpen(false);
  };

  const handleNavigate = (page, tutorialId) => {
    // Handle navigation from help tutorials
    console.log(`Navigate to ${page} with context:`, tutorialId);
    
    // Since we're already on the construction page, we could:
    // 1. Scroll to specific sections
    // 2. Highlight specific features
    // 3. Show additional content based on tutorial context
    
    if (tutorialId) {
      // Example: Scroll to features section when tutorials are clicked
      const featuresSection = document.querySelector('.features-preview');
      if (featuresSection) {
        featuresSection.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <>
      <div className="construction-page">
        <div className="construction-content">
          {/* Header */}
          <header className="construction-header">
            <div className="logo-container">
              <img src={BlueVLogo} alt="BlueV Logo" className="brand-logo" />
            </div>
            <button 
              className="help-button" 
              onClick={openHelp}
              title="Help & Tutorials"
            >
              <i data-feather="help-circle"></i>
            </button>
          </header>

          {/* Main Content */}
          <main className="construction-main">
            <div className="construction-icon">
              <i data-feather="settings"></i>
            </div>
            
            <h1>We're Building Something Amazing</h1>
            <p className="subtitle">
              CRISP (Cyber Risk Information Sharing Platform) is currently under development. 
              We're working hard to bring you the most advanced threat intelligence platform.
            </p>

            {/* Countdown Timer */}
            <div className="countdown-container">
              <h3>Estimated Launch</h3>
              <div className="countdown">
                <div className="time-unit">
                  <span className="number">{timeLeft.days}</span>
                  <span className="label">Days</span>
                </div>
                <div className="time-unit">
                  <span className="number">{timeLeft.hours}</span>
                  <span className="label">Hours</span>
                </div>
                <div className="time-unit">
                  <span className="number">{timeLeft.minutes}</span>
                  <span className="label">Minutes</span>
                </div>
                <div className="time-unit">
                  <span className="number">{timeLeft.seconds}</span>
                  <span className="label">Seconds</span>
                </div>
              </div>
            </div>

            {/* Features Preview */}
            <div className="features-preview">
              <h3>What's Coming</h3>
              <div className="features-grid">
                <div className="feature-card">
                  <div className="feature-icon">
                    <i data-feather="shield"></i>
                  </div>
                  <h4>Threat Intelligence Hub</h4>
                  <p>Centralized platform for collecting, analyzing, and sharing threat intelligence across institutions.</p>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">
                    <i data-feather="rss"></i>
                  </div>
                  <h4>Real-time Threat Feeds</h4>
                  <p>Integration with STIX/TAXII, MISP, and custom threat intelligence sources for real-time updates.</p>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">
                    <i data-feather="search"></i>
                  </div>
                  <h4>IoC Management</h4>
                  <p>Advanced tools for managing indicators of compromise with automated validation and enrichment.</p>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">
                    <i data-feather="trending-up"></i>
                  </div>
                  <h4>TTP Analysis</h4>
                  <p>MITRE ATT&CK framework integration for comprehensive tactics, techniques, and procedures analysis.</p>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">
                    <i data-feather="users"></i>
                  </div>
                  <h4>Collaborative Sharing</h4>
                  <p>Secure, trust-based sharing network enabling institutions to collaborate on threat intelligence.</p>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">
                    <i data-feather="bar-chart"></i>
                  </div>
                  <h4>Advanced Analytics</h4>
                  <p>Machine learning-powered analytics for pattern recognition and threat prediction.</p>
                </div>
              </div>
            </div>

            {/* Call to Action */}
            <div className="cta-section">
              <h3>Get Ready for Launch</h3>
              <p>Learn about CRISP's features and capabilities while we finish development.</p>
              <div className="cta-buttons">
                <button className="btn btn-primary" onClick={openHelp}>
                  <i data-feather="book-open"></i>
                  View Tutorials
                </button>
                <button className="btn btn-outline" onClick={() => window.location.href = 'mailto:info@bluevision-itm.com'}>
                  <i data-feather="mail"></i>
                  Get Notified
                </button>
              </div>
            </div>

            {/* Progress Indicator */}
            <div className="progress-section">
              <h4>Development Progress</h4>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: '75%' }}></div>
              </div>
              <div className="progress-labels">
                <span>Planning</span>
                <span>Development</span>
                <span>Testing</span>
                <span>Launch</span>
              </div>
            </div>
          </main>

          {/* Footer */}
          <footer className="construction-footer">
            <div className="footer-content">
              <div className="footer-section">
                <h4>BlueVision ITM</h4>
                <p>Leading cybersecurity solutions and threat intelligence management.</p>
              </div>
              <div className="footer-section">
                <h4>Quick Links</h4>
                <ul>
                  <li><button onClick={openHelp}><i data-feather="help-circle"></i> Help & Tutorials</button></li>
                  <li><a href="mailto:info@bluevision-itm.com"><i data-feather="mail"></i> Contact Us</a></li>
                  <li><a href="#"><i data-feather="globe"></i> Website</a></li>
                </ul>
              </div>
              <div className="footer-section">
                <h4>Stay Updated</h4>
                <p>Follow our progress and get notified when CRISP launches.</p>
                <div className="social-links">
                  <a href="#" title="LinkedIn"><i data-feather="linkedin"></i></a>
                  <a href="#" title="Twitter"><i data-feather="twitter"></i></a>
                  <a href="#" title="GitHub"><i data-feather="github"></i></a>
                </div>
              </div>
            </div>
            <div className="footer-bottom">
              <p>&copy; 2025 BlueVision ITM. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </div>

      {/* Help Modal */}
      <CrispHelp 
        isOpen={isHelpOpen} 
        onClose={closeHelp} 
        onNavigate={handleNavigate}
      />
    </>
  );
}

export default Construction;