import { ref, watch } from 'vue'
import type { Workflow } from 'components/workflow/types'

const STORAGE_KEY = 'lab-pilot-workflows'

const workflows = ref<Workflow[]>(load())

function load(): Workflow[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(workflows.value))
  } catch {
    console.error('[Workflows] localStorage 저장 실패')
  }
}

watch(workflows, persist, { deep: true })

let idSeq = workflows.value.reduce((max, w) => Math.max(max, w.id), 0)

export function useWorkflows() {
  function nextId() {
    return ++idSeq
  }

  function add(workflow: Workflow) {
    workflows.value.push(workflow)
  }

  function update(index: number, workflow: Workflow) {
    workflows.value[index] = workflow
  }

  function remove(index: number) {
    workflows.value.splice(index, 1)
  }

  return {
    workflows,
    nextId,
    add,
    update,
    remove,
  }
}
