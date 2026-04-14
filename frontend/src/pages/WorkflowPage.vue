<template>
  <q-page padding>
    <WorkflowList
      v-if="!editing"
      :workflows="workflows"
      @create="createWorkflow"
      @select="selectWorkflow"
    />
    <WorkflowEditor
      v-else
      :workflow="currentWorkflow!"
      @back="cancelEdit"
      @save="saveWorkflow"
    />
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import WorkflowList from 'components/workflow/WorkflowList.vue'
import WorkflowEditor from 'components/workflow/WorkflowEditor.vue'
import { useWorkflows } from 'src/composables/useWorkflows'
import type { Workflow } from 'components/workflow/types'

const $q = useQuasar()
const router = useRouter()
const { workflows, nextId, add, update } = useWorkflows()
const editing = ref(false)
const editIndex = ref<number | null>(null)
const currentWorkflow = ref<Workflow | null>(null)
const savedSnapshot = ref<string>('')

function createWorkflow() {
  currentWorkflow.value = {
    id: nextId(),
    name: '',
    compositions: [],
    steps: [],
    createdAt: new Date().toLocaleString('ko-KR'),
    status: '작성 중',
  }
  savedSnapshot.value = JSON.stringify(currentWorkflow.value)
  editIndex.value = null
  editing.value = true
}

function selectWorkflow(index: number) {
  const wf = workflows.value[index]
  if (!wf) return
  currentWorkflow.value = JSON.parse(JSON.stringify(wf))
  savedSnapshot.value = JSON.stringify(currentWorkflow.value)
  editIndex.value = index
  editing.value = true
}

function saveWorkflow() {
  if (!currentWorkflow.value) return
  // 유효성 검증: 최소 1개 스텝 필요
  if (currentWorkflow.value.steps.length === 0) {
    $q.notify({ type: 'warning', message: '최소 1개의 공정 스텝을 추가해주세요.' })
    return
  }
  const name = currentWorkflow.value.name.trim() || `워크플로우 ${workflows.value.length + 1}`
  currentWorkflow.value.name = name

  if (editIndex.value != null) {
    update(editIndex.value, JSON.parse(JSON.stringify(currentWorkflow.value)))
  } else {
    add(JSON.parse(JSON.stringify(currentWorkflow.value)))
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
</script>