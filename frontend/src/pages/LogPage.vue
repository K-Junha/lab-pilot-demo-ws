<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">실험 로그</div>

    <!-- 필터 -->
    <div class="row q-gutter-sm q-mb-md">
      <q-select
        v-model="filterWorkflowId"
        :options="workflowOptions"
        option-value="value"
        option-label="label"
        emit-value
        map-options
        label="Plan 필터"
        outlined
        dense
        clearable
        style="min-width: 220px"
        @update:model-value="loadLogs"
      />
      <q-select
        v-model="filterStepType"
        :options="stepTypeOptions"
        label="Step 필터"
        outlined
        dense
        clearable
        style="min-width: 160px"
        @update:model-value="loadLogs"
      />
      <q-select
        v-model="filterStatus"
        :options="['진행중', '완료', '오류']"
        label="상태 필터"
        outlined
        dense
        clearable
        style="min-width: 140px"
        @update:model-value="loadLogs"
      />
      <q-btn flat icon="refresh" @click="loadLogs" />
    </div>

    <div class="row q-gutter-md">
      <!-- 로그 테이블 -->
      <div :class="selectedLog ? 'col-7' : 'col-12'">
        <q-table
          :rows="logs"
          :columns="columns"
          row-key="log_id"
          dense
          flat
          bordered
          :loading="loading"
          @row-click="(_, row) => selectedLog = row"
        >
          <template #body-cell-status="props">
            <q-td :props="props">
              <q-badge :color="statusColor(props.value)" :label="props.value" />
            </q-td>
          </template>
          <template #body-cell-data_summary="props">
            <q-td :props="props">
              <span class="text-caption text-grey-7">{{ summarize(props.row.data_collected) }}</span>
            </q-td>
          </template>
        </q-table>
      </div>

      <!-- 사이드패널 -->
      <div v-if="selectedLog" class="col">
        <q-card flat bordered class="q-pa-md">
          <div class="row items-center q-mb-md">
            <div class="text-subtitle1 col">{{ selectedLog.step_name }}</div>
            <q-btn flat dense round icon="close" @click="selectedLog = null" />
          </div>
          <q-list dense>
            <q-item><q-item-section><q-item-label caption>Step 타입</q-item-label><q-item-label>{{ selectedLog.step_type }}</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>상태</q-item-label><q-item-label><q-badge :color="statusColor(selectedLog.status)" :label="selectedLog.status" /></q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>시작</q-item-label><q-item-label>{{ fmtDate(selectedLog.started_at) }}</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>종료</q-item-label><q-item-label>{{ fmtDate(selectedLog.ended_at) }}</q-item-label></q-item-section></q-item>
          </q-list>
          <q-separator class="q-my-md" />
          <div class="text-caption text-grey q-mb-xs">수집 데이터</div>
          <pre v-if="selectedLog.data_collected" class="text-caption bg-grey-1 q-pa-sm rounded-borders" style="overflow:auto; max-height:300px">{{ JSON.stringify(selectedLog.data_collected, null, 2) }}</pre>
          <div v-else class="text-grey text-caption">없음</div>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from 'src/stores/auth'
import { useWorkflows } from 'src/composables/useWorkflows'
import type { QTableColumn } from 'quasar'

const API_BASE = 'http://localhost:8000/api'

interface LogRow {
  log_id: number
  workflow_id: number
  step_uid: number
  step_type: string
  step_name: string
  status: string
  data_collected: Record<string, unknown> | null
  started_at: string | null
  ended_at: string | null
}

const authStore = useAuthStore()
const { workflows, fetchAll } = useWorkflows()

const logs = ref<LogRow[]>([])
const loading = ref(false)
const selectedLog = ref<LogRow | null>(null)

const filterWorkflowId = ref<number | null>(null)
const filterStepType = ref<string | null>(null)
const filterStatus = ref<string | null>(null)

const stepTypeOptions = ['weighing', 'mixing', 'forming', 'firing', 'heattreat', 'machining', 'analysis']

const workflowOptions = computed(() =>
  workflows.value.map((w) => ({ label: w.name, value: w.id }))
)

const columns: QTableColumn[] = [
  { name: 'step_name', label: 'Step 이름', field: 'step_name', align: 'left', sortable: true },
  { name: 'step_type', label: '타입', field: 'step_type', align: 'left', sortable: true },
  { name: 'status', label: '상태', field: 'status', align: 'left', sortable: true },
  { name: 'data_summary', label: '수집 데이터 요약', field: 'data_collected', align: 'left' },
  { name: 'started_at', label: '시작', field: 'started_at', align: 'left', sortable: true, format: fmtDate },
]

function statusColor(s: string) {
  switch (s) {
    case '완료': return 'green'
    case '진행중': return 'blue'
    case '오류': return 'red'
    default: return 'grey'
  }
}

function summarize(data: Record<string, unknown> | null): string {
  if (!data) return '-'
  const keys = Object.keys(data).slice(0, 3)
  return keys.map((k) => `${k}: ${String(data[k])}`).join(' | ') || '-'
}

function fmtDate(v: string | null | undefined): string {
  if (!v) return '-'
  return new Date(v).toLocaleString('ko-KR')
}

async function loadLogs() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filterWorkflowId.value) params.set('workflow_id', String(filterWorkflowId.value))
    if (filterStepType.value) params.set('step_type', filterStepType.value)
    if (filterStatus.value) params.set('status', filterStatus.value)

    const res = await fetch(`${API_BASE}/logs?${params.toString()}`, {
      headers: { Authorization: `Bearer ${authStore.token ?? ''}` },
    })
    if (!res.ok) throw new Error()
    logs.value = await res.json() as LogRow[]
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchAll()
  await loadLogs()
})
</script>
