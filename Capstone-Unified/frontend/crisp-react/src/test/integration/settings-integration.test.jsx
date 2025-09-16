import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AdminSettings from '../../components/enhanced/AdminSettings'
import Settings from '../../components/enhanced/Settings'

// Mock the api module for getCurrentUser
vi.mock('../../api.js', () => ({
  getCurrentUser: vi.fn()
}))

import * as api from '../../api.js'

describe('Settings Integration Tests', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    localStorage.setItem('crisp_auth_token', 'test-token')
  })

  test('admin settings integrates with localStorage correctly', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Admin Settings')).toBeInTheDocument()
    })

    // Change system settings
    const systemNameInput = screen.getByDisplayValue('CRISP Trust Management')
    await user.clear(systemNameInput)
    await user.type(systemNameInput, 'Integration Test System')

    const maxTrustInput = screen.getByDisplayValue('100')
    await user.clear(maxTrustInput)
    await user.type(maxTrustInput, '150')

    // Save settings
    const saveButton = screen.getByText('Save System Settings')
    await user.click(saveButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Update System Settings')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Update Settings')
    await user.click(confirmButton)

    // Wait for save completion
    await waitFor(() => {
      expect(screen.queryByText('Update System Settings')).not.toBeInTheDocument()
    }, { timeout: 5000 })

    // Verify localStorage was updated
    const savedSettings = JSON.parse(localStorage.getItem('crisp_system_settings'))
    expect(savedSettings).toBeTruthy()
    expect(savedSettings.system_name).toBe('Integration Test System')
    expect(savedSettings.max_trust_relationships).toBe(150)

    // Reload component to test persistence
    const { unmount, rerender } = render(<AdminSettings />)
    unmount()
    
    rerender(<AdminSettings />)
    
    await waitFor(() => {
      expect(screen.getByDisplayValue('Integration Test System')).toBeInTheDocument()
    })
    expect(screen.getByDisplayValue('150')).toBeInTheDocument()
  })

  test('user settings profile integration with real API calls', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      username: 'testuser',
      role: 'admin'
    })

    // Mock successful profile fetch
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          user: {
            first_name: 'Integration',
            last_name: 'Test',
            email: 'integration@test.com',
            username: 'testuser'
          }
        }
      })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Integration')).toBeInTheDocument()
    })

    // Test profile update
    const firstNameInput = screen.getByDisplayValue('Integration')
    await user.clear(firstNameInput)
    await user.type(firstNameInput, 'Updated Integration')

    // Mock successful profile update
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          user: {
            first_name: 'Updated Integration',
            last_name: 'Test',
            email: 'integration@test.com',
            username: 'testuser'
          }
        }
      })
    })

    const saveButton = screen.getByText('Save Profile Changes')
    await user.click(saveButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Update Profile')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Update Profile')
    await user.click(confirmButton)

    // Verify API was called correctly
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/auth/profile/', {
        method: 'PUT',
        headers: {
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: 'Updated Integration',
          last_name: 'Test',
          email: 'integration@test.com'
        })
      })
    })
  })

  test('password change integration with API', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      username: 'testuser',
      role: 'admin'
    })

    // Mock initial profile fetch
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          user: {
            first_name: 'Test',
            last_name: 'User',
            email: 'test@example.com'
          }
        }
      })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    // Switch to password tab
    const passwordTab = screen.getByText('Password')
    await user.click(passwordTab)

    // Fill in password form
    const currentPasswordInput = screen.getByLabelText('Current Password')
    const newPasswordInput = screen.getByLabelText('New Password')
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password')

    await user.type(currentPasswordInput, 'currentpass123')
    await user.type(newPasswordInput, 'newpassword456')
    await user.type(confirmPasswordInput, 'newpassword456')

    // Mock successful password change
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        message: 'Password changed successfully'
      })
    })

    const changePasswordButton = screen.getByText('Change Password')
    await user.click(changePasswordButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Change Password')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Change Password')
    await user.click(confirmButton)

    // Verify API call
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/auth/change-password/', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: 'currentpass123',
          new_password: 'newpassword456'
        })
      })
    })

    // Should clear password fields after successful change
    await waitFor(() => {
      expect(currentPasswordInput.value).toBe('')
      expect(newPasswordInput.value).toBe('')
      expect(confirmPasswordInput.value).toBe('')
    })
  })

  test('notification settings persist in localStorage', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      username: 'testuser',
      role: 'admin'
    })

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          user: {
            first_name: 'Test',
            last_name: 'User',
            email: 'test@example.com'
          }
        }
      })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    // Switch to notifications tab
    const notificationsTab = screen.getByText('Notifications')
    await user.click(notificationsTab)

    // Toggle some notification settings
    const emailNotificationsCheckbox = screen.getByRole('checkbox', { name: /email notifications/i })
    const trustNotificationsCheckbox = screen.getByRole('checkbox', { name: /trust relationship notifications/i })

    await user.click(emailNotificationsCheckbox) // Turn off
    await user.click(trustNotificationsCheckbox) // Turn off

    // Save settings
    const saveButton = screen.getByText('Save Notification Settings')
    await user.click(saveButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Update Notification Settings')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Update Settings')
    await user.click(confirmButton)

    // Verify localStorage persistence
    await waitFor(() => {
      const savedSettings = JSON.parse(localStorage.getItem('crisp_notification_settings'))
      expect(savedSettings.email_notifications).toBe(false)
      expect(savedSettings.trust_notifications).toBe(false)
      expect(savedSettings.security_alerts).toBe(true) // Should remain true
    })

    // Reload component to test persistence
    const { unmount } = render(<Settings />)
    unmount()

    // Re-render and check persistence
    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    const notificationsTab2 = screen.getByText('Notifications')
    await user.click(notificationsTab2)

    // Checkboxes should maintain their state
    await waitFor(() => {
      const emailCheckbox = screen.getByRole('checkbox', { name: /email notifications/i })
      const trustCheckbox = screen.getByRole('checkbox', { name: /trust relationship notifications/i })
      const securityCheckbox = screen.getByRole('checkbox', { name: /security alerts/i })

      expect(emailCheckbox.checked).toBe(false)
      expect(trustCheckbox.checked).toBe(false)
      expect(securityCheckbox.checked).toBe(true)
    })
  })

  test('admin settings handles API errors gracefully', async () => {
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByText('Admin Settings')).toBeInTheDocument()
    })

    // Component should render without crashing even if localStorage operations fail
    const originalSetItem = localStorage.setItem
    localStorage.setItem = vi.fn().mockImplementation(() => {
      throw new Error('Storage error')
    })

    // Try to save settings - should handle error gracefully
    const saveButton = screen.getByText('Save System Settings')
    fireEvent.click(saveButton)

    // Should not crash the application
    expect(screen.getByText('Admin Settings')).toBeInTheDocument()

    // Restore original localStorage
    localStorage.setItem = originalSetItem
  })

  test('cross-component data sharing works correctly', async () => {
    api.getCurrentUser.mockReturnValue({
      role: 'BlueVisionAdmin',
      username: 'admin'
    })

    // Set some admin settings
    localStorage.setItem('crisp_system_settings', JSON.stringify({
      system_name: 'Shared System',
      maintenance_mode: true
    }))

    // Render AdminSettings
    const { unmount } = render(<AdminSettings />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Shared System')).toBeInTheDocument()
    })

    unmount()

    // The settings should persist for other components or future renders
    const savedSettings = JSON.parse(localStorage.getItem('crisp_system_settings'))
    expect(savedSettings.system_name).toBe('Shared System')
    expect(savedSettings.maintenance_mode).toBe(true)
  })
})