import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UserProfile from './UserProfile'

describe('UserProfile Component', () => {
  beforeEach(() => {
    // Set up auth token in localStorage
    localStorage.setItem('crisp_auth_token', 'test-token')
  })

  test('renders user profile with loading state initially', () => {
    render(<UserProfile />)
    expect(screen.getByText('Loading profile...')).toBeInTheDocument()
  })

  test('renders profile data when loaded successfully', async () => {
    // Mock successful API response
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          user: {
            first_name: 'John',
            last_name: 'Doe',
            email: 'john.doe@example.com',
            username: 'johndoe',
            role: 'admin',
            organization: { name: 'Test Org' },
            is_active: true,
            created_at: '2024-01-01T00:00:00Z'
          }
        }
      })
    })

    render(<UserProfile />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
    expect(screen.getByText('johndoe')).toBeInTheDocument()
    expect(screen.getByText('admin')).toBeInTheDocument()
    expect(screen.getByText('Test Org')).toBeInTheDocument()
  })

  test('renders error state when API call fails', async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'))

    render(<UserProfile />)

    await waitFor(() => {
      expect(screen.getByText(/Error loading profile/)).toBeInTheDocument()
    })

    expect(screen.getByText('Retry')).toBeInTheDocument()
  })

  test('enters edit mode when edit button is clicked', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          user: {
            first_name: 'John',
            last_name: 'Doe',
            email: 'john.doe@example.com',
            username: 'johndoe',
            role: 'admin',
            organization: { name: 'Test Org' },
            is_active: true,
            created_at: '2024-01-01T00:00:00Z'
          }
        }
      })
    })

    render(<UserProfile />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const editButton = screen.getByText('Edit Profile')
    fireEvent.click(editButton)

    expect(screen.getByDisplayValue('John')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Doe')).toBeInTheDocument()
    expect(screen.getByDisplayValue('john.doe@example.com')).toBeInTheDocument()
    expect(screen.getByText('Save Changes')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
  })

  test('saves profile changes when save button is clicked', async () => {
    const user = userEvent.setup()
    
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
              email: 'john.doe@example.com',
              username: 'johndoe',
              role: 'admin',
              organization: { name: 'Test Org' },
              is_active: true,
              created_at: '2024-01-01T00:00:00Z'
            }
          }
        })
      })
      // Save changes
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: {
            user: {
              first_name: 'Jane',
              last_name: 'Smith',
              email: 'jane.smith@example.com',
              username: 'johndoe',
              role: 'admin',
              organization: { name: 'Test Org' },
              is_active: true,
              created_at: '2024-01-01T00:00:00Z'
            }
          }
        })
      })

    render(<UserProfile />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    // Enter edit mode
    const editButton = screen.getByText('Edit Profile')
    fireEvent.click(editButton)

    // Change first name
    const firstNameInput = screen.getByDisplayValue('John')
    await user.clear(firstNameInput)
    await user.type(firstNameInput, 'Jane')

    // Change last name
    const lastNameInput = screen.getByDisplayValue('Doe')
    await user.clear(lastNameInput)
    await user.type(lastNameInput, 'Smith')

    // Change email
    const emailInput = screen.getByDisplayValue('john.doe@example.com')
    await user.clear(emailInput)
    await user.type(emailInput, 'jane.smith@example.com')

    // Save changes
    const saveButton = screen.getByText('Save Changes')
    fireEvent.click(saveButton)

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
          email: 'jane.smith@example.com'
        })
      })
    })
  })

  test('cancels edit mode when cancel button is clicked', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          user: {
            first_name: 'John',
            last_name: 'Doe',
            email: 'john.doe@example.com',
            username: 'johndoe',
            role: 'admin',
            organization: { name: 'Test Org' },
            is_active: true,
            created_at: '2024-01-01T00:00:00Z'
          }
        }
      })
    })

    render(<UserProfile />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    // Enter edit mode
    const editButton = screen.getByText('Edit Profile')
    fireEvent.click(editButton)

    expect(screen.getByDisplayValue('John')).toBeInTheDocument()

    // Cancel edit mode
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    expect(screen.getByText('Edit Profile')).toBeInTheDocument()
    expect(screen.queryByDisplayValue('John')).not.toBeInTheDocument()
  })

  test('does not render when active prop is false', () => {
    render(<UserProfile active={false} />)
    expect(screen.queryByText('My Profile')).not.toBeInTheDocument()
  })

  test('handles different user roles correctly', async () => {
    const roles = ['admin', 'viewer', 'publisher', 'bluevisionadmin']
    
    for (const role of roles) {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: {
            user: {
              first_name: 'John',
              last_name: 'Doe',
              email: 'john.doe@example.com',
              username: 'johndoe',
              role: role,
              organization: { name: 'Test Org' },
              is_active: true,
              created_at: '2024-01-01T00:00:00Z'
            }
          }
        })
      })

      const { unmount } = render(<UserProfile />)

      await waitFor(() => {
        expect(screen.getByText(role)).toBeInTheDocument()
      })

      unmount()
    }
  })
})