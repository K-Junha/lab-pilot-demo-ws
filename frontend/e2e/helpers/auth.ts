import type { Page } from '@playwright/test'

export const FAKE_TOKEN = 'fake-jwt-token-for-e2e-testing'
export const FAKE_USER = {
  user_id: 1,
  username: 'e2e_user',
  email: 'e2e@test.com',
  role: 'admin',
}

/**
 * 페이지 초기화 스크립트로 인증 상태를 주입한다.
 * addInitScript는 모든 페이지 로드 전에 실행되므로 goto() 전에 호출해야 한다.
 * auth store는 localStorage 값만 확인하므로 실제 JWT 불필요.
 */
export async function injectAuth(page: Page): Promise<void> {
  await page.addInitScript(
    ({ token, user }: { token: string; user: string }) => {
      localStorage.setItem('lab-pilot-token', token)
      localStorage.setItem('lab-pilot-user', user)
    },
    { token: FAKE_TOKEN, user: JSON.stringify(FAKE_USER) },
  )
}

/**
 * 로그인 API를 mock한다.
 */
export async function mockLoginApi(page: Page): Promise<void> {
  await page.route('**/api/auth/login', (route) => {
    void route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ access_token: FAKE_TOKEN }),
    })
  })
  await page.route('**/api/auth/me', (route) => {
    void route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(FAKE_USER),
    })
  })
  await page.route('**/api/auth/register', (route) => {
    void route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({ user_id: 2, username: 'newuser' }),
    })
  })
}

/**
 * 모니터링 API mock
 */
export async function mockManagersApi(page: Page): Promise<void> {
  await page.route('**/api/managers', (route) => {
    void route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

export const MOCK_WORKFLOWS = [
  {
    id: 1,
    name: '테스트 워크플로우',
    owner_id: 1,
    steps: [{ id: 'step-1', type: 'weighing', name: '원료 칭량', config: {} }],
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  },
]

export async function mockWorkflowApi(page: Page, workflows = MOCK_WORKFLOWS): Promise<void> {
  await page.route('**/api/workflows', (route) => {
    if (route.request().method() === 'GET') {
      void route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(workflows),
      })
    } else if (route.request().method() === 'POST') {
      const newWorkflow = { id: Date.now(), ...workflows[0], name: '새 워크플로우' }
      void route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(newWorkflow),
      })
    } else {
      void route.continue()
    }
  })
  await page.route('**/api/workflows/*', (route) => {
    if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
      void route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(workflows[0]) })
    } else if (route.request().method() === 'DELETE') {
      void route.fulfill({ status: 204 })
    } else {
      void route.continue()
    }
  })
}
