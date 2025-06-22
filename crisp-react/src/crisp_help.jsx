import React, { useState, useEffect } from 'react';
import './assets/crisp_help.css';

function CrispHelp({ isOpen, onClose, onNavigate }) {
  const [activeTab, setActiveTab] = useState('getting-started');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFAQ, setExpandedFAQ] = useState(null);

  // Initialize Feather icons when component mounts
  useEffect(() => {
    if (isOpen) {
      // Load Feather icons script if not already loaded
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
        // If already loaded, just replace the icons
        setTimeout(() => window.feather.replace(), 100);
      }
    }
  }, [isOpen, activeTab]);

  // Re-run feather.replace() when content changes
  useEffect(() => {
    if (window.feather && isOpen) {
      setTimeout(() => window.feather.replace(), 100);
    }
  }, [expandedFAQ, searchQuery, isOpen]);

  // Handle escape key to close
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  const handleTutorialClick = (item) => {
    if (item.link === 'construction') {
      onClose(); // Close the help modal first
      
      // Navigate to construction page
      if (onNavigate) {
        onNavigate('construction.jsx', item.id);
      } else {
        // Fallback: Direct navigation if no onNavigate prop
        window.location.href = '../construction.jsx';
      }
    } else if (item.link) {
      // Handle other types of links (URLs, etc.)
      if (item.link.startsWith('http')) {
        window.open(item.link, '_blank');
      } else {
        window.location.href = item.link;
      }
    }
  };

  if (!isOpen) return null;

  const helpSections = {
    'getting-started': {
      title: 'Getting Started',
      icon: 'play-circle',
      content: [
        {
          id: 'quick-start',
          title: 'Quick Start Guide',
          description: 'Learn the basics of CRISP in 5 minutes',
          type: 'tutorial',
          duration: '5 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'dashboard-overview',
          title: 'Dashboard Overview',
          description: 'Understanding your threat intelligence dashboard',
          type: 'tutorial',
          duration: '8 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'first-feed',
          title: 'Setting up Your First Feed',
          description: 'Connect to your first threat intelligence feed',
          type: 'guide',
          duration: '10 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'account-setup',
          title: 'User Account Setup',
          description: 'Configure your profile and preferences',
          type: 'guide',
          duration: '3 min',
          link: 'construction' // Change this to actual URL later
        }
      ]
    },
    'threat-feeds': {
      title: 'Threat Feeds',
      icon: 'rss',
      content: [
        {
          id: 'stix-taxii',
          title: 'Managing STIX/TAXII Feeds',
          description: 'Configure and monitor STIX/TAXII data sources',
          type: 'tutorial',
          duration: '12 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'misp-integration',
          title: 'MISP Integration',
          description: 'Connect and sync with MISP instances',
          type: 'tutorial',
          duration: '15 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'feed-monitoring',
          title: 'Feed Health Monitoring',
          description: 'Track feed status and troubleshoot issues',
          type: 'guide',
          duration: '7 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'custom-feeds',
          title: 'Custom Feed Creation',
          description: 'Build custom threat intelligence feeds',
          type: 'guide',
          duration: '20 min',
          link: 'construction' // Change this to actual URL later
        }
      ]
    },
    'ioc-management': {
      title: 'IoC Management',
      icon: 'search',
      content: [
        {
          id: 'ioc-validation',
          title: 'IoC Validation and Verification',
          description: 'Best practices for validating indicators',
          type: 'guide',
          duration: '10 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'bulk-operations',
          title: 'Bulk IoC Operations',
          description: 'Import, export, and manage large IoC datasets',
          type: 'tutorial',
          duration: '12 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'ioc-sharing',
          title: 'IoC Sharing and Collaboration',
          description: 'Share indicators with trusted institutions',
          type: 'tutorial',
          duration: '8 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'automated-processing',
          title: 'Automated IoC Processing',
          description: 'Set up automated IoC enrichment and classification',
          type: 'guide',
          duration: '18 min',
          link: 'construction' // Change this to actual URL later
        }
      ]
    },
    'ttp-analysis': {
      title: 'TTP Analysis',
      icon: 'trending-up',
      content: [
        {
          id: 'mitre-mapping',
          title: 'MITRE ATT&CK Mapping',
          description: 'Map observed behaviors to MITRE ATT&CK framework',
          type: 'tutorial',
          duration: '15 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'pattern-recognition',
          title: 'TTP Pattern Recognition',
          description: 'Identify and analyze attack patterns',
          type: 'guide',
          duration: '12 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'threat-profiling',
          title: 'Threat Actor Profiling',
          description: 'Build comprehensive threat actor profiles',
          type: 'tutorial',
          duration: '20 min',
          link: 'construction' // Change this to actual URL later
        },
        {
          id: 'campaign-analysis',
          title: 'Campaign Analysis',
          description: 'Track and analyze multi-stage attack campaigns',
          type: 'guide',
          duration: '16 min',
          link: 'construction' // Change this to actual URL later
        }
      ]
    }
  };

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

  const filteredSections = Object.entries(helpSections).reduce((acc, [key, section]) => {
    if (searchQuery) {
      const filteredContent = section.content.filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
      if (filteredContent.length > 0) {
        acc[key] = { ...section, content: filteredContent };
      }
    } else {
      acc[key] = section;
    }
    return acc;
  }, {});

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
            <i data-feather="x"></i>
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
                className={`nav-item ${activeTab === 'threat-feeds' ? 'active' : ''}`}
                onClick={() => setActiveTab('threat-feeds')}
              >
                <i data-feather="rss"></i>
                Threat Feeds
              </button>
              <button
                className={`nav-item ${activeTab === 'ioc-management' ? 'active' : ''}`}
                onClick={() => setActiveTab('ioc-management')}
              >
                <i data-feather="search"></i>
                IoC Management
              </button>
              <button
                className={`nav-item ${activeTab === 'ttp-analysis' ? 'active' : ''}`}
                onClick={() => setActiveTab('ttp-analysis')}
              >
                <i data-feather="trending-up"></i>
                TTP Analysis
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
                      <a href="mailto:support@bluevision-itm.com" className="contact-link">
                        support@bluevision-itm.com
                      </a>
                    </div>
                  </div>
                  
                  <div className="contact-card">
                    <div className="contact-icon">
                      <i data-feather="phone"></i>
                    </div>
                    <div className="contact-details">
                      <h4>Phone Support</h4>
                      <p>Speak directly with our technical team</p>
                      <a href="tel:+27123456789" className="contact-link">
                        +27 (12) 345-6789
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
                      <a href="https://support.crisp.bluevision-itm.com" className="contact-link">
                        Visit Support Portal
                      </a>
                    </div>
                  </div>
                  
                  <div className="contact-card">
                    <div className="contact-icon">
                      <i data-feather="message-square"></i>
                    </div>
                    <div className="contact-details">
                      <h4>Live Chat</h4>
                      <p>Chat with support during business hours</p>
                      <button className="btn btn-primary btn-sm">
                        Start Live Chat
                      </button>
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
                      <button 
                        className="help-link" 
                        onClick={() => handleTutorialClick(item)}
                      >
                        <span>View {item.type}</span>
                        <i data-feather="external-link"></i>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CrispHelp;