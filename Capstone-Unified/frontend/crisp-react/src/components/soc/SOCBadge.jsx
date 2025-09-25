import React from 'react';

const SOCBadge = ({ text, color, className = '', style = {} }) => {
  const badgeStyle = {
    backgroundColor: color,
    color: 'white',
    padding: '4px 8px',
    fontSize: '0.75rem',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    borderRadius: '2px',
    display: 'inline-block',
    ...style
  };

  return (
    <span className={className} style={badgeStyle}>
      {text}
    </span>
  );
};

// Helper functions for SOC colors
export const getPriorityColor = (priority) => {
  switch (priority) {
    case 'critical': return '#dc3545';
    case 'high': return '#fd7e14';
    case 'medium': return '#ffc107';
    case 'low': return '#28a745';
    default: return '#6c757d';
  }
};

export const getStatusColor = (status) => {
  switch (status) {
    case 'new': return '#007bff';
    case 'assigned': return '#17a2b8';
    case 'in_progress': return '#ffc107';
    case 'resolved': return '#28a745';
    case 'closed': return '#6c757d';
    case 'false_positive': return '#6f42c1';
    default: return '#6c757d';
  }
};

export default SOCBadge;