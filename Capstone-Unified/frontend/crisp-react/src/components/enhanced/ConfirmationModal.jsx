import React from 'react';

const ConfirmationModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message, 
  confirmText = 'Confirm', 
  cancelText = 'Cancel',
  confirmButtonClass = 'confirm-btn',
  isDestructive = false,
  actionType = 'default', // 'activate', 'deactivate', 'delete', 'default'
  isLoading = false // Add loading state support
}) => {

  const handleConfirm = () => {
    if (isLoading) return; // Prevent action if already loading
    onConfirm();
    // Don't auto-close if loading, let the parent handle closing after operation completes
    if (!isLoading) {
      onClose();
    }
  };

  const handleCancel = () => {
    if (isLoading) return; // Prevent closing if loading
    onClose();
  };

  // Memoize the button class calculation
  const getButtonClass = React.useCallback(() => {
    const baseClass = 'btn';
    
    if (actionType === 'activate' || actionType === 'reactivate') {
      return `${baseClass} btn-success confirmation-btn-green`;
    }
    
    if (actionType === 'deactivate' || actionType === 'delete') {
      return `${baseClass} btn-danger confirmation-btn-red`;
    }
    
    return `${baseClass} ${isDestructive ? 'btn-danger' : 'btn-primary'}`;
  }, [actionType, isDestructive]);

  // Handle escape key
  React.useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    // Prevent body scroll
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="confirmation-modal-overlay" onClick={handleCancel}>
      <div className="confirmation-modal" onClick={(e) => e.stopPropagation()}>
        <div className="confirmation-modal-header">
          <h3>{title}</h3>
          <button 
            className="confirmation-modal-close" 
            onClick={handleCancel}
            aria-label="Close"
            disabled={isLoading}
          >
            ×
          </button>
        </div>
        
        <div className="confirmation-modal-body">
          {isLoading ? (
            <div style={{textAlign: 'center', padding: '20px'}}>
              <i className="fas fa-spinner fa-spin" style={{fontSize: '32px', color: '#007bff', marginBottom: '15px'}}></i>
              <p style={{fontSize: '16px', margin: '10px 0'}}>Processing...</p>
              <p style={{color: '#6c757d', fontSize: '14px'}}>Please wait, this may take a moment.</p>
            </div>
          ) : (
            <p>{message}</p>
          )}
        </div>
        
        <div className="confirmation-modal-footer">
          <button 
            className="btn btn-secondary" 
            onClick={handleCancel}
            disabled={isLoading}
          >
            {cancelText}
          </button>
          <button 
            className={getButtonClass()}
            onClick={handleConfirm}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin" style={{marginRight: '8px'}}></i>
                Processing...
              </>
            ) : (
              confirmText
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;