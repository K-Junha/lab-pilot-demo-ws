<template>
  <q-page class="lp-page">
    <!-- Page header -->
    <div class="lp-page-head">
      <div>
        <h1 class="lp-page-head__title">완료 실험 결과</h1>
        <div v-if="!loading" class="lp-page-head__sub lp-mono">총 {{ results.length }}건</div>
      </div>
      <div class="lp-page-head__actions">
        <q-btn flat dense no-caps icon="download" label="내보내기" class="lp-btn-ghost" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="lp-loading">
      <q-spinner size="28px" style="color: var(--accent);" />
    </div>

    <!-- Empty state -->
    <div v-else-if="results.length === 0" class="lp-empty">
      <q-icon name="science" size="48px" style="color: var(--t4);" />
      <div class="lp-empty__title">완료된 실험이 없습니다</div>
      <div class="lp-empty__sub">실험을 완료하면 여기에 결과가 표시됩니다</div>
    </div>

    <!-- Main layout -->
    <div v-else class="lp-results-layout">
      <!-- Card list -->
      <div class="lp-results-list">
        <div
          v-for="r in results"
          :key="r.result_id"
          class="lp-result-card"
          :class="{ 'lp-result-card--active': selectedResult?.result_id === r.result_id }"
          @click="selectResult(r)"
        >
          <div class="lp-result-card__num lp-mono">#{{ r.result_id }}</div>
          <div class="lp-result-card__date lp-mono">{{ fmtDate(r.created_at) }}</div>
          <div class="lp-result-card__notes">{{ r.notes || '노트 없음' }}</div>
        </div>
      </div>

      <!-- Detail pane -->
      <div class="lp-result-detail">
        <div v-if="!selectedResult" class="lp-result-detail__placeholder">
          <q-icon name="analytics" size="36px" style="color: var(--t4);" />
          <div style="font-size: 13px; color: var(--t3); margin-top: 8px;">결과를 선택하세요</div>
        </div>

        <template v-else>
          <div class="lp-result-detail__head">
            <div class="lp-result-detail__id lp-mono">#{{ selectedResult.result_id }}</div>
            <div class="lp-result-detail__date lp-mono">{{ fmtDate(selectedResult.created_at) }}</div>
          </div>

          <!-- Summary grid -->
          <div class="lp-result-summary">
            <div class="lp-result-summary__item">
              <div class="lp-result-summary__label">완료일</div>
              <div class="lp-result-summary__value lp-mono">{{ fmtDate(selectedResult.created_at) }}</div>
            </div>
            <div class="lp-result-summary__item">
              <div class="lp-result-summary__label">워크플로우 ID</div>
              <div class="lp-result-summary__value lp-mono">{{ selectedResult.workflow_id }}</div>
            </div>
            <div class="lp-result-summary__item">
              <div class="lp-result-summary__label">상태</div>
              <div class="lp-result-summary__value">
                <span class="lp-status-chip lp-status-chip--green">완료</span>
              </div>
            </div>
          </div>

          <div class="lp-result-detail__divider" />

          <!-- Notes editor -->
          <div class="lp-result-detail__section-label">노트</div>
          <q-input
            v-model="editNotes"
            type="textarea"
            outlined
            autogrow
            class="lp-notes-input q-mb-sm"
            placeholder="실험 메모를 입력하세요..."
          />
          <div class="lp-result-detail__actions">
            <q-btn
              unelevated no-caps
              label="저장"
              class="lp-btn-primary"
              :loading="saving"
              @click="saveNotes"
            />
          </div>

          <div class="lp-result-detail__divider" />

          <!-- Chart placeholder -->
          <div class="lp-chart-placeholder">
            <q-icon name="bar_chart" size="28px" style="color: var(--t4);" />
            <div style="font-size: 11px; color: var(--t3); margin-top: 6px;">차트 영역 (추후 구현)</div>
          </div>
        </template>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'

const API_BASE = 'http://localhost:8000/api'

interface ResultRow {
  result_id: number
  workflow_id: number
  notes: string | null
  created_at: string
  updated_at: string
}

const $q = useQuasar()
const authStore = useAuthStore()

const results = ref<ResultRow[]>([])
const loading = ref(false)
const selectedResult = ref<ResultRow | null>(null)
const editNotes = ref('')
const saving = ref(false)

function fmtDate(v: string) {
  return new Date(v).toLocaleString('ko-KR')
}

function authHeader() {
  return { Authorization: `Bearer ${authStore.token ?? ''}`, 'Content-Type': 'application/json' }
}

async function loadResults() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/results`, { headers: authHeader() })
    if (!res.ok) throw new Error()
    results.value = await res.json() as ResultRow[]
  } finally {
    loading.value = false
  }
}

function selectResult(r: ResultRow) {
  selectedResult.value = r
  editNotes.value = r.notes ?? ''
}

async function saveNotes() {
  if (!selectedResult.value) return
  saving.value = true
  try {
    const res = await fetch(`${API_BASE}/results/${selectedResult.value.result_id}`, {
      method: 'PATCH',
      headers: authHeader(),
      body: JSON.stringify({ notes: editNotes.value }),
    })
    if (!res.ok) throw new Error()
    const updated = await res.json() as ResultRow
    selectedResult.value = updated
    const idx = results.value.findIndex((r) => r.result_id === updated.result_id)
    if (idx !== -1) results.value[idx] = updated
    $q.notify({ type: 'positive', message: '노트가 저장되었습니다.' })
  } catch {
    $q.notify({ type: 'negative', message: '저장 실패' })
  } finally {
    saving.value = false
  }
}

onMounted(() => void loadResults())
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

.lp-page-head__actions {
  display: flex;
  gap: 8px;
}

.lp-btn-ghost {
  color: var(--t2) !important;
  border: 1px solid var(--bd) !important;
  border-radius: var(--r1) !important;
  font-size: 12px;
}

.lp-btn-primary {
  background: var(--accent) !important;
  color: white !important;
  font-size: 12px;
  border-radius: var(--r1) !important;
  padding: 6px 16px !important;
}

/* ── Loading / empty ── */
.lp-loading {
  display: flex;
  justify-content: center;
  padding: 80px 0;
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

/* ── Main layout ── */
.lp-results-layout {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

/* ── Card list ── */
.lp-results-list {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lp-result-card {
  background: var(--s1);
  border: 1px solid var(--bd);
  border-left: 2px solid transparent;
  border-radius: var(--r1);
  padding: 12px 14px;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
}

.lp-result-card:hover {
  background: var(--s2);
}

.lp-result-card--active {
  background: var(--accent-bg) !important;
  border-color: var(--accent-bd);
  border-left-color: var(--accent);
}

.lp-result-card__num {
  font-size: 15px;
  font-weight: 700;
  color: var(--t1);
  margin-bottom: 2px;
}

.lp-result-card--active .lp-result-card__num {
  color: var(--accent);
}

.lp-result-card__date {
  font-size: 10px;
  color: var(--t3);
  margin-bottom: 6px;
}

.lp-result-card__notes {
  font-size: 11px;
  color: var(--t2);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* ── Detail pane ── */
.lp-result-detail {
  flex: 1;
  min-width: 0;
  background: var(--s1);
  border: 1px solid var(--bd);
  border-radius: var(--r2);
  padding: 22px;
}

.lp-result-detail__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

.lp-result-detail__head {
  margin-bottom: 16px;
}

.lp-result-detail__id {
  font-size: 20px;
  font-weight: 700;
  color: var(--t1);
  margin-bottom: 4px;
}

.lp-result-detail__date {
  font-size: 11px;
  color: var(--t3);
}

/* ── Summary grid ── */
.lp-result-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.lp-result-summary__label {
  font-size: 10px;
  color: var(--t3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.lp-result-summary__value {
  font-size: 13px;
  color: var(--t1);
}

.lp-result-detail__divider {
  height: 1px;
  background: var(--bd);
  margin: 16px 0;
}

.lp-result-detail__section-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--t2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

/* ── Notes input ── */
.lp-notes-input :deep(.q-field__control) {
  background: var(--s2) !important;
  border-color: var(--bd) !important;
}

.lp-notes-input :deep(.q-field__native) {
  color: var(--t1) !important;
  font-size: 13px;
  min-height: 80px;
}

.lp-result-detail__actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0;
}

/* ── Chart placeholder ── */
.lp-chart-placeholder {
  background: var(--s2);
  border: 1px dashed var(--bd2);
  border-radius: var(--r1);
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* ── Mono ── */
.lp-mono {
  font-family: var(--mono) !important;
}
</style>
