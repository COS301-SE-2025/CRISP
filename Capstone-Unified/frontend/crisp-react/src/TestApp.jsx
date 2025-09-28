import React from 'react';

// Minimal test app to check performance
function TestApp() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Performance Test App</h1>
      <p>If this loads fast, the issue is in the main App.jsx</p>
      <p>If this is slow too, the issue is elsewhere</p>
    </div>
  );
}

export default TestApp;