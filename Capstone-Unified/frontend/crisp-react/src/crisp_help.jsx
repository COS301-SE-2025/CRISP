import React from 'react';

function CrispHelp({ isOpen, onClose, onNavigate }) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 9999
    }}>
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2>Help & Support</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer' }}>×</button>
        </div>
        
        <div style={{ marginBottom: '1.5rem' }}>
          <h3>Getting Started</h3>
          <p>Welcome to CRISP - Cyber Risk Information Sharing Platform. This platform allows educational institutions to securely share threat intelligence.</p>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3>Login Help</h3>
          <p>If you're having trouble logging in:</p>
          <ul>
            <li>Ensure you're using the correct username and password</li>
            <li>Contact your system administrator for account issues</li>
            <li>Use the "Forgot Password" link if you've forgotten your password</li>
          </ul>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3>Contact Support</h3>
          <p>For technical support, please contact:</p>
          <p><strong>Email:</strong> support@bluevision.com</p>
          <p><strong>Phone:</strong> +1 (555) 123-4567</p>
        </div>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
          <button onClick={onClose} style={{
            padding: '0.5rem 1rem',
            background: '#0056b3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default CrispHelp;