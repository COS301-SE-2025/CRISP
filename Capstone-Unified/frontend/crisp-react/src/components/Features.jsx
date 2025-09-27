import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import ElectricBorder from './ElectricBorder';
import GradientText from './GradientText';

gsap.registerPlugin(ScrollTrigger);

function Features() {
  const [ref, inView] = useInView({
    threshold: 0.1,
    triggerOnce: true
  });

  const features = [
    {
      icon: "🛡️",
      title: "Real-Time Threat Detection",
      description: "Advanced AI-powered detection system continuously monitors and identifies emerging cyber threats across educational networks.",
      details: ["24/7 automated monitoring", "Machine learning threat classification", "Instant alert system"],
      color: "#4285f4",
      gradient: "linear-gradient(135deg, #4285f4, #1976d2)"
    },
    {
      icon: "🔐",
      title: "Privacy-First Architecture",
      description: "Built with student data privacy at its core, ensuring FERPA compliance while enabling effective threat intelligence sharing.",
      details: ["FERPA compliant anonymization", "Zero-knowledge sharing", "Encrypted data transmission"],
      color: "#34a853",
      gradient: "linear-gradient(135deg, #34a853, #2e7d32)"
    },
    {
      icon: "🌐",
      title: "Collaborative Intelligence",
      description: "Connect with trusted educational institutions to share anonymized threat intelligence and strengthen collective defense.",
      details: ["Trusted institution network", "Peer-to-peer intelligence sharing", "Collaborative threat hunting"],
      color: "#fbbc04",
      gradient: "linear-gradient(135deg, #fbbc04, #f57f17)"
    },
    {
      icon: "📊",
      title: "Advanced Analytics",
      description: "Comprehensive dashboards and reporting tools provide deep insights into threat landscapes and security posture.",
      details: ["Interactive threat visualizations", "Custom security reports", "Trend analysis and forecasting"],
      color: "#ea4335",
      gradient: "linear-gradient(135deg, #ea4335, #c62828)"
    },
    {
      icon: "⚡",
      title: "MITRE ATT&CK Integration",
      description: "Leverage the MITRE ATT&CK framework for standardized threat intelligence and tactical analysis.",
      details: ["ATT&CK technique mapping", "Tactical analysis tools", "Standardized threat classification"],
      color: "#9c27b0",
      gradient: "linear-gradient(135deg, #9c27b0, #7b1fa2)"
    },
    {
      icon: "🔄",
      title: "Automated Response",
      description: "Smart automation capabilities enable rapid response to detected threats and streamlined security operations.",
      details: ["Automated threat containment", "Smart playbook execution", "Integrated SOAR capabilities"],
      color: "#00bcd4",
      gradient: "linear-gradient(135deg, #00bcd4, #0097a7)"
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2
      }
    }
  };

  const cardVariants = {
    hidden: {
      opacity: 0,
      y: 80,
      scale: 0.8,
      rotateX: -20
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      rotateX: 0,
      transition: {
        duration: 0.8,
        ease: "back.out(1.2)",
        type: "spring",
        stiffness: 80
      }
    }
  };

  return (
    <section id="features" className="features-new">
      <div className="container">
        <motion.div
          className="features-header"
          initial={{ opacity: 0, y: 50 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
        >
          <div className="header-badge">
            <span className="badge-icon">✨</span>
            <span>Platform Features</span>
          </div>
          <h2 className="features-title">
            <GradientText text="Next-Generation Security" />
            <br />
            <span className="title-subtitle">for Educational Excellence</span>
          </h2>
          <p className="features-description">
            Discover how CRISP revolutionizes cybersecurity for educational institutions
            with cutting-edge threat intelligence, privacy-first design, and collaborative defense.
          </p>
        </motion.div>

        <motion.div
          ref={ref}
          className="features-grid"
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={cardVariants}
              className="feature-card-new"
              whileHover={{
                scale: 1.03,
                y: -8,
                rotateY: 5,
                transition: { duration: 0.3 }
              }}
              style={{ perspective: "1000px" }}
            >
              <ElectricBorder className="feature-border">
                <div className="feature-content">
                  <div
                    className="feature-background"
                    style={{ background: feature.gradient }}
                  />
                  <div className="feature-icon">{feature.icon}</div>
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                </div>
              </ElectricBorder>
            </motion.div>
          ))}
        </motion.div>
      </div>

      <style jsx>{`
        .features {
          padding: 100px 0;
          background: linear-gradient(135deg, #0a0b0d 0%, #1a1b1e 100%);
          position: relative;
        }

        .features::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: radial-gradient(ellipse at 30% 70%, rgba(52, 168, 83, 0.05) 0%, transparent 70%);
          pointer-events: none;
        }

        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
          position: relative;
          z-index: 1;
        }

        .section-header {
          text-align: center;
          margin-bottom: 4rem;
        }

        .section-title {
          font-size: 3rem;
          font-weight: 800;
          margin-bottom: 1rem;
          color: #ffffff;
        }

        .highlight {
          background: linear-gradient(135deg, #4285f4, #34a853);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .section-description {
          font-size: 1.2rem;
          color: #b0b0b0;
          max-width: 700px;
          margin: 0 auto;
          line-height: 1.6;
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 2rem;
          max-width: 1100px;
          margin: 0 auto;
        }

        .feature-card {
          position: relative;
          cursor: pointer;
        }

        .feature-content {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          padding: 2rem;
          height: 100%;
          position: relative;
          overflow: hidden;
          transition: all 0.3s ease;
        }

        .feature-card:hover .feature-content {
          border-color: rgba(255, 255, 255, 0.2);
          background: rgba(255, 255, 255, 0.08);
        }

        .feature-icon {
          font-size: 3rem;
          margin-bottom: 1.5rem;
          display: block;
        }

        .feature-title {
          font-size: 1.5rem;
          font-weight: 700;
          margin-bottom: 1rem;
          color: #ffffff;
        }

        .feature-description {
          color: #b0b0b0;
          line-height: 1.6;
          margin-bottom: 1.5rem;
        }

        .feature-accent {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 3px;
          transform-origin: left;
        }

        @media (max-width: 768px) {
          .section-title {
            font-size: 2.5rem;
          }
          
          .features-grid {
            grid-template-columns: 1fr;
            max-width: 100%;
          }
          
          .feature-content {
            padding: 1.5rem;
          }
        }
      `}</style>
    </section>
  );
}

export default Features;