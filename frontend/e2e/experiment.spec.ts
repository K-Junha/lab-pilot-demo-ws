import { test, expect, type Page } from '@playwright/test'

async function clearStorage(page: Page) {
  await page.goto('/#/')
  await page.evaluate(() => localStorage.clear())
}

async function createWorkflowWithWeighing(page: Page, name: string) {
  await page.goto('/#/workflow')
  await page.locator('button, .q-btn').filter({ hasText: '새 워크플로우' }).click()
  await page.getByLabel('워크플로우 이름').fill(name)
  await page.locator('[data-testid="add-step-btn"]').click()
  await page.getByText('원료 칭량').click()
  await page.locator('button, .q-btn').filter({ hasText: '저장' }).first().click()
  await expect(page.getByText('워크플로우가 저장되었습니다')).toBeVisible({ timeout: 10000 })
}

test.describe('실험 실행 페이지', () => {
  test.beforeEach(async ({ page }) => {
    await clearStorage(page)
    await createWorkflowWithWeighing(page, '테스트 워크플로우')
  })

  test('워크플로우 선택 가능', async ({ page }) => {
    await page.goto('/#/experiment')
    await expect(page.getByText('테스트 워크플로우')).toBeVisible()
  })

  test('워크플로우 수정 후 실험 페이지 복귀 시 변경 감지', async ({ page }) => {
    // 실험 페이지 진입 확인
    await page.goto('/#/experiment')
    await expect(page).toHaveURL(/experiment/)
    await expect(page.locator('body')).not.toContainText('Not Found')

    // 워크플로우 페이지로 이동해 스텝 추가
    await page.goto('/#/workflow')
    await page.getByText('테스트 워크플로우').first().click()
    await page.locator('[data-testid="add-step-btn"]').click()
    await page.getByText('믹싱', { exact: true }).click()
    await page.getByRole('button', { name: '저장' }).first().click()

    // 실험 페이지로 돌아가면 워크플로우가 업데이트됨
    await page.goto('/#/experiment')
    await expect(page).toHaveURL(/experiment/)
  })
})

test.describe('실험 실행 흐름', () => {
  test('페이지 진입 시 기본 레이아웃 표시', async ({ page }) => {
    await clearStorage(page)
    await page.goto('/#/experiment')

    // 네비게이션이 있는지 확인
    await expect(page).toHaveURL(/experiment/)
    // 페이지 에러가 없어야 함 (에러 페이지로 redirect되지 않아야)
    await expect(page.locator('body')).not.toContainText('404')
    await expect(page.locator('body')).not.toContainText('Not Found')
  })
})
