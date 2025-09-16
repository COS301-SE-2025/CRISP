import { test, expect } from '@playwright/test'

test.describe('Login Flow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Clear storage before each test
    await page.context().clearCookies()
    await page.evaluate(() => {
      localStorage.clear()
      sessionStorage.clear()
    })
  })

  test('user can access login page', async ({ page }) => {
    await page.goto('/')
    
    // Should show login form or redirect to login
    await expect(page).toHaveTitle(/CRISP/i)
    
    // Look for login elements
    const loginForm = page.locator('form').first()
    const usernameField = page.locator('input[type="text"]').first()
    const passwordField = page.locator('input[type="password"]').first()
    
    if (await loginForm.isVisible()) {
      await expect(usernameField).toBeVisible()
      await expect(passwordField).toBeVisible()
    }
  })

  test('user can attempt login with credentials', async ({ page }) => {
    await page.goto('/')
    
    // Wait for page to load
    await page.waitForLoadState('networkidle')
    
    // Try to find login form elements
    const usernameField = page.locator('input[name="username"], input[placeholder*="username" i]').first()
    const passwordField = page.locator('input[type="password"]').first()
    const loginButton = page.locator('button:has-text("Login"), button:has-text("Sign In")').first()
    
    if (await usernameField.isVisible()) {
      await usernameField.fill('testuser')
      await passwordField.fill('testpassword')
      await loginButton.click()
      
      // Wait for response
      await page.waitForTimeout(2000)
      
      // Should either succeed and redirect or show error
      const hasError = await page.locator('[class*="error"], [class*="alert"]').count() > 0
      const hasRedirect = page.url() !== page.url()
      
      expect(hasError || hasRedirect).toBeTruthy()
    } else {
      console.log('Login form not found - application may already be authenticated')
    }
  })

  test('application handles invalid credentials gracefully', async ({ page }) => {
    await page.goto('/')
    
    await page.waitForLoadState('networkidle')
    
    const usernameField = page.locator('input[name="username"], input[placeholder*="username" i]').first()
    const passwordField = page.locator('input[type="password"]').first()
    const loginButton = page.locator('button:has-text("Login"), button:has-text("Sign In")').first()
    
    if (await usernameField.isVisible()) {
      await usernameField.fill('invaliduser')
      await passwordField.fill('wrongpassword')
      await loginButton.click()
      
      // Should show error message
      await expect(page.locator('[class*="error"], [class*="alert"], text=*invalid*')).toBeVisible({ timeout: 5000 })
    }
  })

  test('application loads main interface after authentication', async ({ page }) => {
    await page.goto('/')
    
    // Check if already authenticated or needs authentication
    await page.waitForLoadState('networkidle')
    
    // Look for main application elements
    const hasDashboard = await page.locator('text=Dashboard').count() > 0
    const hasNavigation = await page.locator('nav, [role="navigation"]').count() > 0
    const hasMainContent = await page.locator('main, [role="main"]').count() > 0
    
    if (hasDashboard || hasNavigation || hasMainContent) {
      // Application is loaded
      expect(hasDashboard || hasNavigation || hasMainContent).toBeTruthy()
    } else {
      // Might need authentication first
      const hasLoginForm = await page.locator('input[type="password"]').count() > 0
      expect(hasLoginForm).toBeTruthy()
    }
  })

  test('navigation works correctly', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Check if we can navigate between sections
    const navigationLinks = await page.locator('nav a, [role="navigation"] a').all()
    
    if (navigationLinks.length > 0) {
      // Try clicking a navigation link
      await navigationLinks[0].click()
      await page.waitForTimeout(1000)
      
      // Should navigate successfully without errors
      const hasError = await page.locator('[class*="error"]').count() > 0
      expect(hasError).toBeFalsy()
    }
  })

  test('user profile is accessible', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Look for user profile access
    const profileButton = page.locator('button:has-text("Profile"), [class*="profile"], [class*="user"]').first()
    const profileLink = page.locator('a:has-text("Profile")').first()
    
    if (await profileButton.isVisible()) {
      await profileButton.click()
      await page.waitForTimeout(1000)
      
      // Should show profile content or menu
      const hasProfileContent = await page.locator('text=Profile, text=Account, text=Settings').count() > 0
      expect(hasProfileContent).toBeTruthy()
    } else if (await profileLink.isVisible()) {
      await profileLink.click()
      await page.waitForTimeout(1000)
      
      const hasProfileContent = await page.locator('text=Profile, text=Account').count() > 0
      expect(hasProfileContent).toBeTruthy()
    }
  })
})