import { ref } from 'vue'
import { useQuasar } from 'quasar'
import type { Workflow } from 'components/workflow/types'
import { useAuthStore } from 'src/stores/auth'

const API_BASE = 'http://localhost:8000/api'

const workflows = ref<Workflow[]>([])

function toWorkflow(raw: Record<string, unknown>): Workflow {
  const data = (raw.data ?? {}) as { compositions?: unknown[]; steps?: unknown[] }
  return {
    id: raw.workflow_id as number,
    name: raw.name as string,
    compositions: (data.compositions ?? []) as Workflow['compositions'],
    steps: (data.steps ?? []) as Workflow['steps'],
    createdAt: raw.created_at as string,
    status: raw.status as string,
  }
}

export function useWorkflows() {
  const $q = useQuasar()
  const authStore = useAuthStore()

  function authHeaders(): Record<string, string> {
    return { 'Content-Type': 'application/json', Authorization: `Bearer ${authStore.token ?? ''}` }
  }

  async function fetchAll(): Promise<void> {
    try {
      const res = await fetch(`${API_BASE}/workflows`, { headers: authHeaders() })
      if (res.status === 401) {
        authStore.clearAuth()
        return
      }
      if (!res.ok) throw new Error(await res.text())
      const raw = await res.json() as Record<string, unknown>[]
      workflows.value = raw.map(toWorkflow)
    } catch {
      $q.notify({ type: 'negative', message: '워크플로우 목록 조회 실패' })
    }
  }

  function nextId(): number {
    /* 로컬에서 임시 ID — 실제 ID는 서버 응답으로 교체됨 */
    return Date.now()
  }

  async function add(workflow: Workflow): Promise<void> {
    try {
      const body = {
        name: workflow.name,
        data: { compositions: workflow.compositions, steps: workflow.steps },
      }
      const res = await fetch(`${API_BASE}/workflows`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(await res.text())
      const raw = await res.json() as Record<string, unknown>
      workflows.value.unshift(toWorkflow(raw))
    } catch {
      $q.notify({ type: 'negative', message: '워크플로우 생성 실패' })
    }
  }

  async function update(index: number, workflow: Workflow): Promise<void> {
    const target = workflows.value[index]
    if (!target) return
    try {
      const body = {
        name: workflow.name,
        status: workflow.status,
        data: { compositions: workflow.compositions, steps: workflow.steps },
      }
      const res = await fetch(`${API_BASE}/workflows/${target.id}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(await res.text())
      const raw = await res.json() as Record<string, unknown>
      workflows.value[index] = toWorkflow(raw)
    } catch {
      $q.notify({ type: 'negative', message: '워크플로우 수정 실패' })
    }
  }

  async function remove(index: number): Promise<void> {
    const target = workflows.value[index]
    if (!target) return
    try {
      const res = await fetch(`${API_BASE}/workflows/${target.id}`, {
        method: 'DELETE',
        headers: authHeaders(),
      })
      if (!res.ok) throw new Error(await res.text())
      workflows.value.splice(index, 1)
    } catch {
      $q.notify({ type: 'negative', message: '워크플로우 삭제 실패' })
    }
  }

  return {
    workflows,
    nextId,
    fetchAll,
    add,
    update,
    remove,
  }
}
