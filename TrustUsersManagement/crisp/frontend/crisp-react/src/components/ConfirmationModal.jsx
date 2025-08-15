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
  actionType = 'default' // 'activate', 'deactivate', 'delete', 'default'
}) => {

  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  const handleCancel = () => {
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
          >
            ×
          </button>
        </div>
        
        <div className="confirmation-modal-body">
          <p>{message}</p>
        </div>
        
        <div className="confirmation-modal-footer">
          <button 
            className="btn btn-secondary" 
            onClick={handleCancel}
          >
            {cancelText}
          </button>
          <button 
            className={getButtonClass()}
            onClick={handleConfirm}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;