import { ref, computed } from 'vue'
import { useAuthStore } from 'src/stores/auth'
import type { SilaManager, SilaServer } from 'src/components/workflow/types'

const API_BASE = 'http://localhost:8000/api'

/* /api/managers 응답 타입 */
interface DeviceFromApi {
  id: string
  name: string
  icon: string
  connected: boolean
  latest_value: Record<string, number>
}

interface ManagerFromApi {
  manager_id: number
  name: string
  host: string
  ws_port: number
  online: boolean
  last_seen: string | null
  devices: DeviceFromApi[]
}

function toSilaManager(m: ManagerFromApi): SilaManager {
  const servers: SilaServer[] = m.devices.map((d) => ({
    id: d.id,
    name: d.name,
    device: d.name,
    icon: d.icon,
    address: `${m.host}:${m.ws_port}`,
    online: d.connected,
    status: d.connected ? 'Running' : 'Offline',
  }))

  return {
    id: String(m.manager_id),
    name: m.name,
    lab: m.name,
    online: m.online,
    servers,
  }
}

const managers = ref<SilaManager[]>([])

async function fetchManagers(): Promise<void> {
  const authStore = useAuthStore()
  const token = authStore.token
  if (!token) return

  try {
    const res = await fetch(`${API_BASE}/managers`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) return
    const data = (await res.json()) as ManagerFromApi[]
    managers.value = data.map(toSilaManager)
  } catch {
    /* 네트워크 오류 — 이전 상태 유지 */
  }
}

export interface DeviceOption {
  serverId: string
  serverName: string
  device: string
  icon: string
  address: string
  online: boolean
  status: string
  managerLab: string
  managerName: string
}

const allDevices = computed<DeviceOption[]>(() =>
  managers.value.flatMap((mgr) =>
    mgr.servers.map((srv) => ({
      serverId: srv.id,
      serverName: srv.name,
      device: srv.device,
      icon: srv.icon,
      address: srv.address,
      online: srv.online,
      status: srv.status,
      managerLab: mgr.lab,
      managerName: mgr.name,
    }))
  )
)

export function useSilaDevices() {
  return { managers, allDevices, fetchManagers }
}
