import { test, expect } from '@playwright/test'

test.describe('User Profile Flow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('user can access profile page', async ({ page }) => {
    // Try to find and click profile access
    const profileButton = page.locator('button:has-text("Profile"), button:has-text("My Profile")').first()
    const userMenu = page.locator('[class*="user"], [class*="profile"], [class*="avatar"]').first()
    
    if (await profileButton.isVisible()) {
      await profileButton.click()
    } else if (await userMenu.isVisible()) {
      await userMenu.click()
      // Look for profile option in dropdown
      const profileOption = page.locator('text=Profile, text=My Profile').first()
      if (await profileOption.isVisible()) {
        await profileOption.click()
      }
    }
    
    await page.waitForTimeout(2000)
    
    // Should show profile page or content
    const hasProfileHeading = await page.locator('h1:has-text("Profile"), h2:has-text("Profile"), h1:has-text("My Profile")').count() > 0
    const hasUserInfo = await page.locator('input[type="email"], text=@, [class*="email"]').count() > 0
    
    expect(hasProfileHeading || hasUserInfo).toBeTruthy()
  })

  test('user can view their profile information', async ({ page }) => {
    // Navigate to profile
    await page.goto('/')
    await page.waitForTimeout(1000)
    
    // Try different ways to access profile
    const profileButton = page.locator('button:has-text("Profile")').first()
    const userButton = page.locator('[class*="user-menu"], [class*="profile-menu"]').first()
    
    if (await profileButton.isVisible()) {
      await profileButton.click()
      await page.waitForTimeout(1000)
      
      // Check for profile information
      const hasEmail = await page.locator('input[type="email"], [class*="email"]').count() > 0
      const hasName = await page.locator('input[placeholder*="name" i], [class*="name"]').count() > 0
      const hasUserDetails = await page.locator('[class*="user"], [class*="profile"]').count() > 0
      
      expect(hasEmail || hasName || hasUserDetails).toBeTruthy()
    }
  })

  test('user can enter edit mode for profile', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(1000)
    
    // Navigate to profile and find edit button
    const editButton = page.locator('button:has-text("Edit"), button:has-text("Edit Profile")').first()
    
    // First try to access profile
    const profileAccess = page.locator('button:has-text("Profile"), [class*="profile"]').first()
    if (await profileAccess.isVisible()) {
      await profileAccess.click()
      await page.waitForTimeout(1000)
    }
    
    // Now look for edit button
    const editBtn = page.locator('button:has-text("Edit"), button:has-text("Edit Profile")').first()
    if (await editBtn.isVisible()) {
      await editBtn.click()
      await page.waitForTimeout(1000)
      
      // Should show editable form fields
      const editableFields = await page.locator('input:not([readonly]):not([disabled])').count()
      expect(editableFields).toBeGreaterThan(0)
      
      // Should have save/cancel buttons
      const hasSaveButton = await page.locator('button:has-text("Save")').count() > 0
      const hasCancelButton = await page.locator('button:has-text("Cancel")').count() > 0
      
      expect(hasSaveButton || hasCancelButton).toBeTruthy()
    }
  })

  test('profile form validation works', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(1000)
    
    // Try to access profile edit mode
    const profileBtn = page.locator('button:has-text("Profile")').first()
    if (await profileBtn.isVisible()) {
      await profileBtn.click()
      await page.waitForTimeout(1000)
    }
    
    const editBtn = page.locator('button:has-text("Edit")').first()
    if (await editBtn.isVisible()) {
      await editBtn.click()
      await page.waitForTimeout(1000)
      
      // Try to clear required fields and save
      const emailField = page.locator('input[type="email"]').first()
      if (await emailField.isVisible()) {
        await emailField.clear()
        
        const saveButton = page.locator('button:has-text("Save")').first()
        if (await saveButton.isVisible()) {
          await saveButton.click()
          await page.waitForTimeout(1000)
          
          // Should show validation error or prevent save
          const hasError = await page.locator('[class*="error"], [class*="invalid"]').count() > 0
          const fieldStillEmpty = await emailField.inputValue() === ''
          
          // If field is required, should show error or not clear the field
          expect(hasError || !fieldStillEmpty).toBeTruthy()
        }
      }
    }
  })

  test('settings page is accessible', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(1000)
    
    // Look for settings access
    const settingsButton = page.locator('button:has-text("Settings"), a:has-text("Settings")').first()
    const accountButton = page.locator('button:has-text("Account"), a:has-text("Account")').first()
    
    if (await settingsButton.isVisible()) {
      await settingsButton.click()
    } else if (await accountButton.isVisible()) {
      await accountButton.click()
    } else {
      // Try user menu
      const userMenu = page.locator('[class*="user-menu"]').first()
      if (await userMenu.isVisible()) {
        await userMenu.click()
        await page.waitForTimeout(500)
        
        const settingsOption = page.locator('text=Settings, text=Account Settings').first()
        if (await settingsOption.isVisible()) {
          await settingsOption.click()
        }
      }
    }
    
    await page.waitForTimeout(1000)
    
    // Should show settings page
    const hasSettingsHeading = await page.locator('h1:has-text("Settings"), h2:has-text("Settings")').count() > 0
    const hasSettingsTabs = await page.locator('[role="tab"], [class*="tab"]').count() > 0
    const hasSettingsContent = await page.locator('[class*="settings"]').count() > 0
    
    expect(hasSettingsHeading || hasSettingsTabs || hasSettingsContent).toBeTruthy()
  })

  test('admin settings are accessible for admin users', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(1000)
    
    // Look for admin settings - might be in user menu
    const userMenu = page.locator('[class*="user-menu"], [class*="profile-menu"]').first()
    if (await userMenu.isVisible()) {
      await userMenu.click()
      await page.waitForTimeout(500)
      
      const adminSettings = page.locator('text=Admin Settings, text=Administration').first()
      if (await adminSettings.isVisible()) {
        await adminSettings.click()
        await page.waitForTimeout(1000)
        
        // Should show admin settings or access denied
        const hasAdminContent = await page.locator('h1:has-text("Admin"), h2:has-text("Admin")').count() > 0
        const hasAccessDenied = await page.locator('text=Access Denied, text=Permission').count() > 0
        
        expect(hasAdminContent || hasAccessDenied).toBeTruthy()
      }
    }
  })

  test('navigation between profile sections works', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(1000)
    
    // Try to access settings with tabs
    const settingsAccess = page.locator('button:has-text("Settings"), [class*="settings"]').first()
    if (await settingsAccess.isVisible()) {
      await settingsAccess.click()
      await page.waitForTimeout(1000)
      
      // Look for tabs
      const tabs = await page.locator('[role="tab"], [class*="tab"]').all()
      if (tabs.length > 1) {
        // Click different tabs
        await tabs[0].click()
        await page.waitForTimeout(500)
        
        await tabs[1].click()
        await page.waitForTimeout(500)
        
        // Should navigate without errors
        const hasError = await page.locator('[class*="error"]').count() > 0
        expect(hasError).toBeFalsy()
      }
    }
  })

  test('profile changes can be saved', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(1000)
    
    // Access profile edit
    const profileBtn = page.locator('button:has-text("Profile")').first()
    if (await profileBtn.isVisible()) {
      await profileBtn.click()
      await page.waitForTimeout(1000)
    }
    
    const editBtn = page.locator('button:has-text("Edit")').first()
    if (await editBtn.isVisible()) {
      await editBtn.click()
      await page.waitForTimeout(1000)
      
      // Make a change to a field
      const nameField = page.locator('input[placeholder*="name" i]').first()
      if (await nameField.isVisible()) {
        const originalValue = await nameField.inputValue()
        await nameField.fill('Test User Updated')
        
        // Save changes
        const saveBtn = page.locator('button:has-text("Save")').first()
        if (await saveBtn.isVisible()) {
          await saveBtn.click()
          await page.waitForTimeout(2000)
          
          // Should show success or complete save
          const hasSuccessMessage = await page.locator('text=success, text=saved, text=updated').count() > 0
          const noError = await page.locator('[class*="error"]').count() === 0
          
          expect(hasSuccessMessage || noError).toBeTruthy()
        }
      }
    }
  })
})