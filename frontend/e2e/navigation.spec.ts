import { test, expect } from '@playwright/test'

test.describe('앱 기본 네비게이션', () => {
  test('모니터링 페이지 진입 (기본 홈)', async ({ page }) => {
    await page.goto('/#/')
    await expect(page).toHaveURL(/localhost:9000/)
    await expect(page.locator('body')).not.toContainText('Not Found')
  })

  test('워크플로우 페이지 이동', async ({ page }) => {
    await page.goto('/#/workflow')
    await expect(page.getByText('워크플로우 목록')).toBeVisible()
  })

  test('실험 페이지 이동', async ({ page }) => {
    await page.goto('/#/experiment')
    await expect(page).toHaveURL(/experiment/)
    await expect(page.locator('body')).not.toContainText('Not Found')
  })

  test('존재하지 않는 경로 → 404 페이지', async ({ page }) => {
    await page.goto('/#/nonexistent-page')
    await expect(page.locator('body')).toContainText('404')
  })
})
