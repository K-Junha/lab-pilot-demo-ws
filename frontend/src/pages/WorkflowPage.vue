<template>
  <q-page padding>
    <WorkflowList
      v-if="!editing"
      :workflows="workflows"
      @create="createWorkflow"
      @select="selectWorkflow"
      @start="startWorkflow"
      @copy="openCopyDialog"
      @delete="deleteWorkflow"
    />
    <WorkflowEditor
      v-else
      :workflow="currentWorkflow!"
      @back="cancelEdit"
      @save="saveWorkflow"
    />

    <!-- Plan 복사 다이얼로그 -->
    <q-dialog v-model="copyDialogOpen">
      <q-card style="min-width: 320px">
        <q-card-section>
          <div class="text-h6">Plan 복사</div>
        </q-card-section>
        <q-card-section>
          <q-input
            v-model="copyName"
            label="새 Plan 이름"
            outlined
            dense
            autofocus
            @keyup.enter="confirmCopy"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="취소" v-close-popup />
          <q-btn color="primary" label="복사" :disable="!copyName.trim()" @click="confirmCopy" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import WorkflowList from 'components/workflow/WorkflowList.vue'
import WorkflowEditor from 'components/workflow/WorkflowEditor.vue'
import { useWorkflows } from 'src/composables/useWorkflows'
import type { Workflow } from 'components/workflow/types'
import { API_BASE } from 'src/config'

const $q = useQuasar()
const authStore = useAuthStore()
const { workflows, nextId, fetchAll, add, update, remove } = useWorkflows()

const editing = ref(false)
const editIndex = ref<number | null>(null)
const currentWorkflow = ref<Workflow | null>(null)
const savedSnapshot = ref<string>('')

const copyDialogOpen = ref(false)
const copyName = ref('')
const copySourceIndex = ref<number | null>(null)

onMounted(() => void fetchAll())

function authHeaders(): Record<string, string> {
  return { 'Content-Type': 'application/json', Authorization: `Bearer ${authStore.token ?? ''}` }
}

function createWorkflow() {
  currentWorkflow.value = {
    id: nextId(),
    name: '',
    compositions: [],
    steps: [],
    createdAt: new Date().toLocaleString('ko-KR'),
    status: '계획중',
  }
  savedSnapshot.value = JSON.stringify(currentWorkflow.value)
  editIndex.value = null
  editing.value = true
}

function selectWorkflow(index: number) {
  const wf = workflows.value[index]
  if (!wf) return
  currentWorkflow.value = JSON.parse(JSON.stringify(wf)) as Workflow
  savedSnapshot.value = JSON.stringify(currentWorkflow.value)
  editIndex.value = index
  editing.value = true
}

function saveWorkflow() {
  if (!currentWorkflow.value) return
  if (currentWorkflow.value.steps.length === 0) {
    $q.notify({ type: 'warning', message: '최소 1개의 공정 스텝을 추가해주세요.' })
    return
  }
  const name = currentWorkflow.value.name.trim() || `워크플로우 ${workflows.value.length + 1}`
  currentWorkflow.value.name = name

  if (editIndex.value != null) {
    void update(editIndex.value, JSON.parse(JSON.stringify(currentWorkflow.value)) as Workflow)
  } else {
    void add(JSON.parse(JSON.stringify(currentWorkflow.value)) as Workflow)
  }
  editing.value = false
  currentWorkflow.value = null
  $q.notify({ type: 'positive', message: '워크플로우가 저장되었습니다.' })
}

function cancelEdit() {
  const hasChanges = JSON.stringify(currentWorkflow.value) !== savedSnapshot.value
  if (hasChanges) {
    $q.dialog({
      title: '편집 취소',
      message: '저장하지 않은 변경사항이 있습니다. 나가시겠습니까?',
      cancel: { flat: true, label: '계속 편집' },
      ok: { color: 'negative', label: '나가기' },
    }).onOk(() => {
      editing.value = false
      currentWorkflow.value = null
    })
  } else {
    editing.value = false
    currentWorkflow.value = null
  }
}

async function startWorkflow(index: number) {
  const wf = workflows.value[index]
  if (!wf || wf.status !== '계획중') return
  try {
    const res = await fetch(`${API_BASE}/workflows/${wf.id}`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ status: '진행중' }),
    })
    if (!res.ok) throw new Error()
    void fetchAll()
    $q.notify({ type: 'positive', message: '실험이 시작되었습니다.' })
  } catch {
    $q.notify({ type: 'negative', message: '상태 변경 실패' })
  }
}

function deleteWorkflow(index: number) {
  $q.dialog({
    title: '삭제 확인',
    message: '이 워크플로우를 삭제하시겠습니까?',
    cancel: { flat: true, label: '취소' },
    ok: { color: 'negative', label: '삭제' },
  }).onOk(() => void remove(index))
}

function openCopyDialog(index: number) {
  const wf = workflows.value[index]
  if (!wf) return
  copySourceIndex.value = index
  copyName.value = `${wf.name} (복사)`
  copyDialogOpen.value = true
}

async function confirmCopy() {
  const index = copySourceIndex.value
  if (index === null) return
  const wf = workflows.value[index]
  if (!wf || !copyName.value.trim()) return

  try {
    const res = await fetch(`${API_BASE}/workflows/${wf.id}/copy`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ name: copyName.value.trim() }),
    })
    if (!res.ok) throw new Error()
    copyDialogOpen.value = false
    void fetchAll()
    $q.notify({ type: 'positive', message: 'Plan이 복사되었습니다.' })
  } catch {
    $q.notify({ type: 'negative', message: 'Plan 복사 실패' })
  }
}
</script>
