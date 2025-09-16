import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Settings from './Settings'

// Mock the api module
vi.mock('../../api.js', () => ({
  getCurrentUser: vi.fn()
}))

import * as api from '../../api.js'

describe('Settings Component', () => {
  beforeEach(() => {
    localStorage.setItem('crisp_auth_token', 'test-token')
  })

  test('renders settings tabs correctly', async () => {
    api.getCurrentUser.mockReturnValue({
      username: 'testuser',
      role: 'admin'
    })

    // Mock profile API call
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          user: {
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            username: 'johndoe'
          }
        }
      })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    expect(screen.getByText('Manage your account settings and preferences')).toBeInTheDocument()
    expect(screen.getByText('Profile Settings')).toBeInTheDocument()
    expect(screen.getByText('Password')).toBeInTheDocument()
    expect(screen.getByText('Notifications')).toBeInTheDocument()
  })

  test('loads and displays profile data', async () => {
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
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            username: 'johndoe'
          }
        }
      })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('John')).toBeInTheDocument()
    })

    expect(screen.getByDisplayValue('Doe')).toBeInTheDocument()
    expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument()
  })

  test('switches to password tab and shows password fields', async () => {
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
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com'
          }
        }
      })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    // Click password tab
    const passwordTab = screen.getByText('Password')
    await user.click(passwordTab)

    expect(screen.getByText('Change Password')).toBeInTheDocument()
    expect(screen.getByText('Current Password')).toBeInTheDocument()
    expect(screen.getByText('New Password')).toBeInTheDocument()
    expect(screen.getByText('Confirm New Password')).toBeInTheDocument()
  })

  test('switches to notifications tab and shows notification settings', async () => {
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
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com'
          }
        }
      })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    // Click notifications tab
    const notificationsTab = screen.getByText('Notifications')
    await user.click(notificationsTab)

    expect(screen.getByText('Notification Preferences')).toBeInTheDocument()
    expect(screen.getByText('Email Notifications')).toBeInTheDocument()
    expect(screen.getByText('Trust Relationship Notifications')).toBeInTheDocument()
    expect(screen.getByText('Security Alerts')).toBeInTheDocument()
  })

  test('saves profile changes successfully', async () => {
    const user = userEvent.setup()
    api.getCurrentUser.mockReturnValue({
      username: 'testuser',
      role: 'admin'
    })

    // Initial load
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: {
            user: {
              first_name: 'John',
              last_name: 'Doe',
              email: 'john@example.com'
            }
          }
        })
      })
      // Profile update
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: {
            user: {
              first_name: 'Jane',
              last_name: 'Smith',
              email: 'jane@example.com'
            }
          }
        })
      })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('John')).toBeInTheDocument()
    })

    // Change first name
    const firstNameInput = screen.getByDisplayValue('John')
    await user.clear(firstNameInput)
    await user.type(firstNameInput, 'Jane')

    // Change last name
    const lastNameInput = screen.getByDisplayValue('Doe')
    await user.clear(lastNameInput)
    await user.type(lastNameInput, 'Smith')

    // Save profile
    const saveButton = screen.getByText('Save Profile Changes')
    await user.click(saveButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Update Profile')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Update Profile')
    await user.click(confirmButton)

    // Verify API call
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/auth/profile/', {
        method: 'PUT',
        headers: {
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: 'Jane',
          last_name: 'Smith',
          email: 'john@example.com'
        })
      })
    })
  })

  test('validates password change form', async () => {
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
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com'
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

    // Fill in password fields with mismatched passwords
    const currentPasswordInput = screen.getByLabelText('Current Password')
    const newPasswordInput = screen.getByLabelText('New Password')
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password')

    await user.type(currentPasswordInput, 'oldpassword')
    await user.type(newPasswordInput, 'newpassword123')
    await user.type(confirmPasswordInput, 'differentpassword')

    // Try to save
    const changePasswordButton = screen.getByText('Change Password')
    await user.click(changePasswordButton)

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText('New passwords do not match')).toBeInTheDocument()
    })
  })

  test('validates password length', async () => {
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
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com'
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

    // Fill in password fields with short password
    const currentPasswordInput = screen.getByLabelText('Current Password')
    const newPasswordInput = screen.getByLabelText('New Password')
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password')

    await user.type(currentPasswordInput, 'oldpassword')
    await user.type(newPasswordInput, '123')
    await user.type(confirmPasswordInput, '123')

    // Try to save
    const changePasswordButton = screen.getByText('Change Password')
    await user.click(changePasswordButton)

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText('New password must be at least 8 characters long')).toBeInTheDocument()
    })
  })

  test('saves notification preferences', async () => {
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
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com'
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

    // Toggle email notifications
    const emailNotificationsCheckbox = screen.getByRole('checkbox', { name: /email notifications/i })
    await user.click(emailNotificationsCheckbox)

    // Save settings
    const saveButton = screen.getByText('Save Notification Settings')
    await user.click(saveButton)

    // Confirm in modal
    await waitFor(() => {
      expect(screen.getByText('Update Notification Settings')).toBeInTheDocument()
    })

    const confirmButton = screen.getByText('Update Settings')
    await user.click(confirmButton)

    // Check localStorage
    await waitFor(() => {
      const savedSettings = JSON.parse(localStorage.getItem('crisp_notification_settings'))
      expect(savedSettings.email_notifications).toBe(false) // Was toggled off
    })
  })

  test('does not render when active prop is false', () => {
    render(<Settings active={false} />)
    expect(screen.queryByText('Settings')).not.toBeInTheDocument()
  })
})