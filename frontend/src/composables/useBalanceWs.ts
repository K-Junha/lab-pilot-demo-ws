import { ref, onUnmounted } from 'vue'

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
    connected.value = true
    console.log('[BalanceWS] Connected')
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'weight') {
        weight.value = data.value
      } else if (data.type === 'disconnected') {
        // 저울 물리 미연결 — 무게 0, 연결 상태는 WS 유지
        weight.value = 0
      }
    } catch (e) {
      console.error('[BalanceWS] Parse error:', e)
    }
  }

  ws.onclose = () => {
    connected.value = false
    ws = null
    console.log('[BalanceWS] Disconnected, reconnecting in 3s...')
    reconnectTimer = setTimeout(connect, 3000)
  }

  ws.onerror = (err) => {
    console.error('[BalanceWS] Error:', err)
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
