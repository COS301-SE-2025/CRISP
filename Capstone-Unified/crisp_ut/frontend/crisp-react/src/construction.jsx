import React from 'react';

function Construction() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      textAlign: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>🚧 Under Construction</h1>
      <p style={{ fontSize: '1.2rem', color: '#666' }}>This feature is coming soon!</p>
      <button 
        onClick={() => window.history.back()}
        style={{
          marginTop: '2rem',
          padding: '10px 20px',
          fontSize: '1rem',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer'
        }}
      >
        Go Back
      </button>
    </div>
  );
}

export default Construction;