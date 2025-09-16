import { render, screen } from '@testing-library/react'
import LoadingSpinner from './LoadingSpinner'

describe('LoadingSpinner Component', () => {
  afterEach(() => {
    // Clean up any overlay elements
    const overlay = document.getElementById('bluevision-loading-overlay')
    if (overlay) {
      document.body.removeChild(overlay)
    }
  })

  test('renders inline spinner by default', () => {
    render(<LoadingSpinner />)
    
    const spinner = document.querySelector('.bluevision-loader')
    expect(spinner).toBeInTheDocument()
  })

  test('renders different sizes correctly', () => {
    const sizes = ['small', 'medium', 'large']
    
    sizes.forEach(size => {
      const { unmount } = render(<LoadingSpinner size={size} />)
      
      const spinner = document.querySelector('.bluevision-loader')
      expect(spinner).toBeInTheDocument()
      
      unmount()
    })
  })

  test('renders fullscreen overlay when fullscreen prop is true', () => {
    render(<LoadingSpinner fullscreen={true} />)
    
    // Should create overlay element in DOM
    const overlay = document.getElementById('bluevision-loading-overlay')
    expect(overlay).toBeInTheDocument()
    expect(overlay.style.position).toBe('fixed')
    expect(overlay.style.zIndex).toBe('2147483647')
  })

  test('removes fullscreen overlay when component unmounts', () => {
    const { unmount } = render(<LoadingSpinner fullscreen={true} />)
    
    // Overlay should exist
    let overlay = document.getElementById('bluevision-loading-overlay')
    expect(overlay).toBeInTheDocument()
    
    // Unmount component
    unmount()
    
    // Overlay should be removed
    overlay = document.getElementById('bluevision-loading-overlay')
    expect(overlay).not.toBeInTheDocument()
  })

  test('does not render inline content when fullscreen is true', () => {
    render(<LoadingSpinner fullscreen={true} />)
    
    // Should not render inline spinner content
    const inlineSpinner = screen.queryByText((content, element) => {
      return element?.classList?.contains('bluevision-rotated') || false
    })
    expect(inlineSpinner).not.toBeInTheDocument()
  })

  test('renders inline content when fullscreen is false', () => {
    render(<LoadingSpinner fullscreen={false} />)
    
    const spinner = document.querySelector('.bluevision-loader')
    expect(spinner).toBeInTheDocument()
    
    // Should not create overlay
    const overlay = document.getElementById('bluevision-loading-overlay')
    expect(overlay).not.toBeInTheDocument()
  })

  test('fullscreen overlay contains correct content', () => {
    render(<LoadingSpinner fullscreen={true} size="large" />)
    
    const overlay = document.getElementById('bluevision-loading-overlay')
    expect(overlay).toBeInTheDocument()
    
    // Check for spinner inside overlay
    const spinnerInOverlay = overlay.querySelector('.bluevision-loader')
    expect(spinnerInOverlay).toBeInTheDocument()
    
    // Check for rotated wrapper
    const rotatedWrapper = overlay.querySelector('.bluevision-rotated')
    expect(rotatedWrapper).toBeInTheDocument()
  })

  test('prevents multiple fullscreen overlays', () => {
    // Render first spinner
    const { unmount: unmount1 } = render(<LoadingSpinner fullscreen={true} />)
    
    let overlays = document.querySelectorAll('#bluevision-loading-overlay')
    expect(overlays).toHaveLength(1)
    
    // Render second spinner while first is still active
    const { unmount: unmount2 } = render(<LoadingSpinner fullscreen={true} />)
    
    // Should still only have one overlay
    overlays = document.querySelectorAll('#bluevision-loading-overlay')
    expect(overlays).toHaveLength(1)
    
    unmount1()
    unmount2()
  })

  test('applies correct styles for different sizes in fullscreen mode', () => {
    const sizeMap = {
      small: '32px',
      medium: '48px', 
      large: '64px'
    }
    
    Object.entries(sizeMap).forEach(([size, expectedSize]) => {
      const { unmount } = render(<LoadingSpinner fullscreen={true} size={size} />)
      
      const overlay = document.getElementById('bluevision-loading-overlay')
      const spinner = overlay.querySelector('.bluevision-loader')
      
      // Check that the size is applied in the style content
      const styleElement = overlay.querySelector('style')
      expect(styleElement.textContent).toContain(`width: ${expectedSize}`)
      expect(styleElement.textContent).toContain(`height: ${expectedSize}`)
      
      unmount()
    })
  })

  test('overlay has correct CSS properties', () => {
    render(<LoadingSpinner fullscreen={true} />)
    
    const overlay = document.getElementById('bluevision-loading-overlay')
    const styles = overlay.style
    
    expect(styles.position).toBe('fixed')
    expect(styles.top).toBe('0')
    expect(styles.left).toBe('0')
    expect(styles.width).toBe('100vw')
    expect(styles.height).toBe('100vh')
    expect(styles.backgroundColor).toBe('white')
    expect(styles.display).toBe('flex')
    expect(styles.justifyContent).toBe('center')
    expect(styles.alignItems).toBe('center')
    expect(styles.zIndex).toBe('2147483647')
  })

  test('handles size prop changes in fullscreen mode', () => {
    const { rerender } = render(<LoadingSpinner fullscreen={true} size="small" />)
    
    let overlay = document.getElementById('bluevision-loading-overlay')
    let styleContent = overlay.querySelector('style').textContent
    expect(styleContent).toContain('width: 32px')
    
    // Change size
    rerender(<LoadingSpinner fullscreen={true} size="large" />)
    
    overlay = document.getElementById('bluevision-loading-overlay')
    styleContent = overlay.querySelector('style').textContent
    expect(styleContent).toContain('width: 64px')
  })

  test('cleanup works correctly when switching between fullscreen and inline', () => {
    const { rerender } = render(<LoadingSpinner fullscreen={true} />)
    
    // Should have overlay
    let overlay = document.getElementById('bluevision-loading-overlay')
    expect(overlay).toBeInTheDocument()
    
    // Switch to inline
    rerender(<LoadingSpinner fullscreen={false} />)
    
    // Overlay should be removed
    overlay = document.getElementById('bluevision-loading-overlay')
    expect(overlay).not.toBeInTheDocument()
    
    // Should have inline spinner
    const inlineSpinner = document.querySelector('.bluevision-loader')
    expect(inlineSpinner).toBeInTheDocument()
  })
})