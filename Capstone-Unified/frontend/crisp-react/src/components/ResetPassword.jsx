import React, { useState } from 'react';

function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsSubmitted(true);
    setIsLoading(false);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: '#f5f7fa'
    }}>
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        maxWidth: '400px',
        width: '90%',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        {!isSubmitted ? (
          <>
            <h2>Reset Password</h2>
            <p style={{ marginBottom: '1.5rem', color: '#666' }}>
              Enter your new password below.
            </p>
            {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label>New Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ 
                    width: '100%', 
                    padding: '0.75rem', 
                    marginTop: '0.25rem',
                    border: '1px solid #e2e8f0',
                    borderRadius: '4px'
                  }}
                  required
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label>Confirm New Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  style={{ 
                    width: '100%', 
                    padding: '0.75rem', 
                    marginTop: '0.25rem',
                    border: '1px solid #e2e8f0',
                    borderRadius: '4px'
                  }}
                  required
                />
              </div>
              <button 
                type="submit" 
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: '#0056b3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                {isLoading ? 'Resetting...' : 'Reset Password'}
              </button>
            </form>
          </>
        ) : (
          <>
            <h2>Password Reset Complete</h2>
            <p style={{ marginBottom: '1.5rem', color: '#666' }}>
              Your password has been successfully reset.
            </p>
            <a href="/login" style={{ color: '#0056b3' }}>Go to Login</a>
          </>
        )}
      </div>
    </div>
  );
}

export default ResetPassword;