<template>
  <q-page class="lp-page">
    <!-- Page header -->
    <div class="lp-page-head">
      <div>
        <h1 class="lp-page-head__title">실험 로그</h1>
        <div class="lp-page-head__sub lp-mono">{{ logs.length }}개 항목</div>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="lp-filter-bar">
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
        class="lp-select"
        style="min-width: 200px"
        @update:model-value="loadLogs"
      />
      <q-select
        v-model="filterStepType"
        :options="stepTypeOptions"
        label="Step 필터"
        outlined
        dense
        clearable
        class="lp-select"
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
        class="lp-select"
        style="min-width: 140px"
        @update:model-value="loadLogs"
      />
      <q-btn flat dense no-caps icon="refresh" class="lp-btn-ghost" @click="loadLogs" />
    </div>

    <!-- Main content -->
    <div class="lp-log-layout" :class="{ 'lp-log-layout--split': !!selectedLog }">
      <!-- Log table -->
      <div class="lp-log-table-wrap">
        <div v-if="loading" class="lp-loading">
          <q-spinner size="24px" style="color: var(--accent);" />
        </div>

        <div v-else-if="logs.length === 0" class="lp-empty">
          <q-icon name="list_alt" size="48px" style="color: var(--t4);" />
          <div class="lp-empty__title">로그가 없습니다</div>
          <div class="lp-empty__sub">필터 조건을 변경하거나 실험을 실행하세요</div>
        </div>

        <table v-else class="lp-table">
          <thead>
            <tr>
              <th class="lp-table__sortable" @click="setSort('step_name')">
                Step 이름 <span class="lp-sort-icon">{{ sortKey === 'step_name' ? (sortAsc ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th class="lp-table__sortable" @click="setSort('step_type')">
                타입 <span class="lp-sort-icon">{{ sortKey === 'step_type' ? (sortAsc ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th class="lp-table__sortable" @click="setSort('status')">
                상태 <span class="lp-sort-icon">{{ sortKey === 'status' ? (sortAsc ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th>수집 데이터 요약</th>
              <th class="lp-table__sortable" @click="setSort('started_at')">
                시작 <span class="lp-sort-icon">{{ sortKey === 'started_at' ? (sortAsc ? '↑' : '↓') : '↕' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in sortedLogs"
              :key="row.log_id"
              class="lp-table__row"
              :class="{ 'lp-table__row--active': selectedLog?.log_id === row.log_id }"
              @click="selectedLog = row"
            >
              <td class="lp-table__name">{{ row.step_name }}</td>
              <td class="lp-mono lp-table__type">{{ row.step_type }}</td>
              <td>
                <span class="lp-status-chip" :class="statusChipClass(row.status)">
                  <span v-if="row.status === '진행중'" class="lp-pulse-dot" />
                  {{ row.status }}
                </span>
              </td>
              <td class="lp-table__summary">{{ summarize(row.data_collected) }}</td>
              <td class="lp-mono lp-table__date">{{ fmtDate(row.started_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Side panel -->
      <div v-if="selectedLog" class="lp-log-panel">
        <div class="lp-log-panel__head">
          <div class="lp-log-panel__title">{{ selectedLog.step_name }}</div>
          <q-btn flat dense round icon="close" class="lp-icon-btn" @click="selectedLog = null" />
        </div>

        <!-- Meta grid -->
        <div class="lp-meta-grid">
          <div class="lp-meta-grid__item">
            <div class="lp-meta-grid__label">Step 타입</div>
            <div class="lp-meta-grid__value lp-mono">{{ selectedLog.step_type }}</div>
          </div>
          <div class="lp-meta-grid__item">
            <div class="lp-meta-grid__label">상태</div>
            <div class="lp-meta-grid__value">
              <span class="lp-status-chip" :class="statusChipClass(selectedLog.status)">
                {{ selectedLog.status }}
              </span>
            </div>
          </div>
          <div class="lp-meta-grid__item">
            <div class="lp-meta-grid__label">시작</div>
            <div class="lp-meta-grid__value lp-mono">{{ fmtDate(selectedLog.started_at) }}</div>
          </div>
          <div class="lp-meta-grid__item">
            <div class="lp-meta-grid__label">종료</div>
            <div class="lp-meta-grid__value lp-mono">{{ fmtDate(selectedLog.ended_at) }}</div>
          </div>
        </div>

        <div class="lp-log-panel__divider" />

        <!-- Collected data -->
        <div class="lp-log-panel__data-label">수집 데이터</div>
        <div
          v-if="selectedLog.data_collected && selectedLog.status === '오류'"
          class="lp-data-box lp-data-box--error"
        >
          <pre>{{ JSON.stringify(selectedLog.data_collected, null, 2) }}</pre>
        </div>
        <div
          v-else-if="selectedLog.data_collected"
          class="lp-data-box"
        >
          <pre>{{ JSON.stringify(selectedLog.data_collected, null, 2) }}</pre>
        </div>
        <div v-else class="lp-log-panel__no-data">없음</div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from 'src/stores/auth'
import { useWorkflows } from 'src/composables/useWorkflows'

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

type SortKey = 'step_name' | 'step_type' | 'status' | 'started_at'
const sortKey = ref<SortKey>('started_at')
const sortAsc = ref(false)

const sortedLogs = computed(() => {
  const k = sortKey.value
  return [...logs.value].sort((a, b) => {
    const va = a[k] ?? ''
    const vb = b[k] ?? ''
    const cmp = String(va).localeCompare(String(vb), 'ko')
    return sortAsc.value ? cmp : -cmp
  })
})

function setSort(k: SortKey) {
  if (sortKey.value === k) sortAsc.value = !sortAsc.value
  else { sortKey.value = k; sortAsc.value = true }
}

const filterWorkflowId = ref<number | null>(null)
const filterStepType = ref<string | null>(null)
const filterStatus = ref<string | null>(null)

const stepTypeOptions = ['weighing', 'mixing', 'forming', 'firing', 'heattreat', 'machining', 'analysis']

const workflowOptions = computed(() =>
  workflows.value.map((w) => ({ label: w.name, value: w.id }))
)

function statusChipClass(s: string) {
  switch (s) {
    case '완료':   return 'lp-status-chip--green'
    case '진행중': return 'lp-status-chip--blue'
    case '오류':   return 'lp-status-chip--red'
    default:       return 'lp-status-chip--grey'
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

<style scoped>
.lp-page { padding: 24px; }

/* ── Page head ── */
.lp-page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.lp-page-head__title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--t1);
  margin: 0 0 3px;
}

.lp-page-head__sub {
  font-size: 11px;
  color: var(--t3);
}

/* ── Filter bar ── */
.lp-filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.lp-select :deep(.q-field__control) {
  background: var(--s2) !important;
  border-color: var(--bd) !important;
}

.lp-select :deep(.q-field__native),
.lp-select :deep(.q-field__input) {
  color: var(--t1) !important;
}

.lp-select :deep(.q-field__label) {
  color: var(--t3) !important;
}

.lp-btn-ghost {
  color: var(--t2) !important;
  border: 1px solid var(--bd) !important;
  border-radius: var(--r1) !important;
}

/* ── Layout ── */
.lp-log-layout {
  display: flex;
  gap: 16px;
}

.lp-log-layout--split .lp-log-table-wrap {
  flex: 7;
  min-width: 0;
}

.lp-log-table-wrap {
  flex: 1;
  min-width: 0;
}

/* ── Loading / empty ── */
.lp-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.lp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 8px;
}

.lp-empty__title {
  font-size: 15px;
  color: var(--t2);
  font-weight: 500;
}

.lp-empty__sub {
  font-size: 12px;
  color: var(--t3);
}

/* ── Table ── */
.lp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.lp-table th {
  background: var(--s2);
  color: var(--t3);
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid var(--bd);
  white-space: nowrap;
  user-select: none;
}

.lp-table__sortable {
  cursor: pointer;
}

.lp-table__sortable:hover {
  color: var(--t1);
}

.lp-sort-icon {
  font-size: 9px;
  opacity: 0.6;
  margin-left: 3px;
}

.lp-table__row {
  border-bottom: 1px solid var(--bd);
  cursor: pointer;
  transition: background 0.1s;
}

.lp-table__row:hover {
  background: var(--s2);
}

.lp-table__row--active {
  background: var(--accent-bg) !important;
  border-left: 2px solid var(--accent);
}

.lp-table td {
  padding: 9px 12px;
  color: var(--t1);
  vertical-align: middle;
}

.lp-table__name {
  font-weight: 500;
  min-width: 120px;
}

.lp-table__type {
  color: var(--t2) !important;
  font-size: 11px;
}

.lp-table__summary {
  color: var(--t3) !important;
  font-size: 11px;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lp-table__date {
  color: var(--t3) !important;
  font-size: 11px;
  white-space: nowrap;
}

/* ── Side panel ── */
.lp-log-panel {
  flex: 5;
  background: var(--s1);
  border: 1px solid var(--bd);
  border-radius: var(--r2);
  padding: 18px;
  min-width: 260px;
  align-self: flex-start;
  position: sticky;
  top: 16px;
}

.lp-log-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.lp-log-panel__title {
  font-size: 13px;
  font-weight: 600;
  color: var(--t1);
  line-height: 1.4;
}

.lp-icon-btn {
  color: var(--t3) !important;
  flex-shrink: 0;
}

.lp-icon-btn:hover {
  color: var(--t1) !important;
}

/* ── Meta grid ── */
.lp-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 0;
}

.lp-meta-grid__label {
  font-size: 10px;
  color: var(--t3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 3px;
}

.lp-meta-grid__value {
  font-size: 12px;
  color: var(--t1);
}

.lp-log-panel__divider {
  height: 1px;
  background: var(--bd);
  margin: 14px 0;
}

.lp-log-panel__data-label {
  font-size: 10px;
  color: var(--t3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

/* ── Data box ── */
.lp-data-box {
  background: var(--s2);
  border: 1px solid var(--bd);
  border-radius: var(--r1);
  padding: 10px 12px;
  overflow: auto;
  max-height: 320px;
}

.lp-data-box--error {
  background: var(--red-bg);
  border-color: var(--red-bd);
}

.lp-data-box pre {
  font-family: var(--mono) !important;
  font-size: 11px;
  color: var(--t1);
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.lp-data-box--error pre {
  color: var(--red);
}

.lp-log-panel__no-data {
  font-size: 12px;
  color: var(--t3);
}

/* ── Pulse dot ── */
.lp-pulse-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
  animation: lp-pulse 1.4s ease infinite;
}

/* ── Mono ── */
.lp-mono {
  font-family: var(--mono) !important;
}
</style>
