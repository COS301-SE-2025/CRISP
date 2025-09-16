import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AdminSettings from './AdminSettings'

// Mock the api module
vi.mock('../../api.js', () => ({
  getCurrentUser: vi.fn()
}))

import * as api from '../../api.js'

describe('AdminSettings Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  test('renders admin settings for BlueVisionAdmin users', async () => {
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Admin Settings')).toBeInTheDocument()
    })

    expect(screen.getByText('System administration and configuration')).toBeInTheDocument()
    expect(screen.getByText('System Settings')).toBeInTheDocument()
    expect(screen.getByText('Security')).toBeInTheDocument()
    expect(screen.getByText('Trust Management')).toBeInTheDocument()
    expect(screen.getByText('Audit Logs')).toBeInTheDocument()
  })

  test('renders admin settings for admin users', async () => {
    api.getCurrentUser.mockReturnValue({
      role: 'admin',
      username: 'admin'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Admin Settings')).toBeInTheDocument()
    })
  })

  test('denies access to non-admin users', async () => {
    api.getCurrentUser.mockReturnValue({
      role: 'viewer',
      username: 'user'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Access Denied')).toBeInTheDocument()
    })

    expect(screen.getByText('Administrator privileges are required to access this page.')).toBeInTheDocument()
  })

  test('switches between tabs correctly', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Admin Settings')).toBeInTheDocument()
    })

    // Initially on System Settings tab
    expect(screen.getByText('System Name')).toBeInTheDocument()

    // Click Security tab
    const securityTab = screen.getByText('Security')
    await user.click(securityTab)

    expect(screen.getByText('Password Min Length')).toBeInTheDocument()
    expect(screen.getByText('Session Timeout (Minutes)')).toBeInTheDocument()

    // Click Trust Management tab
    const trustTab = screen.getByText('Trust Management')
    await user.click(trustTab)

    expect(screen.getByText('Trust Management Settings')).toBeInTheDocument()
    expect(screen.getByText('Auto-Accept Trust Requests')).toBeInTheDocument()

    // Click Audit Logs tab
    const auditTab = screen.getByText('Audit Logs')
    await user.click(auditTab)

    expect(screen.getByText('Audit Logs Coming Soon')).toBeInTheDocument()
  })

  test('loads saved settings from localStorage', async () => {
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    // Pre-populate localStorage with settings
    localStorage.setItem('crisp_system_settings', JSON.stringify({
      system_name: 'Custom CRISP System',
      maintenance_mode: true,
      registration_enabled: false,
      max_trust_relationships: 50,
      trust_expiry_days: 180
    }))

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Custom CRISP System')).toBeInTheDocument()
    })

    expect(screen.getByDisplayValue('50')).toBeInTheDocument()
    expect(screen.getByDisplayValue('180')).toBeInTheDocument()
  })

  test('saves system settings to localStorage', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Admin Settings')).toBeInTheDocument()
    })

    // Change system name
    const systemNameInput = screen.getByDisplayValue('CRISP Trust Management')
    await user.clear(systemNameInput)
    await user.type(systemNameInput, 'Updated CRISP System')

    // Change max trust relationships
    const maxTrustInput = screen.getByDisplayValue('100')
    await user.clear(maxTrustInput)
    await user.type(maxTrustInput, '200')

    // Save settings
    const saveButton = screen.getByText('Save System Settings')
    await user.click(saveButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Update System Settings')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Update Settings')
    await user.click(confirmButton)

    // Check localStorage
    await waitFor(() => {
      const savedSettings = JSON.parse(localStorage.getItem('crisp_system_settings'))
      expect(savedSettings.system_name).toBe('Updated CRISP System')
      expect(savedSettings.max_trust_relationships).toBe(200)
    })
  })

  test('saves security settings to localStorage', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Admin Settings')).toBeInTheDocument()
    })

    // Switch to Security tab
    const securityTab = screen.getByText('Security')
    await user.click(securityTab)

    // Change password min length
    const passwordLengthInput = screen.getByDisplayValue('8')
    await user.clear(passwordLengthInput)
    await user.type(passwordLengthInput, '12')

    // Toggle password requirements
    const uppercaseCheckbox = screen.getByRole('checkbox', { name: /require uppercase letters/i })
    await user.click(uppercaseCheckbox)

    // Save settings
    const saveButton = screen.getByText('Save Security Settings')
    await user.click(saveButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Update Security Settings')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Update Settings')
    await user.click(confirmButton)

    // Check localStorage
    await waitFor(() => {
      const savedSettings = JSON.parse(localStorage.getItem('crisp_security_settings'))
      expect(savedSettings.password_min_length).toBe(12)
      expect(savedSettings.password_require_uppercase).toBe(false) // Was toggled off
    })
  })

  test('saves trust settings to localStorage', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Admin Settings')).toBeInTheDocument()
    })

    // Switch to Trust Management tab
    const trustTab = screen.getByText('Trust Management')
    await user.click(trustTab)

    // Toggle trust decay
    const trustDecayCheckbox = screen.getByRole('checkbox', { name: /trust decay enabled/i })
    await user.click(trustDecayCheckbox)

    // Trust decay rate input should now be visible
    await waitFor(() => {
      expect(screen.getByText('Trust Decay Rate (0.01 - 1.0)')).toBeInTheDocument()
    })

    const decayRateInput = screen.getByDisplayValue('0.1')
    await user.clear(decayRateInput)
    await user.type(decayRateInput, '0.2')

    // Save settings
    const saveButton = screen.getByText('Save Trust Settings')
    await user.click(saveButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Update Trust Settings')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Update Settings')
    await user.click(confirmButton)

    // Check localStorage
    await waitFor(() => {
      const savedSettings = JSON.parse(localStorage.getItem('crisp_trust_settings'))
      expect(savedSettings.trust_decay_enabled).toBe(true)
      expect(savedSettings.trust_decay_rate).toBe(0.2)
    })
  })

  test('does not render when active prop is false', () => {
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    render(<AdminSettings active={false} />)
    expect(screen.queryByText('Admin Settings')).not.toBeInTheDocument()
  })

  test('handles null user gracefully', async () => {
    api.getCurrentUser.mockReturnValue(null)

    render(<AdminSettings />)

    // Should not crash and should show loading state
    expect(screen.queryByText('Access Denied')).not.toBeInTheDocument()
  })
})