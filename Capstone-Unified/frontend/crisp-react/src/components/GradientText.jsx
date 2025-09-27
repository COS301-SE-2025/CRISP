import React from 'react';
import './GradientText.css';

const GradientText = ({ text }) => {
  return (
    <span className="gradient-text">
      {text}
    </span>
  );
};

export default GradientText;