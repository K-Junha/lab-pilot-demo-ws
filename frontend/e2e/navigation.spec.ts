import { test, expect } from '@playwright/test'
import { injectAuth, mockManagersApi } from './helpers/auth'

test.describe('앱 기본 네비게이션', () => {
  test('모니터링 페이지 진입 (기본 홈)', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.goto('/#/')
    await expect(page).toHaveURL(/localhost:9000/)
    await expect(page.locator('body')).not.toContainText('Not Found')
  })

  test('워크플로우 페이지 이동', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.route('**/api/workflows', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
    )
    await page.goto('/#/workflow')
    await expect(page.getByText('워크플로우 목록')).toBeVisible({ timeout: 10000 })
  })

  test('실험 페이지 이동', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.route('**/api/workflows', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
    )
    await page.goto('/#/experiment')
    await expect(page).toHaveURL(/experiment/)
    await expect(page.locator('body')).not.toContainText('Not Found')
  })

  test('존재하지 않는 경로 → 404 페이지', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.goto('/#/nonexistent-page')
    await expect(page.locator('body')).toContainText('404')
  })

  test('비인증 상태에서 protected 경로 → /login 리다이렉트', async ({ page }) => {
    await page.goto('/#/workflow')
    await expect(page).toHaveURL(/login/)
  })
})
