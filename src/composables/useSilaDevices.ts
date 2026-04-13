import { ref, computed } from 'vue'
import type { SilaManager, SilaServer } from 'src/components/workflow/types'

const managers = ref<SilaManager[]>([
  {
    id: 'mgr-1',
    name: 'SiLA Server Manager 1',
    lab: '실험실 #1',
    online: true,
    servers: [
      {
        id: 'srv-1',
        name: 'SiLA Server 1',
        device: '저울 (Balance)',
        icon: 'scale',
        address: '192.168.0.101:50051',
        online: true,
        status: 'Idle',
      },
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
  return { managers, allDevices }
}
