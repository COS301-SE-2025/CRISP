import React from 'react';
import { useNotifications } from './NotificationManager';

const NotificationDemo = () => {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications();

  const handleTestSuccess = () => {
    showSuccess('Success!', 'This is a success notification with auto-close');
  };

  const handleTestError = () => {
    showError('Error!', 'This is an error notification that stays longer');
  };

  const handleTestWarning = () => {
    showWarning('Warning!', 'This is a warning notification');
  };

  const handleTestInfo = () => {
    showInfo('Information', 'This is an info notification');
  };

  const handleTestPersistent = () => {
    showError('Persistent Error', 'This notification will not auto-close', { autoCloseDelay: 0 });
  };

  return (
    <div style={{ padding: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
      <button onClick={handleTestSuccess} className="btn btn-success">
        Test Success Toast
      </button>
      <button onClick={handleTestError} className="btn btn-danger">
        Test Error Toast
      </button>
      <button onClick={handleTestWarning} className="btn btn-warning">
        Test Warning Toast
      </button>
      <button onClick={handleTestInfo} className="btn btn-info">
        Test Info Toast
      </button>
      <button onClick={handleTestPersistent} className="btn btn-secondary">
        Test Persistent Toast
      </button>
    </div>
  );
};

export default NotificationDemo;