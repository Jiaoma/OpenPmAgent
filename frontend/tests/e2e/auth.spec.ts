import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Go to login page before each test
    await page.goto('http://localhost:8080');
  });

  test('should display login page', async ({ page }) => {
    // Should see login form
    await expect(page.locator('text=OpenPmAgent')).toBeVisible();
    await expect(page.locator('text=管理员登录')).toBeVisible();
    await expect(page.locator('text=普通用户登录')).toBeVisible();
  });

  test('admin login with valid credentials', async ({ page }) => {
    // Switch to admin login tab
    await page.click('text=管理员登录');

    // Enter credentials
    await page.fill('input[name="emp_id"]', 'admin001');
    await page.fill('input[name="password"]', 'admin123');

    // Click login button
    await page.click('button:has-text("登录")');

    // Should navigate to dashboard
    await page.waitForURL(/\/team/, { timeout: 5000 });

    // Verify login was successful
    await expect(page.locator('text=仪表盘')).toBeVisible();
    await expect(page.locator('text=admin001')).toBeVisible();
  });

  test('admin login with invalid credentials', async ({ page }) => {
    await page.click('text=管理员登录');

    await page.fill('input[name="emp_id"]', 'admin001');
    await page.fill('input[name="password"]', 'wrongpassword');

    await page.click('button:has-text("登录")');

    // Should show error message
    await expect(page.locator('text=/登录失败|Invalid credentials/').first).toBeVisible({
      timeout: 3000,
    });
  });

  test('user login with employee ID only', async ({ page }) => {
    // Switch to user login tab
    await page.click('text=普通用户登录');

    await page.fill('input[name="emp_id"]', 'user001');

    await page.click('button:has-text("登录")');

    // Should navigate to dashboard
    await page.waitForURL(/\/team/, { timeout: 5000 });

    await expect(page.locator('text=仪表盘')).toBeVisible();
  });

  test('logout functionality', async ({ page }) => {
    // First login
    await page.click('text=管理员登录');
    await page.fill('input[name="emp_id"]', 'admin001');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    await page.waitForURL(/\/team/, { timeout: 5000 });

    // Click logout
    await page.click('[aria-label="退出登录"]');

    // Should redirect to login page
    await page.waitForURL(/\/login/, { timeout: 5000 });

    // Should see login form again
    await expect(page.locator('text=OpenPmAgent')).toBeVisible();
  });
});

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('http://localhost:8080');
    await page.click('text=管理员登录');
    await page.fill('input[name="emp_id"]', 'admin001');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    await page.waitForURL(/\/team/, { timeout: 5000 });
  });

  test('navigate to team management pages', async ({ page }) => {
    // Test navigating to team management
    await page.click('text=团队管理');

    // Click on team subpages
    await expect(page.locator('text=人员列表')).toBeVisible();
    await page.click('text=人员列表');
    await expect(page.locator('h1=人员列表')).toBeVisible();

    // Go back
    await page.goBack();

    await page.click('text=小组管理');
    await expect(page.locator('h1=小组管理')).toBeVisible();
  });

  test('navigate to architecture pages', async ({ page }) => {
    await page.click('text=技术架构');
    await expect(page.locator('text=模块管理')).toBeVisible();

    await page.click('text=模块管理');
    await expect(page.locator('text=模块管理功能开发中...')).toBeVisible();
  });

  test('navigate to project management pages', async ({ page }) => {
    await page.click('text=项目管理');
    await expect(page.locator('text=版本管理')).toBeVisible();

    await page.click('text=版本管理');
    await expect(page.locator('text=版本管理功能开发中...')).toBeVisible();
  });
});

test.describe('Protected Routes', () => {
  test('should redirect to login for protected routes without auth', async ({ page }) => {
    // Try to access protected route without login
    await page.goto('http://localhost:8080/team/persons');

    // Should redirect to login
    await page.waitForURL(/\/login/, { timeout: 5000 });
    await expect(page.locator('text=OpenPmAgent')).toBeVisible();
  });

  test('should allow access after login', async ({ page }) => {
    // Login first
    await page.click('text=管理员登录');
    await page.fill('input[name="emp_id"]', 'admin001');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    await page.waitForURL(/\/team/, { timeout: 5000 });

    // Now access team pages
    await page.goto('http://localhost:8080/team/persons');
    await expect(page.locator('h1=人员列表')).toBeVisible();

    await page.goto('http://localhost:8080/team/groups');
    await expect(page.locator('h1=小组管理')).toBeVisible();
  });
});
