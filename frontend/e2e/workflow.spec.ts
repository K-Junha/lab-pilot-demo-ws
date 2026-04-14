import { test, expect, type Page } from '@playwright/test'

// 테스트 전 localStorage 초기화
async function clearStorage(page: Page) {
  await page.goto('/#/')
  await page.evaluate(() => localStorage.clear())
}

test.describe('워크플로우 관리', () => {
  test.beforeEach(async ({ page }) => {
    await clearStorage(page)
    await page.goto('/#/workflow')
  })

  test('빈 목록 상태 표시', async ({ page }) => {
    await expect(page.getByText('아직 워크플로우가 없습니다')).toBeVisible()
    await expect(page.getByRole('button', { name: /새 워크플로우/ })).toBeVisible()
  })

  test('새 워크플로우 생성 후 저장', async ({ page }) => {
    await page.getByRole('button', { name: /새 워크플로우/ }).click()

    // 이름 입력
    await page.getByLabel('워크플로우 이름').fill('테스트 워크플로우')

    // 스텝 추가 버튼 클릭
    await page.locator('[data-testid="add-step-btn"]').click()

    // 다이얼로그에서 계량 선택
    await page.getByText('원료 칭량').click()
    await expect(page.getByText('1. 원료 칭량')).toBeVisible()

    // 저장
    await page.getByRole('button', { name: '저장' }).first().click()
    await expect(page.getByText('워크플로우가 저장되었습니다')).toBeVisible()

    // 목록에 나타나는지 확인
    await expect(page.getByText('테스트 워크플로우')).toBeVisible()
  })

  test('스텝 추가 후 X버튼으로 삭제', async ({ page }) => {
    await page.getByRole('button', { name: /새 워크플로우/ }).click()

    // 스텝 2개 추가
    await page.locator('[data-testid="add-step-btn"]').click()
    await page.getByText('원료 칭량').click()

    await page.locator('[data-testid="add-step-btn"]').click()
    await page.getByText('믹싱', { exact: true }).click()

    await expect(page.getByText('1. 원료 칭량')).toBeVisible()
    await expect(page.getByText('2. 믹싱')).toBeVisible()

    // 첫 번째 스텝 X 버튼 클릭
    const firstTabClose = page.locator('.step-close-btn').first()
    await firstTabClose.click()

    // 확인 다이얼로그에 OK 클릭
    await page.getByRole('button', { name: /삭제|확인|OK|ok/i }).last().click()

    // 스텝이 1개만 남아야 함
    await expect(page.getByText('1. 원료 칭량')).not.toBeVisible()
    await expect(page.getByText('1. 믹싱')).toBeVisible()
  })

  test('스텝 없이 저장 시 경고 표시', async ({ page }) => {
    await page.getByRole('button', { name: /새 워크플로우/ }).click()
    await page.getByLabel('워크플로우 이름').fill('빈 워크플로우')
    await page.getByRole('button', { name: '저장' }).first().click()

    await expect(page.getByText(/최소 1개의 공정 스텝/)).toBeVisible()
  })

  test('변경 사항 있을 때 취소 시 확인 다이얼로그', async ({ page }) => {
    await page.getByRole('button', { name: /새 워크플로우/ }).click()

    // 이름만 입력 후 뒤로가기
    await page.getByLabel('워크플로우 이름').fill('변경만')
    await page.getByRole('button', { name: /취소/ }).first().click()

    await expect(page.getByText(/저장하지 않은 변경사항/)).toBeVisible()
  })

  test('여러 스텝 추가 시 UID 충돌 없음 (탭 전환 정상)', async ({ page }) => {
    await page.getByRole('button', { name: /새 워크플로우/ }).click()

    const stepTypes = ['원료 칭량', '믹싱', '성형']
    for (const stepType of stepTypes) {
      await page.locator('[data-testid="add-step-btn"]').click()
      await page.locator('.q-item__label:not(.q-item__label--caption)').filter({ hasText: stepType }).click()
    }

    // 탭이 3개 존재하고 각 탭 클릭이 정상 작동하는지 확인
    await expect(page.getByText('1. 원료 칭량')).toBeVisible()
    await expect(page.getByText('2. 믹싱')).toBeVisible()
    await expect(page.getByText('3. 성형')).toBeVisible()

    // 탭 전환
    await page.getByText('2. 믹싱').click()
    await page.getByText('3. 성형').click()
    await page.getByText('1. 원료 칭량').click()
  })
})

test.describe('워크플로우 편집 후 재진입', () => {
  test('기존 워크플로우 수정 시 스텝 재진입 가능', async ({ page }) => {
    await clearStorage(page)
    await page.goto('/#/workflow')

    // 워크플로우 생성
    await page.getByRole('button', { name: /새 워크플로우/ }).click()
    await page.getByLabel('워크플로우 이름').fill('편집 테스트')
    await page.locator('[data-testid="add-step-btn"]').click()
    await page.getByText('원료 칭량').click()
    await page.getByRole('button', { name: '저장' }).first().click()

    // 목록에서 워크플로우 클릭 → 편집 재진입
    await page.getByText('편집 테스트').first().click()

    // 에디터가 표시되고 기존 스텝이 보여야 함
    await expect(page.getByText('1. 원료 칭량')).toBeVisible()
    await expect(page.getByText('편집 테스트')).toBeVisible()
  })
})
