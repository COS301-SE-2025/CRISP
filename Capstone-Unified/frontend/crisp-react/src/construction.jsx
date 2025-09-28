import React from 'react';

function Construction() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #0056b3 0%, #00a0e9 100%)',
      color: 'white',
      textAlign: 'center',
      padding: '2rem'
    }}>
      <div style={{ maxWidth: '600px' }}>
        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🚧</div>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Under Construction</h1>
        <p style={{ fontSize: '1.2rem', marginBottom: '2rem', opacity: 0.9 }}>
          This feature is currently being developed. We're working hard to bring you the best experience possible.
        </p>
        <div style={{ marginBottom: '2rem' }}>
          <h3>Coming Soon:</h3>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '1rem' }}>
            <li style={{ margin: '0.5rem 0' }}>📊 Advanced Analytics Dashboard</li>
            <li style={{ margin: '0.5rem 0' }}>🔐 Enhanced Security Features</li>
            <li style={{ margin: '0.5rem 0' }}>🤝 Improved Collaboration Tools</li>
            <li style={{ margin: '0.5rem 0' }}>📱 Mobile Application</li>
          </ul>
        </div>
        <a 
          href="/" 
          style={{
            display: 'inline-block',
            padding: '1rem 2rem',
            background: 'white',
            color: '#0056b3',
            textDecoration: 'none',
            borderRadius: '8px',
            fontWeight: 'bold',
            transition: 'transform 0.3s ease'
          }}
        >
          Go Back Home
        </a>
      </div>
    </div>
  );
}

export default Construction;