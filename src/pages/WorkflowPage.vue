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
import WorkflowList from 'components/workflow/WorkflowList.vue'
import WorkflowEditor from 'components/workflow/WorkflowEditor.vue'
import { useWorkflows } from 'src/composables/useWorkflows'
import type { Workflow } from 'components/workflow/types'

const { workflows, nextId, add, update } = useWorkflows()
const editing = ref(false)
const editIndex = ref<number | null>(null)
const currentWorkflow = ref<Workflow | null>(null)

function createWorkflow() {
  currentWorkflow.value = {
    id: nextId(),
    name: '',
    compositions: [],
    steps: [],
    createdAt: new Date().toLocaleString('ko-KR'),
    status: '작성 중',
  }
  editIndex.value = null
  editing.value = true
}

function selectWorkflow(index: number) {
  const wf = workflows.value[index]
  if (!wf) return
  currentWorkflow.value = JSON.parse(JSON.stringify(wf))
  editIndex.value = index
  editing.value = true
}

function saveWorkflow() {
  if (!currentWorkflow.value) return
  const name = currentWorkflow.value.name.trim() || `워크플로우 ${workflows.value.length + 1}`
  currentWorkflow.value.name = name

  if (editIndex.value != null) {
    update(editIndex.value, JSON.parse(JSON.stringify(currentWorkflow.value)))
  } else {
    add(JSON.parse(JSON.stringify(currentWorkflow.value)))
  }
  editing.value = false
  currentWorkflow.value = null
}

function cancelEdit() {
  editing.value = false
  currentWorkflow.value = null
}
</script>