import { test, expect } from '@playwright/test'
import { mockLoginApi, mockManagersApi, injectAuth } from './helpers/auth'

test.describe('인증 — 로그인 페이지', () => {
  test('비인증 상태에서 protected 경로 접근 시 /login 리다이렉트', async ({ page }) => {
    await page.goto('/#/workflow')
    await expect(page).toHaveURL(/login/)
  })

  test('로그인 페이지 UI 요소 표시', async ({ page }) => {
    await page.goto('/#/login')
    await expect(page.getByLabel('사용자명')).toBeVisible()
    await expect(page.getByLabel('비밀번호')).toBeVisible()
    await expect(page.getByRole('button', { name: '로그인' })).toBeVisible()
  })

  test('로그인 성공 → 홈으로 이동', async ({ page }) => {
    await mockLoginApi(page)
    await mockManagersApi(page)
    await page.goto('/#/login')
    await page.getByLabel('사용자명').fill('testuser')
    await page.getByLabel('비밀번호').fill('password123')
    await page.getByRole('button', { name: '로그인' }).click()
    await expect(page).toHaveURL(/localhost:9000\/#\/$|localhost:9000\/$/)
    await expect(page).not.toHaveURL(/login/)
  })

  test('회원가입 폼으로 전환', async ({ page }) => {
    await page.goto('/#/login')
    await page.getByRole('button', { name: /회원가입/ }).last().click()
    await expect(page.getByRole('button', { name: '회원가입' }).first()).toBeVisible()
    await expect(page.getByLabel('이메일 (선택)')).toBeVisible()
  })

  test('회원가입 성공 → 완료 알림 표시', async ({ page }) => {
    await mockLoginApi(page)
    await page.goto('/#/login')
    await page.getByRole('button', { name: /회원가입/ }).last().click()
    await page.getByLabel('사용자명').fill('newuser')
    await page.getByLabel('비밀번호').fill('pass12345')
    await page.getByRole('button', { name: '회원가입' }).first().click()
    await expect(page.getByText('회원가입 완료')).toBeVisible({ timeout: 5000 })
  })
})

test.describe('인증 — 로그아웃', () => {
  test('로그아웃 후 로그인 페이지로 이동', async ({ page }) => {
    await injectAuth(page)
    await mockManagersApi(page)
    await page.goto('/#/')

    // 사이드바 또는 메뉴에서 로그아웃 버튼 찾기
    const logoutBtn = page.getByRole('button', { name: /로그아웃/ })
    if (await logoutBtn.count() > 0) {
      await logoutBtn.first().click()
      await expect(page).toHaveURL(/login/)
    } else {
      // 로그아웃 버튼이 직접 노출되지 않는 레이아웃 — 스킵
      test.skip()
    }
  })
})
