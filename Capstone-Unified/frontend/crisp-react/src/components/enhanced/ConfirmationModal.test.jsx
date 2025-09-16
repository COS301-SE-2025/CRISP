import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ConfirmationModal from './ConfirmationModal'

describe('ConfirmationModal Component', () => {
  const mockOnClose = vi.fn()
  const mockOnConfirm = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('does not render when isOpen is false', () => {
    render(
      <ConfirmationModal
        isOpen={false}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    expect(screen.queryByText('Test Title')).not.toBeInTheDocument()
  })

  test('renders modal content when isOpen is true', () => {
    render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('Test message')).toBeInTheDocument()
    expect(screen.getByText('Confirm')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
  })

  test('renders custom button text when provided', () => {
    render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
        confirmText="Delete Item"
        cancelText="Keep Item"
      />
    )

    expect(screen.getByText('Delete Item')).toBeInTheDocument()
    expect(screen.getByText('Keep Item')).toBeInTheDocument()
  })

  test('calls onConfirm and onClose when confirm button is clicked', async () => {
    const user = userEvent.setup()
    
    render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    const confirmButton = screen.getByText('Confirm')
    await user.click(confirmButton)

    expect(mockOnConfirm).toHaveBeenCalledTimes(1)
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  test('calls onClose when cancel button is clicked', async () => {
    const user = userEvent.setup()
    
    render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    const cancelButton = screen.getByText('Cancel')
    await user.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
    expect(mockOnConfirm).not.toHaveBeenCalled()
  })

  test('calls onClose when close button (×) is clicked', async () => {
    const user = userEvent.setup()
    
    render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    const closeButton = screen.getByText('×')
    await user.click(closeButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
    expect(mockOnConfirm).not.toHaveBeenCalled()
  })

  test('calls onClose when overlay is clicked', async () => {
    const user = userEvent.setup()
    
    render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    const overlay = document.querySelector('.confirmation-modal-overlay')
    await user.click(overlay)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
    expect(mockOnConfirm).not.toHaveBeenCalled()
  })

  test('does not close when modal content is clicked', async () => {
    const user = userEvent.setup()
    
    render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    const modalContent = document.querySelector('.confirmation-modal')
    await user.click(modalContent)

    expect(mockOnClose).not.toHaveBeenCalled()
    expect(mockOnConfirm).not.toHaveBeenCalled()
  })

  test('applies correct button class for different action types', () => {
    const { rerender } = render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
        actionType="activate"
      />
    )

    let confirmButton = screen.getByText('Confirm')
    expect(confirmButton).toHaveClass('confirmation-btn-green')

    rerender(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
        actionType="delete"
      />
    )

    confirmButton = screen.getByText('Confirm')
    expect(confirmButton).toHaveClass('confirmation-btn-red')

    rerender(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
        isDestructive={true}
      />
    )

    confirmButton = screen.getByText('Confirm')
    expect(confirmButton).toHaveClass('btn-danger')
  })

  test('handles escape key press', () => {
    render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' })

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  test('prevents body scroll when modal is open', () => {
    const originalOverflow = document.body.style.overflow
    
    const { unmount } = render(
      <ConfirmationModal
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    expect(document.body.style.overflow).toBe('hidden')

    unmount()

    expect(document.body.style.overflow).toBe('unset')
    
    // Restore original
    document.body.style.overflow = originalOverflow
  })

  test('does not prevent body scroll when modal is closed', () => {
    const originalOverflow = document.body.style.overflow
    
    render(
      <ConfirmationModal
        isOpen={false}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Test Title"
        message="Test message"
      />
    )

    expect(document.body.style.overflow).toBe(originalOverflow)
  })

  test('renders different action types with correct styling', () => {
    const actionTypes = [
      { type: 'activate', expectedClass: 'confirmation-btn-green' },
      { type: 'reactivate', expectedClass: 'confirmation-btn-green' },
      { type: 'deactivate', expectedClass: 'confirmation-btn-red' },
      { type: 'delete', expectedClass: 'confirmation-btn-red' }
    ]

    actionTypes.forEach(({ type, expectedClass }) => {
      const { unmount } = render(
        <ConfirmationModal
          isOpen={true}
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
          title="Test Title"
          message="Test message"
          actionType={type}
        />
      )

      const confirmButton = screen.getByText('Confirm')
      expect(confirmButton).toHaveClass(expectedClass)

      unmount()
    })
  })
})