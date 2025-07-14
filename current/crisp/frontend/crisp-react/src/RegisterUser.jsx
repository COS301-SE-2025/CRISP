import { useState } from 'react';
import { registerUser } from './api'; // Import the real API function

function RegisterUser({ onRegisterSuccess, switchView }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [institution, setInstitution] = useState('');
  const [role, setRole] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (!username || !password || !fullName || !institution || !role) {
      setError('All fields are required');
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(username)) {
      setError('Please enter a valid email address');
      return;
    }

    // Password strength validation
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setSuccess('');
    
    try {
      console.log('Attempting to register user:', { username, fullName, institution, role });
      
      // Call the real API function to register the user
      const userData = await registerUser(username, password, fullName, institution, role);
      
      console.log('Registration successful:', userData);
      setSuccess('User registered successfully!');
      
      // Clear form
      setUsername('');
      setPassword('');
      setConfirmPassword('');
      setFullName('');
      setInstitution('');
      setRole('');
      
      // Call the onRegisterSuccess callback with user data
      if (onRegisterSuccess) {
        // If we're in admin mode registering another user, don't auto-login
        const isAdminRegistering = localStorage.getItem("crisp_auth_token");
        if (isAdminRegistering) {
          setTimeout(() => {
            onRegisterSuccess();
          }, 2000);
        } else {
          // If registering as a new user, auto-login
          onRegisterSuccess({
            user: userData.user,
            token: userData.token
          });
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      if (typeof error === 'string') {
        setError(error);
      } else if (error.message) {
        setError(error.message);
      } else if (error.detail) {
        setError(error.detail);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Check if user is already authenticated (admin registering another user)
  const isAdminMode = localStorage.getItem("crisp_auth_token");

  return (
    <>
      <CSSStyles />
      <div className="login-page">
        <div className="login-content">
          <div className="login-left">
            <div className="brand-info">
              <div className="logo-container">
                <div className="brand-logo-placeholder">CRISP</div>
              </div>
              <h2>Cyber Risk Information Sharing Platform</h2>
              <p>{isAdminMode ? 'Register a new user to access the platform' : 'Create your account to access threat intelligence sharing and committee management'}</p>
              
              <div className="feature-list">
                <div className="feature-item">
                  <div className="feature-icon"><i className="fas fa-shield-alt"></i></div>
                  <div className="feature-text">
                    <h3>Monitor Threats</h3>
                    <p>Track and analyze security threats across institutions</p>
                  </div>
                </div>
                
                <div className="feature-item">
                  <div className="feature-icon"><i className="fas fa-exchange-alt"></i></div>
                  <div className="feature-text">
                    <h3>Share Intelligence</h3>
                    <p>Securely exchange threat data with trusted partners</p>
                  </div>
                </div>
                
                <div className="feature-item">
                  <div className="feature-icon"><i className="fas fa-chart-line"></i></div>
                  <div className="feature-text">
                    <h3>Analyze Patterns</h3>
                    <p>Identify emerging threat patterns with advanced analytics</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="login-right">
            <div className="login-form-container">
              <h2>{isAdminMode ? 'Register New User' : 'Create Account'}</h2>
              <p className="subtitle">{isAdminMode ? 'Add a new user to the platform' : 'Join the CRISP community'}</p>
              
              {error && <div className="error-message"><i className="fas fa-exclamation-circle"></i> {error}</div>}
              {success && <div className="success-message"><i className="fas fa-check-circle"></i> {success}</div>}
              
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="fullName">Full Name *</label>
                  <div className="input-with-icon">
                    <i className="fas fa-user"></i>
                    <input 
                      type="text" 
                      id="fullName" 
                      value={fullName} 
                      onChange={(e) => setFullName(e.target.value)} 
                      placeholder="John Doe"
                      required
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="username">Email Address *</label>
                  <div className="input-with-icon">
                    <i className="fas fa-envelope"></i>
                    <input 
                      type="email" 
                      id="username" 
                      value={username} 
                      onChange={(e) => setUsername(e.target.value)} 
                      placeholder="john.doe@example.com"
                      required
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="institution">Institution/Organization *</label>
                  <div className="input-with-icon">
                    <i className="fas fa-building"></i>
                    <input 
                      type="text" 
                      id="institution" 
                      value={institution} 
                      onChange={(e) => setInstitution(e.target.value)} 
                      placeholder="University of Pretoria"
                      required
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="role">Role *</label>
                  <div className="input-with-icon">
                    <i className="fas fa-user-shield"></i>
                    <select 
                      id="role" 
                      value={role} 
                      onChange={(e) => setRole(e.target.value)}
                      className="role-select"
                      required
                    >
                      <option value="">Select a role</option>
                      <option value="analyst">Security Analyst</option>
                      <option value="admin">Administrator</option>
                      <option value="user">Standard User</option>
                      <option value="guest">Guest</option>
                    </select>
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="password">Password *</label>
                  <div className="input-with-icon">
                    <i className="fas fa-lock"></i>
                    <input 
                      type="password" 
                      id="password" 
                      value={password} 
                      onChange={(e) => setPassword(e.target.value)} 
                      placeholder="••••••••"
                      required
                      minLength="8"
                    />
                  </div>
                  <small className="password-hint">Password must be at least 8 characters long</small>
                </div>
                
                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirm Password *</label>
                  <div className="input-with-icon">
                    <i className="fas fa-lock"></i>
                    <input 
                      type="password" 
                      id="confirmPassword" 
                      value={confirmPassword} 
                      onChange={(e) => setConfirmPassword(e.target.value)} 
                      placeholder="••••••••"
                      required
                    />
                  </div>
                </div>
                
                <button 
                  type="submit"
                  className="btn-sign-in" 
                  disabled={isLoading}
                >
                  {isLoading ? 'Registering...' : (isAdminMode ? 'Register User' : 'Create Account')}
                </button>
              </form>
              
              <div className="login-footer">
                <p>
                  {isAdminMode ? (
                    <>Return to <a href="#" onClick={() => switchView ? switchView() : null} className="register-link">Dashboard</a></>
                  ) : (
                    <>Already have an account? <a href="#" onClick={() => switchView ? switchView() : null} className="register-link">Sign In</a></>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

// CSS Styles for Register with scrollable right panel
function CSSStyles() {
  return (
    <style>
      {`
        :root {
            --primary-color: #0056b3;
            --primary-dark: #003366;
            --primary-light: #007bff;
            --accent-color: #00a0e9;
            --text-light: #ffffff;
            --text-dark: #2d3748;
            --text-muted: #718096;
            --danger: #e53e3e;
            --success: #38a169;
            --warning: #f6ad55;
            --info: #4299e1;
            --bg-light: #f5f7fa;
            --bg-medium: #e2e8f0;
            --bg-dark: #1a202c;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        
        html, body {
            height: 100%;
            width: 100%;
            overflow-x: hidden;
        }
        
        body {
            background-color: var(--bg-light);
            color: var(--text-dark);
            min-height: 100vh;
        }
        
        /* Login Styles */
        .login-page {
            min-height: 100vh;
            height: 100vh;
            display: flex;
            align-items: stretch;
            background-color: var(--bg-light);
            overflow: hidden;
        }
        
        .login-content {
            display: flex;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }
        
        .login-left {
            flex: 3;
            background: linear-gradient(135deg, #0056b3 0%, #00a0e9 100%);
            color: var(--text-light);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            position: relative;
            overflow: hidden;
        }
        
        .login-left::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            opacity: 0.3;
        }
        
        /* Logo container styles */
        .logo-container {
            margin-bottom: 1.5rem;
        }
        
        .brand-logo-placeholder {
            font-size: 2.5rem;
            font-weight: bold;
            color: white;
            background: rgba(255, 255, 255, 0.2);
            padding: 1rem 2rem;
            border-radius: 10px;
            display: inline-block;
        }
        
        .brand-info {
            position: relative;
            z-index: 2;
            max-width: 700px;
            margin: 0 auto;
        }
        
        .brand-info h2 {
            font-size: 1.8rem;
            font-weight: 500;
            margin-bottom: 1.5rem;
            opacity: 0.9;
        }
        
        .brand-info p {
            font-size: 1.1rem;
            margin-bottom: 3rem;
            opacity: 0.8;
            line-height: 1.6;
        }
        
        .feature-list {
            margin-top: 3rem;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .feature-icon {
            background-color: rgba(255, 255, 255, 0.2);
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
        }
        
        .feature-text h3 {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        
        .feature-text p {
            font-size: 0.95rem;
            opacity: 0.8;
            margin: 0;
        }
        
        .login-right {
            flex: 1;
            background-color: var(--text-light);
            display: flex;
            align-items: flex-start;
            justify-content: center;
            min-width: 320px;
            max-width: 450px;
            box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 2;
            overflow-y: auto;
            max-height: 100vh;
        }
        
        .login-form-container {
            width: 100%;
            max-width: 350px;
            padding: 1.5rem;
            padding-bottom: 3rem;
        }
        
        .login-form-container h2 {
            font-size: 1.75rem;
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: var(--text-muted);
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: var(--text-dark);
        }
        
        .input-with-icon {
            position: relative;
        }
        
        .input-with-icon i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }
        
        .input-with-icon input,
        .input-with-icon select {
            width: 100%;
            padding: 0.8rem 1rem 0.8rem 2.8rem;
            border: 1px solid var(--bg-medium);
            border-radius: 8px;
            font-size: 1rem;
            background-color: var(--bg-light);
            transition: all 0.3s;
            color: #000000 !important;
        }
        
        .input-with-icon input::placeholder,
        .input-with-icon select::placeholder {
            color: #718096;
        }
        
        .input-with-icon input:focus,
        .input-with-icon select:focus {
            outline: none;
            border-color: var(--primary-color);
            background-color: var(--text-light);
            box-shadow: 0 0 0 3px rgba(0, 86, 179, 0.1);
            color: #000000 !important;
        }
        
        .role-select {
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23718096' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 16px;
        }

        .password-hint {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 5px;
            display: block;
        }
        
        .btn-sign-in {
            width: 100%;
            padding: 0.8rem;
            background-color: var(--primary-color);
            color: var(--text-light);
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 1rem;
        }
        
        .btn-sign-in:hover:not(:disabled) {
            background-color: var(--primary-dark);
        }
        
        .btn-sign-in:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .login-footer {
            margin-top: 2rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        .register-link {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
        }
        
        .register-link:hover {
            text-decoration: underline;
        }
        
        .error-message {
            background-color: rgba(229, 62, 62, 0.1);
            color: var(--danger);
            padding: 0.8rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }

        .success-message {
            background-color: rgba(56, 161, 105, 0.1);
            color: var(--success);
            padding: 0.8rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }
        
        /* Responsive Design */
        @media (max-width: 1400px) {
            .login-left {
                flex: 2.5;
                justify-content: center;
            }
            
            .login-right {
                flex: 1;
                min-width: 300px;
                max-width: 350px;
            }
            
            .brand-info {
                max-width: 600px;
            }
        }
        
        @media (max-width: 1200px) {
            .login-left {
                flex: 2;
                justify-content: center;
            }
            
            .login-right {
                flex: 1;
                min-width: 280px;
                max-width: 320px;
            }
            
            .brand-info {
                max-width: 500px;
            }
            
            .login-form-container {
                max-width: 280px;
                padding: 1.25rem;
            }
        }
        
        @media (max-width: 992px) {
            .login-content {
                flex-direction: column;
                height: auto;
                overflow: visible;
            }
            
            .login-page {
                height: auto;
                min-height: 100vh;
                overflow: visible;
            }
            
            .login-left, .login-right {
                flex: none;
                width: 100%;
                min-width: unset;
                max-width: unset;
                max-height: unset;
                overflow-y: visible;
            }
            
            .login-left {
                padding: 2rem;
                min-height: 300px;
                justify-content: center;
            }
            
            .login-right {
                box-shadow: none;
                border-top: 1px solid var(--bg-medium);
                padding: 1rem 0;
            }
            
            .login-form-container {
                padding: 2rem;
                max-width: 400px;
            }
        }
        
        @media (max-width: 768px) {
            .brand-info h2 {
                font-size: 1.3rem;
            }
            
            .brand-info p {
                font-size: 1rem;
            }
            
            .login-form-container {
                padding: 1.5rem;
            }
        }
        
        @media (max-width: 576px) {
            .login-left {
                padding: 1.5rem;
            }
            
            .brand-logo-placeholder {
                font-size: 2rem;
                padding: 0.75rem 1.5rem;
            }
            
            .brand-info h2 {
                font-size: 1.1rem;
            }
            
            .feature-icon {
                width: 40px;
                height: 40px;
                font-size: 1.2rem;
            }
            
            .feature-text h3 {
                font-size: 1rem;
            }
            
            .feature-text p {
                font-size: 0.85rem;
            }
        }
      `}
    </style>
  );
}

export default RegisterUser;