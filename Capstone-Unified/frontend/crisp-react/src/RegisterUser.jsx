import React, { useState } from 'react';

function RegisterUser({ onRegisterSuccess, switchView }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    organization: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock successful registration
      const mockResponse = {
        user: {
          username: formData.username,
          email: formData.email,
          first_name: formData.firstName,
          last_name: formData.lastName
        },
        token: 'mock-jwt-token'
      };

      onRegisterSuccess(mockResponse);
    } catch (error) {
      setError('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: '#f5f7fa',
      padding: '2rem'
    }}>
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        maxWidth: '500px',
        width: '100%',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Register New User</h2>
        
        {error && (
          <div style={{
            background: '#fee',
            color: '#c53030',
            padding: '1rem',
            borderRadius: '4px',
            marginBottom: '1rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label>First Name</label>
              <input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
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
            <div>
              <label>Last Name</label>
              <input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
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
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
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
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
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
            <label>Organization</label>
            <input
              type="text"
              name="organization"
              value={formData.organization}
              onChange={handleChange}
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
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
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

          <div style={{ marginBottom: '2rem' }}>
            <label>Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
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
              cursor: 'pointer',
              marginBottom: '1rem'
            }}
          >
            {isLoading ? 'Registering...' : 'Register'}
          </button>

          <div style={{ textAlign: 'center' }}>
            <button
              type="button"
              onClick={switchView}
              style={{
                background: 'none',
                border: 'none',
                color: '#0056b3',
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
            >
              Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default RegisterUser;