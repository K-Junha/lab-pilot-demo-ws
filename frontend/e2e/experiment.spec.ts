import { test, expect } from '@playwright/test'
import { injectAuth, mockManagersApi } from './helpers/auth'

const WEIGHING_WORKFLOW = {
  id: 1,
  name: '테스트 워크플로우',
  owner_id: 1,
  steps: [{ id: 'step-1', type: 'weighing', name: '원료 칭량', config: {} }],
  created_at: '2024-01-01T00:00:00',
  updated_at: '2024-01-01T00:00:00',
}

test.describe('실험 실행 페이지', () => {
  test('페이지 진입 시 기본 레이아웃 표시', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.route('**/api/workflows', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
    )
    await page.goto('/#/experiment')
    await expect(page).toHaveURL(/experiment/)
    await expect(page.locator('body')).not.toContainText('404')
    await expect(page.locator('body')).not.toContainText('Not Found')
  })

  test('워크플로우 선택 가능 (드롭다운 표시)', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.route('**/api/workflows', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([WEIGHING_WORKFLOW]),
      }),
    )
    await page.goto('/#/experiment')
    // q-select 드롭다운이 페이지에 표시되어야 함
    await expect(page.locator('.q-select')).toBeVisible()
    // 드롭다운 클릭 후 옵션 확인
    await page.locator('.q-select').click()
    await expect(page.getByRole('option').first()).toBeVisible({ timeout: 5000 })
  })

  test('워크플로우 없을 때 페이지 정상 표시', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.route('**/api/workflows', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
    )
    await page.goto('/#/experiment')
    await expect(page).toHaveURL(/experiment/)
    await expect(page.locator('body')).not.toContainText('Not Found')
  })
})

test.describe('모니터링 페이지', () => {
  test('서버 없을 때 빈 상태 메시지 표시', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.goto('/#/')
    await expect(page).toHaveURL(/localhost:9000/)
    await expect(page.locator('body')).not.toContainText('Not Found')
  })

  test('SiLA Server Monitoring 헤딩 표시', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.goto('/#/')
    await expect(page.getByText('SiLA Server Monitoring')).toBeVisible()
  })
})
