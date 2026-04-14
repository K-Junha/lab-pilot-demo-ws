<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">완료 실험 결과</div>

    <div v-if="loading" class="flex flex-center q-pa-xl">
      <q-spinner size="48px" color="primary" />
    </div>

    <div v-else-if="!selectedResult">
      <div v-if="results.length === 0" class="text-center text-grey q-mt-xl">
        <q-icon name="science" size="64px" color="grey-5" class="q-mb-md" />
        <div class="text-h6">완료된 실험이 없습니다</div>
      </div>

      <div class="row q-gutter-md">
        <q-card
          v-for="r in results"
          :key="r.result_id"
          class="col-xs-12 col-sm-5 col-md-3 cursor-pointer"
          flat
          bordered
          @click="selectResult(r)"
        >
          <q-card-section>
            <div class="text-subtitle1">실험 #{{ r.result_id }}</div>
            <div class="text-caption text-grey">{{ fmtDate(r.created_at) }}</div>
          </q-card-section>
          <q-card-section v-if="r.notes" class="q-pt-none">
            <div class="text-caption ellipsis-2-lines text-grey-7">{{ r.notes }}</div>
          </q-card-section>
          <q-card-section v-else class="q-pt-none text-caption text-grey-5">
            노트 없음
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- 상세 뷰 -->
    <div v-else>
      <q-btn flat icon="arrow_back" label="목록으로" @click="selectedResult = null" class="q-mb-md" />
      <q-card flat bordered class="q-pa-md">
        <div class="text-h6 q-mb-md">실험 #{{ selectedResult.result_id }}</div>
        <div class="text-caption text-grey q-mb-md">완료일: {{ fmtDate(selectedResult.created_at) }}</div>

        <div class="text-subtitle2 q-mb-xs">노트</div>
        <q-input
          v-model="editNotes"
          type="textarea"
          outlined
          autogrow
          class="q-mb-md"
        />
        <q-btn color="primary" label="저장" :loading="saving" @click="saveNotes" />
      </q-card>
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
