import React from 'react';
import './ElectricBorder.css';

const ElectricBorder = ({ children, className }) => {
  return (
    <div className={`electric-border ${className}`}>
      {children}
    </div>
  );
};

export default ElectricBorder;