import { ref, computed, onMounted } from 'vue'
import type { SilaManager, SilaServer } from 'src/components/workflow/types'

const BACKEND_URL = 'http://localhost:8000'

// 저울은 실제 SiLA 서버에서 가져옴
const balanceServer = ref<SilaServer>({
  id: 'balance',
  name: 'CB310 저울',
  device: '저울 (Balance)',
  icon: 'scale',
  address: '127.0.0.1:50051',
  online: false,
  status: 'Offline',
})

// 나머지 장비는 mock 데이터
const managers = ref<SilaManager[]>([
  {
    id: 'mgr-1',
    name: 'SiLA Server Manager 1',
    lab: '실험실 #1',
    online: true,
    servers: [
      balanceServer.value,
      {
        id: 'srv-2',
        name: 'SiLA Server 2',
        device: '전기로 (Furnace)',
        icon: 'local_fire_department',
        address: '192.168.0.102:50052',
        online: true,
        status: 'Running',
      },
    ],
  },
  {
    id: 'mgr-2',
    name: 'SiLA Server Manager 2',
    lab: '실험실 #2',
    online: true,
    servers: [
      {
        id: 'srv-3',
        name: 'SiLA Server 3',
        device: '믹서 (Mixer)',
        icon: 'blender',
        address: '192.168.1.101:50053',
        online: true,
        status: 'Idle',
      },
      {
        id: 'srv-4',
        name: 'SiLA Server 4',
        device: '프레서 (Press)',
        icon: 'compress',
        address: '192.168.1.102:50054',
        online: false,
        status: 'Offline',
      },
    ],
  },
])

async function fetchBalanceStatus() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/devices/balance/status`)
    const data = await res.json()
    balanceServer.value.online = data.connected
    balanceServer.value.status = data.connected ? 'Running' : 'Offline'
    // managers 배열 내 저울도 업데이트
    const srv = managers.value[0]?.servers.find(s => s.id === 'balance')
    if (srv) {
      srv.online = data.connected
      srv.status = data.connected ? 'Running' : 'Offline'
    }
  } catch {
    balanceServer.value.online = false
    balanceServer.value.status = 'Offline'
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
  managers.value.flatMap(mgr =>
    mgr.servers.map(srv => ({
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
  // 마운트 시 저울 상태를 backend에서 가져옴
  fetchBalanceStatus()
  return { managers, allDevices, fetchBalanceStatus }
}
