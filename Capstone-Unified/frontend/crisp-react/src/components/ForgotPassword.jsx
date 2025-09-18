import React, { useState } from 'react';

// API configuration
const API_BASE_URL = 'http://localhost:8000';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    console.log('🔄 Starting forgot password request for email:', email);
    
    try {
      const requestUrl = `${API_BASE_URL}/api/auth/forgot-password/`;
      const requestBody = { email };
      
      console.log('📤 Making request to:', requestUrl);
      console.log('📤 Request body:', requestBody);
      
      const response = await fetch(requestUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));

      const data = await response.json();
      console.log('📥 Response data:', data);

      if (response.ok && data.success) {
        console.log('✅ Password reset email sent successfully');
        setIsSubmitted(true);
      } else {
        console.error('❌ Failed to send password reset email:', data.message);
        alert(data.message || 'Failed to send password reset email. Please try again.');
      }
    } catch (error) {
      console.error('💥 Forgot password error:', error);
      alert('An error occurred while sending the password reset email. Please try again later.');
    } finally {
      setIsLoading(false);
      console.log('🏁 Forgot password request completed');
    }
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
            <h2>Forgot Password</h2>
            <p style={{ marginBottom: '1.5rem', color: '#666' }}>
              Enter your email address and we'll send you a link to reset your password.
            </p>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label>Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
                {isLoading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
            <div style={{ marginTop: '1rem', textAlign: 'center' }}>
              <a href="/login" style={{ color: '#0056b3' }}>Back to Login</a>
            </div>
          </>
        ) : (
          <>
            <h2>Check Your Email</h2>
            <p style={{ marginBottom: '1.5rem', color: '#666' }}>
              We've sent a password reset link to {email}
            </p>
            <a href="/login" style={{ color: '#0056b3' }}>Back to Login</a>
          </>
        )}
      </div>
    </div>
  );
}

export default ForgotPassword;