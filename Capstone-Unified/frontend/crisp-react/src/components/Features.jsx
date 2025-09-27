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
                transition: { duration: 0.3 }
              }}
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
    </section>
  );
}

export default Features;