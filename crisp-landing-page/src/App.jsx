import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import Stats from './components/Stats';
import CTA from './components/CTA';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <div className="App">
      <Header />
      <Hero />
      <Stats />
      <Features />
      <CTA />
      <Footer />
    </div>
  );
}

export default App;
