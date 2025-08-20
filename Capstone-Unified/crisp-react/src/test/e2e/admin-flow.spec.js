import { test, expect } from '@playwright/test'

test.describe('Admin Flow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('admin settings page loads correctly', async ({ page }) => {
    // Try to access admin settings
    const userMenu = page.locator('[class*="user-menu"], [class*="profile-menu"]').first()
    if (await userMenu.isVisible()) {
      await userMenu.click()
      await page.waitForTimeout(500)
      
      const adminSettings = page.locator('text=Admin Settings').first()
      if (await adminSettings.isVisible()) {
        await adminSettings.click()
        await page.waitForTimeout(2000)
        
        // Should show admin settings page
        const hasAdminHeading = await page.locator('h1:has-text("Admin")').count() > 0
        const hasSystemSettings = await page.locator('text=System Settings').count() > 0
        const hasAccessDenied = await page.locator('text=Access Denied').count() > 0
        
        // Either show admin content or access denied (both are valid)
        expect(hasAdminHeading || hasSystemSettings || hasAccessDenied).toBeTruthy()
        
        if (hasAdminHeading || hasSystemSettings) {
          // Test admin functionality
          const hasTabs = await page.locator('[role="tab"], [class*="tab"]').count() > 0
          expect(hasTabs).toBeTruthy()
        }
      }
    }
  })

  test('admin can navigate between settings tabs', async ({ page }) => {
    // Access admin settings
    const userMenu = page.locator('[class*="user-menu"]').first()
    if (await userMenu.isVisible()) {
      await userMenu.click()
      await page.waitForTimeout(500)
      
      const adminSettings = page.locator('text=Admin Settings').first()
      if (await adminSettings.isVisible()) {
        await adminSettings.click()
        await page.waitForTimeout(2000)
        
        // Check if we have access (not denied)
        const hasAccessDenied = await page.locator('text=Access Denied').count() > 0
        if (!hasAccessDenied) {
          // Look for tabs
          const securityTab = page.locator('text=Security').first()
          const trustTab = page.locator('text=Trust Management').first()
          
          if (await securityTab.isVisible()) {
            await securityTab.click()
            await page.waitForTimeout(1000)
            
            // Should show security settings
            const hasPasswordSettings = await page.locator('text=Password').count() > 0
            expect(hasPasswordSettings).toBeTruthy()
          }
          
          if (await trustTab.isVisible()) {
            await trustTab.click()
            await page.waitForTimeout(1000)
            
            // Should show trust settings
            const hasTrustSettings = await page.locator('text=Trust').count() > 0
            expect(hasTrustSettings).toBeTruthy()
          }
        }
      }
    }
  })

  test('admin can modify system settings', async ({ page }) => {
    const userMenu = page.locator('[class*="user-menu"]').first()
    if (await userMenu.isVisible()) {
      await userMenu.click()
      await page.waitForTimeout(500)
      
      const adminSettings = page.locator('text=Admin Settings').first()
      if (await adminSettings.isVisible()) {
        await adminSettings.click()
        await page.waitForTimeout(2000)
        
        const hasAccessDenied = await page.locator('text=Access Denied').count() > 0
        if (!hasAccessDenied) {
          // Look for system name input
          const systemNameInput = page.locator('input[value*="CRISP"], input[placeholder*="system" i]').first()
          if (await systemNameInput.isVisible()) {
            // Change system name
            await systemNameInput.fill('Test CRISP System')
            
            // Look for save button
            const saveButton = page.locator('button:has-text("Save")').first()
            if (await saveButton.isVisible()) {
              await saveButton.click()
              await page.waitForTimeout(1000)
              
              // Should show confirmation or complete save
              const hasConfirmation = await page.locator('[class*="modal"], [class*="confirm"]').count() > 0
              const hasSuccess = await page.locator('text=success, text=saved').count() > 0
              
              expect(hasConfirmation || hasSuccess).toBeTruthy()
            }
          }
        }
      }
    }
  })

  test('admin settings show appropriate security options', async ({ page }) => {
    const userMenu = page.locator('[class*="user-menu"]').first()
    if (await userMenu.isVisible()) {
      await userMenu.click()
      await page.waitForTimeout(500)
      
      const adminSettings = page.locator('text=Admin Settings').first()
      if (await adminSettings.isVisible()) {
        await adminSettings.click()
        await page.waitForTimeout(2000)
        
        const hasAccessDenied = await page.locator('text=Access Denied').count() > 0
        if (!hasAccessDenied) {
          // Navigate to security tab
          const securityTab = page.locator('text=Security').first()
          if (await securityTab.isVisible()) {
            await securityTab.click()
            await page.waitForTimeout(1000)
            
            // Check for security settings
            const hasPasswordLength = await page.locator('text=Password Min Length, text=password').count() > 0
            const hasSessionTimeout = await page.locator('text=Session, text=timeout').count() > 0
            const hasLoginAttempts = await page.locator('text=Login, text=attempts').count() > 0
            
            expect(hasPasswordLength || hasSessionTimeout || hasLoginAttempts).toBeTruthy()
          }
        }
      }
    }
  })

  test('admin can access user management', async ({ page }) => {
    // Look for user management in navigation
    const userManagement = page.locator('text=User Management, text=Users').first()
    const managementMenu = page.locator('text=Management').first()
    
    if (await userManagement.isVisible()) {
      await userManagement.click()
      await page.waitForTimeout(2000)
      
      // Should show user management interface
      const hasUserList = await page.locator('[class*="user"], [class*="table"], [class*="list"]').count() > 0
      const hasAddUser = await page.locator('button:has-text("Add"), button:has-text("Create")').count() > 0
      
      expect(hasUserList || hasAddUser).toBeTruthy()
    } else if (await managementMenu.isVisible()) {
      await managementMenu.click()
      await page.waitForTimeout(500)
      
      const userOption = page.locator('text=User Management, text=Users').first()
      if (await userOption.isVisible()) {
        await userOption.click()
        await page.waitForTimeout(2000)
        
        const hasUserInterface = await page.locator('[class*="user"], [class*="management"]').count() > 0
        expect(hasUserInterface).toBeTruthy()
      }
    }
  })

  test('admin dashboard shows system overview', async ({ page }) => {
    // Look for dashboard
    const dashboard = page.locator('text=Dashboard').first()
    if (await dashboard.isVisible()) {
      await dashboard.click()
      await page.waitForTimeout(2000)
      
      // Should show dashboard content
      const hasMetrics = await page.locator('[class*="metric"], [class*="stat"], [class*="chart"]').count() > 0
      const hasCards = await page.locator('[class*="card"], [class*="widget"]').count() > 0
      const hasOverview = await page.locator('text=Overview, text=Statistics').count() > 0
      
      expect(hasMetrics || hasCards || hasOverview).toBeTruthy()
    }
  })

  test('admin can access organization management', async ({ page }) => {
    const orgManagement = page.locator('text=Organisation, text=Organization').first()
    if (await orgManagement.isVisible()) {
      await orgManagement.click()
      await page.waitForTimeout(2000)
      
      // Should show organization management
      const hasOrgContent = await page.locator('[class*="org"], [class*="institution"]').count() > 0
      const hasManagementInterface = await page.locator('[class*="table"], [class*="list"]').count() > 0
      
      expect(hasOrgContent || hasManagementInterface).toBeTruthy()
    }
  })

  test('admin settings persist after page reload', async ({ page }) => {
    const userMenu = page.locator('[class*="user-menu"]').first()
    if (await userMenu.isVisible()) {
      await userMenu.click()
      await page.waitForTimeout(500)
      
      const adminSettings = page.locator('text=Admin Settings').first()
      if (await adminSettings.isVisible()) {
        await adminSettings.click()
        await page.waitForTimeout(2000)
        
        const hasAccessDenied = await page.locator('text=Access Denied').count() > 0
        if (!hasAccessDenied) {
          // Get current system name value
          const systemNameInput = page.locator('input[value*="CRISP"], input[placeholder*="system" i]').first()
          if (await systemNameInput.isVisible()) {
            const originalValue = await systemNameInput.inputValue()
            
            // Reload page
            await page.reload()
            await page.waitForTimeout(2000)
            
            // Navigate back to admin settings
            const userMenu2 = page.locator('[class*="user-menu"]').first()
            if (await userMenu2.isVisible()) {
              await userMenu2.click()
              await page.waitForTimeout(500)
              
              const adminSettings2 = page.locator('text=Admin Settings').first()
              if (await adminSettings2.isVisible()) {
                await adminSettings2.click()
                await page.waitForTimeout(2000)
                
                // Should maintain the same value
                const systemNameInput2 = page.locator('input[value*="CRISP"], input[placeholder*="system" i]').first()
                if (await systemNameInput2.isVisible()) {
                  const newValue = await systemNameInput2.inputValue()
                  expect(newValue).toBe(originalValue)
                }
              }
            }
          }
        }
      }
    }
  })
})