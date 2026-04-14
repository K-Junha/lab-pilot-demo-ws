import { ref } from 'vue'
import { useAuthStore } from 'src/stores/auth'

const BACKEND_WS_URL = 'ws://localhost:8000/api/ws/balance'

const weight = ref<number>(0)
const connected = ref(false)

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null

function connect() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return
  }

  ws = new WebSocket(BACKEND_WS_URL)

  ws.onopen = () => {
    /* 연결 후 첫 메시지로 JWT 전송 (URL 쿼리 파라미터 사용 금지) */
    const authStore = useAuthStore()
    if (authStore.token) {
      ws?.send(JSON.stringify({ type: 'auth', token: authStore.token }))
    }
    connected.value = true
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data as string) as { type: string; value?: number; message?: string }
      if (data.type === 'weight') {
        weight.value = data.value ?? 0
      } else if (data.type === 'disconnected') {
        /* 저울 물리 미연결 — 무게 0, WS 연결은 유지 */
        weight.value = 0
      } else if (data.type === 'error' && data.message === 'Unauthorized') {
        ws?.close()
      }
    } catch {
      /* parse 실패는 무시 */
    }
  }

  ws.onclose = () => {
    connected.value = false
    ws = null
    reconnectTimer = setTimeout(connect, 3000)
  }

  ws.onerror = () => {
    ws?.close()
  }
}

function disconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (ws) {
    ws.close()
    ws = null
  }
  connected.value = false
}

export function useBalanceWs() {
  return { weight, connected, connect, disconnect }
}
