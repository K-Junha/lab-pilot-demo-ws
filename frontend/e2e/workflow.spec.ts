import { test, expect, type Page } from '@playwright/test'
import { injectAuth, mockManagersApi } from './helpers/auth'

async function setupWorkflows(page: Page, workflows: unknown[] = []) {
  // injectAuth는 addInitScript를 사용하므로 goto() 전에 호출해야 함
  await injectAuth(page)
  await mockManagersApi(page)
  await page.route('**/api/workflows', (route) => {
    if (route.request().method() === 'GET') {
      void route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(workflows),
      })
    } else {
      void route.continue()
    }
  })
  await page.goto('/#/workflow')
}

test.describe('워크플로우 관리', () => {
  test('빈 목록 상태 표시', async ({ page }) => {
    await setupWorkflows(page, [])
    await expect(page.getByText('아직 워크플로우가 없습니다')).toBeVisible()
    await expect(page.getByRole('button', { name: /새 워크플로우/ })).toBeVisible()
  })

  test('워크플로우 목록 표시', async ({ page }) => {
    const workflows = [
      {
        id: 1,
        name: '유리 합성 워크플로우',
        owner_id: 1,
        steps: [],
        created_at: '2024-01-01T00:00:00',
        updated_at: '2024-01-01T00:00:00',
      },
    ]
    await setupWorkflows(page, workflows)
    await expect(page.getByText('유리 합성 워크플로우')).toBeVisible()
  })

  test('[새 워크플로우] 버튼 클릭 → 에디터 표시', async ({ page }) => {
    await setupWorkflows(page, [])
    await page.getByRole('button', { name: /새 워크플로우/ }).click()
    await expect(page.getByLabel('워크플로우 이름')).toBeVisible()
  })

  test('스텝 없이 저장 시 경고 표시', async ({ page }) => {
    await setupWorkflows(page, [])
    await page.getByRole('button', { name: /새 워크플로우/ }).click()
    await page.getByLabel('워크플로우 이름').fill('빈 워크플로우')
    await page.getByRole('button', { name: '저장' }).first().click()
    await expect(page.getByText(/최소 1개의 공정 스텝/)).toBeVisible()
  })

  test('스텝 추가 다이얼로그 열기', async ({ page }) => {
    await setupWorkflows(page, [])
    await page.getByRole('button', { name: /새 워크플로우/ }).click()
    await page.locator('[data-testid="add-step-btn"]').click()
    await expect(page.getByText('원료 칭량')).toBeVisible()
  })

  test('변경 사항 있을 때 취소 시 확인 다이얼로그', async ({ page }) => {
    await setupWorkflows(page, [])
    await page.getByRole('button', { name: /새 워크플로우/ }).click()
    await page.getByLabel('워크플로우 이름').fill('변경만')
    await page.getByRole('button', { name: /취소/ }).first().click()
    await expect(page.getByText(/저장하지 않은 변경사항/)).toBeVisible()
  })

  test('스텝 추가 후 탭 표시 확인', async ({ page }) => {
    await setupWorkflows(page, [])
    await page.getByRole('button', { name: /새 워크플로우/ }).click()
    await page.locator('[data-testid="add-step-btn"]').click()
    await page.getByText('원료 칭량').click()
    await expect(page.getByText('1. 원료 칭량')).toBeVisible()
  })

  test('새 워크플로우 저장 성공', async ({ page }) => {
    // POST 응답: toWorkflow가 기대하는 실제 API 형식 (workflow_id, data.steps)
    const savedWorkflow = {
      workflow_id: 99,
      name: '저장 테스트',
      owner_id: 1,
      data: {
        steps: [{ id: 'step-1', type: 'weighing', name: '원료 칭량', config: {} }],
        compositions: [],
      },
      created_at: new Date().toISOString(),
      status: 'draft',
    }

    await injectAuth(page)
    await mockManagersApi(page)
    await page.route('**/api/workflows', (route) => {
      if (route.request().method() === 'POST') {
        void route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify(savedWorkflow),
        })
      } else if (route.request().method() === 'GET') {
        // 초기 로드는 빈 목록 → 저장 후 unshift 로 1개만 표시
        void route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: '[]',
        })
      } else {
        void route.continue()
      }
    })
    await page.goto('/#/workflow')

    await page.getByRole('button', { name: /새 워크플로우/ }).click()
    await page.getByLabel('워크플로우 이름').fill('저장 테스트')
    await page.locator('[data-testid="add-step-btn"]').click()
    await page.getByText('원료 칭량').click()
    await page.getByRole('button', { name: '저장' }).first().click()
    await expect(page.getByText('워크플로우가 저장되었습니다')).toBeVisible({ timeout: 5000 })
    await expect(page.getByText('저장 테스트')).toBeVisible()
  })
})

test.describe('워크플로우 편집 재진입', () => {
  test('기존 워크플로우 클릭 → 에디터 재진입', async ({ page }) => {
    // toWorkflow()가 기대하는 실제 API 형식: workflow_id + data.steps
    const workflow = {
      workflow_id: 1,
      name: '편집 테스트',
      owner_id: 1,
      data: {
        steps: [{ id: 'step-1', type: 'weighing', name: '원료 칭량', config: {} }],
        compositions: [],
      },
      created_at: '2024-01-01T00:00:00',
      status: 'draft',
    }
    await setupWorkflows(page, [workflow])
    await page.getByText('편집 테스트').first().click()
    await expect(page.getByText('1. 원료 칭량')).toBeVisible()
    await expect(page.getByLabel('워크플로우 이름')).toHaveValue('편집 테스트')
  })
})
