import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import Stats from './components/Stats';
import CTA from './components/CTA';
import Footer from './components/Footer';

function LandingPage() {
  return (
    <div className="landing-page">
      <style>
        {`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
              'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
              sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            background-color: #0a0b0d;
            color: #ffffff;
            line-height: 1.6;
          }

          .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          /* Header Styles */
          .header {
            background: rgba(10, 11, 13, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
          }

          .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 20px;
          }

          .logo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #ffffff;
            font-weight: bold;
            font-size: 1.5rem;
          }

          .logo-icon {
            margin-right: 0.5rem;
            color: #4285f4;
            font-size: 1.8rem;
          }

          .nav {
            display: flex;
          }

          .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
          }

          .nav-links a {
            color: #ffffff;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
          }

          .nav-links a:hover {
            color: #4285f4;
          }

          .header-actions {
            display: flex;
            gap: 1rem;
            align-items: center;
          }

          .mobile-menu-toggle {
            display: none;
            background: none;
            border: none;
            color: #ffffff;
            font-size: 1.5rem;
            cursor: pointer;
          }

          /* Button Styles */
          .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
            font-size: 1rem;
          }

          .btn-primary {
            background: linear-gradient(135deg, #4285f4, #34a853);
            color: #ffffff;
          }

          .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(66, 133, 244, 0.3);
          }

          .btn-outline {
            background: transparent;
            border: 2px solid #4285f4;
            color: #4285f4;
          }

          .btn-outline:hover {
            background: #4285f4;
            color: #ffffff;
          }

          .btn-large {
            padding: 1rem 2rem;
            font-size: 1.1rem;
          }

          /* Hero Section */
          .hero {
            min-height: 100vh;
            padding: 80px 0;
            background: linear-gradient(135deg, #0a0b0d 0%, #1a1b1e 100%);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
          }

          .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs><radialGradient id="grad" cx="50%" cy="50%" r="50%"><stop offset="0%" style="stop-color:%234285f4;stop-opacity:0.1" /><stop offset="100%" style="stop-color:%234285f4;stop-opacity:0" /></radialGradient></defs><circle cx="500" cy="500" r="500" fill="url(%23grad)" /></svg>') no-repeat center;
            background-size: cover;
            opacity: 0.5;
          }

          .hero-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            align-items: center;
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 1.5rem;
          }

          .highlight {
            background: linear-gradient(135deg, #4285f4, #34a853);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }

          .hero-description {
            font-size: 1.25rem;
            color: #b0b0b0;
            margin-bottom: 2rem;
            line-height: 1.6;
          }

          .hero-actions {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
          }

          /* Dashboard Preview */
          .dashboard-preview {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
          }

          .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          }

          .dashboard-logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #4285f4;
            font-weight: 600;
          }

          .dashboard-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
          }

          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #34a853;
            animation: pulse 2s infinite;
          }

          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
          }

          .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
          }

          .stat-card {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
          }

          .stat-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
          }

          .threat-icon { background: rgba(244, 67, 54, 0.2); color: #f44336; }
          .institution-icon { background: rgba(66, 133, 244, 0.2); color: #4285f4; }
          .sharing-icon { background: rgba(52, 168, 83, 0.2); color: #34a853; }

          .stat-number {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
          }

          .stat-label {
            font-size: 0.8rem;
            color: #b0b0b0;
          }

          /* Stats Section */
          .stats {
            padding: 120px 0;
            background: transparent;
            display: flex;
            align-items: center;
            min-height: 50vh;
            width: 100vw;
            margin-left: calc(50% - 50vw);
            overflow-x: visible;
            box-sizing: border-box;
          }

          .stats .container {
            width: calc(100vw - 40px);
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            box-sizing: border-box;
          }

          .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            justify-items: center;
            align-items: center;
            width: 100%;
            max-width: 100%;
            overflow: visible;
          }

          .stat-item {
            text-align: center;
            padding: 1.5rem 0.25rem;
            transition: transform 0.3s ease;
            position: relative;
            width: 100%;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
            overflow: visible;
          }

          .stat-item:hover {
            transform: translateY(-8px);
          }

          .stat-item::after,
          .stat-item::before {
            display: none !important;
            content: none !important;
            border: none !important;
            background: none !important;
          }

          /* Aggressively remove any borders or lines that might appear */
          .stats,
          .stats *,
          .stats::before,
          .stats::after,
          .stats *::before,
          .stats *::after {
            border: none !important;
            border-top: none !important;
            border-bottom: none !important;
            border-left: none !important;
            border-right: none !important;
            box-shadow: none !important;
            outline: none !important;
            text-decoration: none !important;
            text-decoration-line: none !important;
            text-decoration-color: transparent !important;
            text-decoration-style: none !important;
            text-underline-offset: 0 !important;
            -webkit-text-decoration-line: none !important;
            -webkit-text-decoration: none !important;
          }

          .stats .stat-item {
            border: none !important;
            border-top: none !important;
            border-bottom: none !important;
            border-left: none !important;
            border-right: none !important;
            box-shadow: none !important;
            outline: none !important;
            text-decoration: none !important;
            position: relative;
          }

          .stats .stat-item::before,
          .stats .stat-item::after {
            display: none !important;
            content: none !important;
            border: none !important;
            background: none !important;
            height: 0 !important;
            width: 0 !important;
          }

          .stats svg,
          .stats i,
          .stats .stat-icon,
          .stats .stat-number,
          .stats .stat-label {
            border: none !important;
            outline: none !important;
            text-decoration: none !important;
            text-decoration-line: none !important;
            background-image: none !important;
          }

          .stat-item .stat-icon,
          .stat-item svg {
            width: 100px !important;
            height: 100px !important;
            margin: 0 auto 1.5rem;
            background: transparent !important;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            color: #4285f4 !important;
            stroke: #4285f4 !important;
            transition: color 0.3s ease, stroke 0.3s ease;
            border: none !important;
            outline: none !important;
          }

          .stat-item:hover .stat-icon,
          .stat-item:hover svg {
            color: #34a853 !important;
            stroke: #34a853 !important;
          }

          .stats .stat-item .stat-number {
            font-size: clamp(2.5rem, 4vw, 4rem) !important;
            font-weight: 900 !important;
            margin-bottom: 1rem !important;
            background: linear-gradient(135deg, #4285f4, #34a853) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            line-height: 1 !important;
            color: transparent !important;
            text-decoration: none !important;
            border: none !important;
            white-space: nowrap !important;
            overflow: visible !important;
          }

          .stat-item .stat-label {
            font-size: 1.3rem;
            color: #b0b0b0;
            font-weight: 500;
            margin-top: 0.5rem;
            text-decoration: none !important;
            text-decoration-line: none !important;
            border-bottom: none !important;
          }

          /* Force remove any possible text decoration or underlines */
          .stats .stat-item,
          .stats .stat-item * {
            text-decoration: none !important;
            text-decoration-line: none !important;
            text-decoration-color: transparent !important;
            text-decoration-style: none !important;
            text-underline-offset: 0 !important;
            -webkit-text-decoration: none !important;
            -webkit-text-decoration-line: none !important;
            border-bottom: none !important;
            border-bottom-width: 0 !important;
            border-bottom-style: none !important;
            border-bottom-color: transparent !important;
          }

          /* Ensure container and grid have no borders */
          .stats .container,
          .stats .stats-grid {
            border: none !important;
            border-bottom: none !important;
            background-image: none !important;
            text-decoration: none !important;
          }

          /* Responsive Design for Stats */
          @media (max-width: 1400px) {
            .stats .container {
              width: calc(100vw - 30px);
              max-width: 1000px;
              padding: 0 15px;
            }
            .stats-grid {
              gap: 1rem;
            }
            .stat-item {
              padding: 1.25rem 0.1rem;
            }
            .stats .stat-item .stat-number {
              font-size: clamp(2rem, 3.5vw, 3.5rem) !important;
            }
          }

          @media (max-width: 1100px) {
            .stats-grid {
              grid-template-columns: repeat(2, 1fr);
              gap: 2rem;
            }
            .stats .container {
              width: calc(100vw - 20px);
              padding: 0 10px;
            }
            .stat-item {
              padding: 2rem 0.5rem;
            }
          }

          @media (max-width: 1200px) {
            .stats .container {
              max-width: 900px;
              padding: 0 15px;
            }
            .stats-grid {
              gap: 1.25rem;
            }
            .stat-item .stat-icon,
            .stat-item svg {
              width: 80px !important;
              height: 80px !important;
            }
            .stats .stat-item .stat-number {
              font-size: 3.5rem !important;
              background: linear-gradient(135deg, #4285f4, #34a853) !important;
              -webkit-background-clip: text !important;
              -webkit-text-fill-color: transparent !important;
              background-clip: text !important;
              color: transparent !important;
            }
          }

          @media (max-width: 900px) {
            .stats-grid {
              grid-template-columns: repeat(2, 1fr);
              gap: 2rem;
            }
            .stats .container {
              padding: 0 15px;
              max-width: 100%;
            }
            .stat-item {
              padding: 2rem 0.5rem;
            }
          }

          @media (max-width: 768px) {
            .stats-grid {
              grid-template-columns: repeat(2, 1fr);
              gap: 1.5rem;
            }
            .stats .container {
              padding: 0 15px;
            }
            .stat-item {
              padding: 2rem 0.5rem;
            }
            .stat-item .stat-icon,
            .stat-item svg {
              width: 60px !important;
              height: 60px !important;
            }
            .stats .stat-item .stat-number {
              font-size: 2.5rem !important;
              background: linear-gradient(135deg, #4285f4, #34a853) !important;
              -webkit-background-clip: text !important;
              -webkit-text-fill-color: transparent !important;
              background-clip: text !important;
              color: transparent !important;
            }
            .stat-item .stat-label {
              font-size: 1.1rem;
            }
          }

          @media (max-width: 480px) {
            .stats-grid {
              grid-template-columns: 1fr;
              gap: 2rem;
            }
            .stat-item {
              padding: 1.5rem 1rem;
            }
            .stat-item .stat-icon,
            .stat-item svg {
              width: 80px !important;
              height: 80px !important;
            }
            .stats .stat-item .stat-number {
              font-size: 3rem !important;
              background: linear-gradient(135deg, #4285f4, #34a853) !important;
              -webkit-background-clip: text !important;
              -webkit-text-fill-color: transparent !important;
              background-clip: text !important;
              color: transparent !important;
            }
            .stat-item .stat-label {
              font-size: 1.2rem;
            }
          }

          /* Features Section */
          .features {
            padding: 80px 0;
            display: flex;
            align-items: center;
            min-height: 80vh;
          }

          .features .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          .section-header {
            text-align: center;
            margin-bottom: 4rem;
          }

          .section-header h2 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
          }

          .section-header p {
            font-size: 1.2rem;
            color: #b0b0b0;
            max-width: 600px;
            margin: 0 auto;
          }

          .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            justify-items: center;
            align-items: stretch;
            max-width: 1100px;
            margin: 0 auto;
          }

          .feature-card {
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
          }

          .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(66, 133, 244, 0.2);
          }

          .feature-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #4285f4, #34a853);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: #ffffff;
            margin-bottom: 1.5rem;
          }

          .feature-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
          }

          .feature-description {
            color: #b0b0b0;
            line-height: 1.6;
          }

          /* CTA Section */
          .cta {
            padding: 80px 0;
            background: linear-gradient(135deg, #4285f4, #34a853);
            text-align: center;
            display: flex;
            align-items: center;
            min-height: 60vh;
          }

          .cta .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }

          .cta-content h2 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #ffffff;
          }

          .cta-content p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            color: rgba(255, 255, 255, 0.9);
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
          }

          .cta-actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
          }

          .cta .btn-primary {
            background: #ffffff;
            color: #4285f4;
          }

          .cta .btn-outline {
            border-color: #ffffff;
            color: #ffffff;
          }

          .cta .btn-outline:hover {
            background: #ffffff;
            color: #4285f4;
          }

          .cta-features {
            display: flex;
            gap: 2rem;
            justify-content: center;
            flex-wrap: wrap;
          }

          .cta-feature {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: rgba(255, 255, 255, 0.9);
          }

          .cta-feature i {
            color: #ffffff;
          }

          /* Footer */
          .footer {
            background: #0a0b0d;
            padding: 60px 0 20px;
          }

          .footer-content {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 3rem;
            margin-bottom: 2rem;
          }

          .footer-logo {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            font-size: 1.5rem;
            font-weight: bold;
          }

          .footer-logo .logo-icon {
            margin-right: 0.5rem;
            color: #4285f4;
          }

          .footer-description {
            color: #b0b0b0;
            margin-bottom: 1.5rem;
            line-height: 1.6;
          }

          .footer-social {
            display: flex;
            gap: 1rem;
          }

          .footer-social a {
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            text-decoration: none;
            transition: background 0.3s ease;
          }

          .footer-social a:hover {
            background: #4285f4;
          }

          .footer-section h4 {
            margin-bottom: 1rem;
            color: #ffffff;
          }

          .footer-section ul {
            list-style: none;
          }

          .footer-section ul li {
            margin-bottom: 0.5rem;
          }

          .footer-section ul li a {
            color: #b0b0b0;
            text-decoration: none;
            transition: color 0.3s ease;
          }

          .footer-section ul li a:hover {
            color: #4285f4;
          }

          .footer-bottom {
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
          }

          .footer-legal {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #b0b0b0;
            font-size: 0.9rem;
          }

          .footer-links {
            display: flex;
            gap: 2rem;
          }

          .footer-links a {
            color: #b0b0b0;
            text-decoration: none;
            transition: color 0.3s ease;
          }

          .footer-links a:hover {
            color: #4285f4;
          }

          /* Responsive Design */
          @media (max-width: 768px) {
            .nav {
              display: none;
            }
            
            .nav-open {
              display: block;
              position: absolute;
              top: 100%;
              left: 0;
              right: 0;
              background: rgba(10, 11, 13, 0.95);
              backdrop-filter: blur(10px);
              border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .nav-open .nav-links {
              flex-direction: column;
              padding: 1rem;
              gap: 1rem;
            }
            
            .mobile-menu-toggle {
              display: block;
            }
            
            .header-actions {
              display: none;
            }
            
            .hero {
              min-height: 100vh;
              padding: 100px 0 60px;
            }
            
            .hero-container {
              grid-template-columns: 1fr;
              gap: 2rem;
              text-align: center;
            }
            
            .hero-title {
              font-size: 2.5rem;
            }
            
            .stats {
              min-height: 50vh;
              padding: 60px 0;
            }
            
            .features {
              min-height: auto;
              padding: 60px 0;
            }
            
            .cta {
              min-height: 50vh;
              padding: 60px 0;
            }
            
            .dashboard-stats {
              grid-template-columns: 1fr;
            }
            
            .features-grid {
              grid-template-columns: 1fr;
              max-width: 100%;
            }
            
            .footer-content {
              grid-template-columns: 1fr;
              gap: 2rem;
            }
            
            .footer-legal {
              flex-direction: column;
              gap: 1rem;
            }
            
            .cta-actions {
              flex-direction: column;
              align-items: center;
            }
          }
        `}
      </style>
      <Header />
      <Hero />
      <Stats />
      <Features />
      <CTA />
      <Footer />
    </div>
  );
}

export default LandingPage;