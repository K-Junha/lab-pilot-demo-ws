import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'

const API_BASE = 'http://localhost:8000/api'

export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()
  const $q = useQuasar()

  async function register(username: string, password: string, email?: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, email }),
      })
      if (!res.ok) {
        const err = await res.json()
        $q.notify({ type: 'negative', message: err.detail ?? '회원가입 실패' })
        return false
      }
      $q.notify({ type: 'positive', message: '회원가입 완료. 로그인해주세요.' })
      return true
    } catch {
      $q.notify({ type: 'negative', message: '서버 연결 실패' })
      return false
    }
  }

  async function login(username: string, password: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      if (!res.ok) {
        const err = await res.json()
        $q.notify({ type: 'negative', message: err.detail ?? '로그인 실패' })
        return false
      }
      const { access_token } = await res.json() as { access_token: string }

      /* 토큰 검증 겸 사용자 정보 조회 */
      const meRes = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` },
      })
      if (!meRes.ok) {
        $q.notify({ type: 'negative', message: '사용자 정보 조회 실패' })
        return false
      }
      const meData = await meRes.json()
      authStore.setAuth(access_token, meData)
      return true
    } catch {
      $q.notify({ type: 'negative', message: '서버 연결 실패' })
      return false
    }
  }

  function logout() {
    authStore.clearAuth()
    void router.push('/login')
  }

  return { register, login, logout }
}
