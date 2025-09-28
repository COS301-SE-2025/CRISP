import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client'; // Add proper import for createRoot
import feather from 'feather-icons'; // Import feather icons
import './crisp_help.css';
import Construction from './construction.jsx'; // Ensure lowercase to match actual filename
import vid from './assets/TEST.mp4';

function CrispHelp({ isOpen, onClose, onNavigate }) {
  const [activeTab, setActiveTab] = useState('getting-started');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFAQ, setExpandedFAQ] = useState(null);
  const [showVideoModal, setShowVideoModal] = useState(false);

  // Initialize Feather icons when component mounts
  useEffect(() => {
    if (isOpen) {
      // Multiple attempts to ensure icons load
      const timeouts = [10, 50, 100, 200];
      timeouts.forEach(delay => {
        setTimeout(() => {
          try {
            feather.replace();
          } catch (error) {
            console.warn('Feather icons replace failed:', error);
          }
        }, delay);
      });
    }
  }, [isOpen, activeTab, expandedFAQ, searchQuery, showVideoModal]);

  // Handle escape key to close
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        if (showVideoModal) {
          setShowVideoModal(false);
        } else if (isOpen) {
          onClose();
        }
      }
    };
    
    if (isOpen || showVideoModal) {
      document.addEventListener('keydown', handleEscape);
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, showVideoModal, onClose]);

  const handleTutorialClick = (item, e) => {
    e.preventDefault(); // Prevent default link behavior
    
    // Handle video links - show video modal instead of closing help
    if (item.link === 'vid') {
      setShowVideoModal(true);
      return;
    }
    
    // Close the help modal first for other links
    onClose();
    
    // If it's a construction link and we have the navigation callback
    if (item.link === 'Construction' || item.link === 'construction') {
      if (typeof onNavigate === 'function') {
        onNavigate('construction', { tutorial: item.title });
      } else {
        // Fallback direct navigation if onNavigate isn't available
        // Use window location to navigate
        window.location.href = '/construction';
      }
    } else if (item.link) {
      // Handle other types of links (external URLs, etc.)
      if (item.link.startsWith('http')) {
        window.open(item.link, '_blank');
      } else {
        if (typeof onNavigate === 'function') {
          onNavigate(item.link);
        } else {
          window.location.href = `/${item.link}`;
        }
      }
    }
  };

  if (!isOpen) return null;

  const faqData = [
    {
      category: 'General',
      questions: [
        {
          question: 'What is CRISP and how does it work?',
          answer: 'CRISP (Cyber Risk Information Sharing Platform) is a collaborative threat intelligence platform that enables institutions to share, analyze, and act on cybersecurity threats. It aggregates threat data from multiple sources and provides tools for analysis, correlation, and sharing.'
        },
        {
          question: 'How do I get access to CRISP?',
          answer: 'Access to CRISP is provided through institutional partnerships. Contact your IT security team or reach out to BlueVision ITM directly to discuss access for your organization.'
        },
        {
          question: 'Is my data secure on CRISP?',
          answer: 'Yes, CRISP employs enterprise-grade security measures including encryption at rest and in transit, role-based access controls, and regular security audits. All data sharing is controlled and follows strict privacy guidelines.'
        }
      ]
    },
    {
      category: 'Threat Feeds',
      questions: [
        {
          question: 'What types of threat feeds can I connect?',
          answer: 'CRISP supports STIX/TAXII feeds, MISP instances, custom APIs, and manual uploads. Popular sources include CIRCL, AlienVault OTX, and institutional CSIRTs.'
        },
        {
          question: 'How often are feeds updated?',
          answer: 'Feed update frequency varies by source. Most external feeds update every 15-60 minutes, while internal feeds can be configured for real-time updates.'
        },
        {
          question: 'Can I create custom feeds?',
          answer: 'Yes, CRISP allows you to create custom feeds from your internal threat intelligence sources using our API or manual upload features.'
        }
      ]
    },
    {
      category: 'IoC Management',
      questions: [
        {
          question: 'What types of IoCs are supported?',
          answer: 'CRISP supports IP addresses, domains, URLs, file hashes (MD5, SHA1, SHA256), email addresses, and custom indicator types.'
        },
        {
          question: 'How do I validate IoC accuracy?',
          answer: 'CRISP provides automated validation tools and allows manual verification. IoCs are scored based on source reputation, community feedback, and verification status.'
        },
        {
          question: 'Can I export IoCs to my security tools?',
          answer: 'Yes, CRISP supports exports in multiple formats including STIX, JSON, CSV, and direct API integration with popular security platforms.'
        }
      ]
    },
    {
      category: 'Sharing & Collaboration',
      questions: [
        {
          question: 'How does trust-based sharing work?',
          answer: 'CRISP uses a trust-level system where institutions can control what data they share with whom. Trust levels are established through verified partnerships and shared experiences.'
        },
        {
          question: 'Can I control what data I share?',
          answer: 'Absolutely. You have granular control over what threat intelligence you share, with whom, and under what conditions. Default settings ensure nothing is shared without explicit approval.'
        },
        {
          question: 'How do I invite new institutions to the platform?',
          answer: 'Institution invitations are managed through administrator accounts. Contact your platform administrator or BlueVision ITM to add new sharing partners.'
        }
      ]
    }
  ];

  // Simple demo content for all tabs
  const demoContent = {
    title: 'CRISP System Demo',
    icon: 'play-circle',
    content: [
      {
        type: 'demo',
        title: 'Complete CRISP Platform Overview',
        description: 'Watch this comprehensive demo video that covers all CRISP features including threat feeds, IoC management, TTP analysis, trust management, and collaboration tools.',
        duration: '15 min',
        link: 'vid'
      }
    ]
  };

  // Use demo content for all sections when not searching
  const filteredSections = {};
  if (!searchQuery) {
    // Show demo content for all tabs except faqs and contact
    ['getting-started', 'threat-feeds', 'ioc-management', 'ttp-analysis'].forEach(tab => {
      filteredSections[tab] = demoContent;
    });
  }

  const filteredFAQs = faqData.map(category => ({
    ...category,
    questions: category.questions.filter(qa =>
      !searchQuery ||
      qa.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      qa.answer.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(category => category.questions.length > 0);

  return (
    <div className="help-overlay" onClick={onClose}>
      <div className="help-modal" onClick={e => e.stopPropagation()}>
        <div className="help-header">
          <div className="help-title">
            <h2><i data-feather="help-circle"></i> Help Center</h2>
            <p>Find answers, tutorials, and guides for CRISP</p>
          </div>
          <button className="help-close" onClick={onClose}>
            <i data-feather="x">×</i>
          </button>
        </div>

        <div className="help-search">
          <div className="search-container">
            <i data-feather="search"></i>
            <input
              type="text"
              placeholder="Search help articles, FAQs, and tutorials..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="help-content">
          <div className="help-sidebar">
            <nav className="help-nav">
              <button
                className={`nav-item ${activeTab === 'getting-started' ? 'active' : ''}`}
                onClick={() => setActiveTab('getting-started')}
              >
                <i data-feather="play-circle"></i>
                Getting Started
              </button>

              <button
                className={`nav-item ${activeTab === 'faqs' ? 'active' : ''}`}
                onClick={() => setActiveTab('faqs')}
              >
                <i data-feather="message-circle"></i>
                FAQs
              </button>
              <button
                className={`nav-item ${activeTab === 'contact' ? 'active' : ''}`}
                onClick={() => setActiveTab('contact')}
              >
                <i data-feather="mail"></i>
                Contact Support
              </button>
            </nav>
          </div>

          <div className="help-main">
            {activeTab === 'faqs' && (
              <div className="help-section">
                <div className="section-header">
                  <h3><i data-feather="message-circle"></i> Frequently Asked Questions</h3>
                  <p>Find quick answers to common questions about CRISP</p>
                </div>
                
                {filteredFAQs.map((category, categoryIndex) => (
                  <div key={categoryIndex} className="faq-category">
                    <h4>{category.category}</h4>
                    {category.questions.map((qa, qaIndex) => {
                      const faqId = `${categoryIndex}-${qaIndex}`;
                      return (
                        <div key={qaIndex} className="faq-item">
                          <button
                            className={`faq-question ${expandedFAQ === faqId ? 'expanded' : ''}`}
                            onClick={() => setExpandedFAQ(expandedFAQ === faqId ? null : faqId)}
                          >
                            <span>{qa.question}</span>
                            <i data-feather={expandedFAQ === faqId ? 'chevron-up' : 'chevron-down'}></i>
                          </button>
                          {expandedFAQ === faqId && (
                            <div className="faq-answer">
                              <p>{qa.answer}</p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'contact' && (
              <div className="help-section">
                <div className="section-header">
                  <h3><i data-feather="mail"></i> Contact Support</h3>
                  <p>Get help from our support team</p>
                </div>
                
                <div className="contact-options">
                  <div className="contact-card">
                    <div className="contact-icon">
                      <i data-feather="mail"></i>
                    </div>
                    <div className="contact-details">
                      <h4>Email Support</h4>
                      <p>Get help via email with detailed responses</p>
                      <a href="mailto:ib@bitm.co.za" className="contact-link">
                        ib@bitm.co.za
                      </a>
                    </div>
                  </div>
                  
                  <div className="contact-card">
                    <div className="contact-icon">
                      <i data-feather="globe"></i>
                    </div>
                    <div className="contact-details">
                      <h4>Online Support</h4>
                      <p>Access our comprehensive knowledge base</p>
                      <a href="https://bitm.co.za/" className="contact-link">
                        Visit Support Portal
                      </a>
                    </div>
                  </div>
                  
                </div>
                
                <div className="support-hours">
                  <h4><i data-feather="clock"></i> Support Hours</h4>
                  <div className="hours-grid">
                    <div className="hours-item">
                      <span className="day">Monday - Friday</span>
                      <span className="time">8:00 AM - 6:00 PM SAST</span>
                    </div>
                    <div className="hours-item">
                      <span className="day">Saturday</span>
                      <span className="time">9:00 AM - 2:00 PM SAST</span>
                    </div>
                    <div className="hours-item">
                      <span className="day">Sunday</span>
                      <span className="time">Emergency Support Only</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {filteredSections[activeTab] && (
              <div className="help-section">
                <div className="section-header">
                  <h3>
                    <i data-feather={filteredSections[activeTab].icon}></i>
                    {filteredSections[activeTab].title}
                  </h3>
                  <p>Learn about {filteredSections[activeTab].title.toLowerCase()} features and best practices</p>
                </div>
                
                <div className="help-grid">
                  {filteredSections[activeTab].content.map((item, index) => (
                    <div key={index} className="help-card">
                      <div className="card-header">
                        <div className="card-type">
                          <i data-feather={item.type === 'tutorial' ? 'video' : 'book-open'}></i>
                          <span>{item.type}</span>
                        </div>
                        <span className="duration">{item.duration}</span>
                      </div>
                      <h4>{item.title}</h4>
                      <p>{item.description}</p>
                      {/* Use a button with onClick handler */}
                      {item.type && (
                        <button 
                          className="help-link"
                          onClick={(e) => handleTutorialClick(item, e)}
                          data-tutorial={item.title}
                        >
                          <span>View {item.type}</span>
                          <i data-feather="external-link"></i>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Video Modal */}
      {showVideoModal && (
        <div className="video-overlay" onClick={() => setShowVideoModal(false)}>
          <div className="video-modal" onClick={e => e.stopPropagation()}>
            <div className="video-header">
              <h3>CRISP System Demo</h3>
              <button className="video-close" onClick={() => setShowVideoModal(false)}>
                <i data-feather="x">×</i>
              </button>
            </div>
            <div className="video-container">
              <video 
                width="100%" 
                height="100%" 
                controls 
                autoPlay
                src={vid}
                onError={(e) => console.error('Video load error:', e)}
                ref={videoRef => {
                  if (videoRef && !showVideoModal) {
                    videoRef.pause();
                  }
                }}
              >
                <source src={vid} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CrispHelp;