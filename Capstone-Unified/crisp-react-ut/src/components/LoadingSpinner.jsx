import React, { useEffect } from 'react';

// Global loading overlay manager
class LoadingOverlay {
  static overlayElement = null;
  static isActive = false;

  static show(size = 'medium') {
    if (this.isActive) return;
    
    this.isActive = true;
    
    // Create overlay element
    this.overlayElement = document.createElement('div');
    this.overlayElement.id = 'bluevision-loading-overlay';
    this.overlayElement.style.cssText = `
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      background-color: white !important;
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      z-index: 2147483647 !important;
      margin: 0 !important;
      padding: 0 !important;
      pointer-events: all !important;
    `;

    const sizeMap = {
      small: '32px',
      medium: '48px',
      large: '64px'
    };

    // Add spinner HTML
    this.overlayElement.innerHTML = `
      <style>
        .bluevision-loader {
          transform-style: preserve-3d;
          perspective: 1000px;
          border-radius: 50%;
          width: ${sizeMap[size]};
          height: ${sizeMap[size]};
          color: #FF3D00;
          position: relative;
          animation: spinDiagonal 2s linear infinite;
        }

        .bluevision-loader:before,
        .bluevision-loader:after {
          content: '';
          display: block;
          position: absolute;
          top: 0;
          left: 0;
          width: inherit;
          height: inherit;
          border-radius: 50%;
          transform: rotateX(70deg);
          animation: 1s spin linear infinite;
        }

        .bluevision-loader:after {
          color: #2196f3;
          transform: rotateY(70deg);
          animation-delay: .4s;
        }

        @keyframes spin {
          0%, 100% {
            box-shadow: .2em 0px 0 0px currentcolor;
          }
          12% {
            box-shadow: .2em .2em 0 0 currentcolor;
          }
          25% {
            box-shadow: 0 .2em 0 0px currentcolor;
          }
          37% {
            box-shadow: -.2em .2em 0 0 currentcolor;
          }
          50% {
            box-shadow: -.2em 0 0 0 currentcolor;
          }
          62% {
            box-shadow: -.2em -.2em 0 0 currentcolor;
          }
          75% {
            box-shadow: 0px -.2em 0 0 currentcolor;
          }
          87% {
            box-shadow: .2em -.2em 0 0 currentcolor;
          }
        }

        @keyframes spinDiagonal {
          0% {
            transform: rotate3d(1, 1, 0, 0deg);
          }
          100% {
            transform: rotate3d(1, 1, 0, 360deg);
          }
        }
        
        .bluevision-rotated {
          display: inline-block;
          transform: rotate(45deg);
        }
      </style>
      <div class="bluevision-rotated">
        <span class="bluevision-loader"></span>
      </div>
    `;

    // Add to document body
    document.body.appendChild(this.overlayElement);
  }

  static hide() {
    if (!this.isActive) return;
    
    this.isActive = false;
    if (this.overlayElement) {
      document.body.removeChild(this.overlayElement);
      this.overlayElement = null;
    }
  }
}

const LoadingSpinner = ({ 
  size = 'medium', 
  fullscreen = false
}) => {
  useEffect(() => {
    if (fullscreen) {
      LoadingOverlay.show(size);
      return () => LoadingOverlay.hide();
    }
  }, [fullscreen, size]);

  // For fullscreen, don't render anything (handled by overlay)
  if (fullscreen) {
    return null;
  }

  // For inline spinner
  const sizeClasses = {
    small: { width: '32px', height: '32px' },
    medium: { width: '48px', height: '48px' },
    large: { width: '64px', height: '64px' }
  };

  return (
    <>
      <style>
        {`
          .bluevision-loader {
            transform-style: preserve-3d;
            perspective: 1000px;
            border-radius: 50%;
            color: #FF3D00;
            position: relative;
            animation: spinDiagonal 2s linear infinite;
          }

          .bluevision-loader:before,
          .bluevision-loader:after {
            content: '';
            display: block;
            position: absolute;
            top: 0;
            left: 0;
            width: inherit;
            height: inherit;
            border-radius: 50%;
            transform: rotateX(70deg);
            animation: 1s spin linear infinite;
          }

          .bluevision-loader:after {
            color: #2196f3;
            transform: rotateY(70deg);
            animation-delay: .4s;
          }

          @keyframes spin {
            0%, 100% {
              box-shadow: .2em 0px 0 0px currentcolor;
            }
            12% {
              box-shadow: .2em .2em 0 0 currentcolor;
            }
            25% {
              box-shadow: 0 .2em 0 0px currentcolor;
            }
            37% {
              box-shadow: -.2em .2em 0 0 currentcolor;
            }
            50% {
              box-shadow: -.2em 0 0 0 currentcolor;
            }
            62% {
              box-shadow: -.2em -.2em 0 0 currentcolor;
            }
            75% {
              box-shadow: 0px -.2em 0 0 currentcolor;
            }
            87% {
              box-shadow: .2em -.2em 0 0 currentcolor;
            }
          }

          @keyframes spinDiagonal {
            0% {
              transform: rotate3d(1, 1, 0, 0deg);
            }
            100% {
              transform: rotate3d(1, 1, 0, 360deg);
            }
          }
          
          .bluevision-rotated {
            display: inline-block;
            transform: rotate(45deg);
          }
        `}
      </style>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px 20px' }}>
        <div className="bluevision-rotated">
          <span 
            className="bluevision-loader" 
            style={sizeClasses[size]}
          ></span>
        </div>
      </div>
    </>
  );
};

export default LoadingSpinner;