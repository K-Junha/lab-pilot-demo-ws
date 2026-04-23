<template>
  <div>
    <!-- 컨트롤 + 저울 연결 상태 -->
    <div class="row items-center q-gutter-md q-mb-md">
      <q-btn
        v-if="execution.status === 'pending'"
        color="primary"
        icon="play_arrow"
        label="칭량 시작"
        :disable="canStart === false"
        @click="$emit('start')"
      >
        <q-tooltip v-if="canStart === false">이전 스텝을 먼저 완료하세요</q-tooltip>
      </q-btn>
      <q-btn
        v-if="execution.status === 'running'"
        color="negative"
        icon="stop"
        label="칭량 완료"
        @click="$emit('stop')"
      />
      <q-badge v-if="execution.status === 'completed'" color="green" class="text-body2 q-pa-sm">
        <q-icon name="check_circle" class="q-mr-xs" /> 칭량 완료
      </q-badge>
      <q-space />
      <!-- 전체 진행률 -->
      <span class="text-caption text-grey q-mr-sm">
        {{ completedCompCount }}/{{ compositions.length }} 조성 완료
      </span>
      <q-badge :color="balanceConnected ? 'green' : 'red'" class="q-pa-sm">
        <q-icon name="scale" class="q-mr-xs" />
        저울 {{ balanceConnected ? 'ONLINE' : 'OFFLINE' }}
      </q-badge>
    </div>

    <!-- 조성 없음 -->
    <div v-if="compositions.length === 0" class="text-grey text-center q-pa-lg">
      조성이 등록되지 않았습니다
    </div>

    <template v-else>
      <!-- 조성 선택 -->
      <div class="row items-center q-gutter-md q-mb-md">
        <q-select
          v-model="activeCompId"
          :options="compOptions"
          option-value="value"
          option-label="label"
          emit-value
          map-options
          dense
          outlined
          style="min-width: 320px;"
          label="조성 선택"
        >
          <template #option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section avatar>
                <q-icon
                  :name="scope.opt.done ? 'check_circle' : scope.opt.partial ? 'hourglass_top' : 'radio_button_unchecked'"
                  :color="scope.opt.done ? 'green' : scope.opt.partial ? 'orange' : 'grey'"
                  size="sm"
                />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ scope.opt.label }} <span class="text-caption text-grey">({{ scope.opt.progress }})</span></q-item-label>
              </q-item-section>
            </q-item>
          </template>
          <template #selected-item>
            <div class="row items-center no-wrap q-gutter-xs">
              <q-icon
                :name="isCompComplete(activeComp!) ? 'check_circle' : hasCompAnyRecord(activeComp!) ? 'hourglass_top' : 'radio_button_unchecked'"
                :color="isCompComplete(activeComp!) ? 'green' : hasCompAnyRecord(activeComp!) ? 'orange' : 'grey'"
                size="xs"
              />
              <span>{{ activeComp?.name || `조성 #${activeCompId}` }}</span>
              <span class="text-caption text-grey">({{ activeCompProgress }})</span>
            </div>
          </template>
        </q-select>

        <!-- 이전/다음 버튼 -->
        <q-btn flat dense icon="chevron_left" :disable="activeCompIdx <= 0" @click="activeCompIdx--" />
        <q-btn flat dense icon="chevron_right" :disable="activeCompIdx >= compositions.length - 1" @click="activeCompIdx++" />
      </div>

      <!-- Pending 상태: 안내 메시지 -->
      <div v-if="execution.status === 'pending'" class="q-mb-md">
        <q-banner dense rounded :class="isDark ? 'bg-blue-10 text-blue-3' : 'bg-blue-1 text-blue-9'">
          <template #avatar>
            <q-icon name="info" />
          </template>
          "칭량 시작"을 누르면 저울이 연결되고 조성별로 원료 칭량을 진행합니다.
        </q-banner>
      </div>

      <!-- 현재 선택된 조성 -->
      <template v-if="activeComp">
        <!-- 현재 칭량 중인 원료 카드 -->
        <div v-if="execution.status === 'running' && currentOxide" class="q-mb-md">
          <q-card flat bordered :class="cardBgClass">
            <q-card-section>
              <div class="row items-center q-gutter-md">
                <!-- 현재 무게 디스플레이 -->
                <div class="col-auto text-center">
                  <div class="text-caption text-grey q-mb-xs">현재 무게</div>
                  <div :class="`text-h3 text-weight-bold text-${weightStateColor}`">
                    {{ balanceWeight.toFixed(4) }}
                    <span class="text-body1">g</span>
                  </div>
                </div>

                <!-- 구분선 -->
                <q-separator vertical />

                <!-- 원료 정보 + 프로그레스 -->
                <div class="col">
                  <div class="row items-center q-mb-xs">
                    <div class="text-subtitle1 text-weight-bold q-mr-sm">
                      {{ currentOxide.oxide }}
                    </div>
                    <q-badge :color="weightStateColor" class="q-mr-sm">
                      {{ weightStateLabel }}
                    </q-badge>
                    <q-space />
                    <div class="text-caption text-grey">
                      목표: <strong>{{ targetG(activeComp, currentOxide) }} g</strong>
                    </div>
                  </div>

                  <!-- 프로그레스 바 -->
                  <q-linear-progress
                    :value="progressValue"
                    :color="weightStateColor"
                    size="20px"
                    rounded
                    class="q-mb-xs"
                  />

                  <div class="row justify-between text-caption">
                    <span :class="`text-${weightStateColor}`">
                      {{ progressPct }}%
                    </span>
                    <span :class="deviationClass">
                      {{ deviationLabel }}
                    </span>
                  </div>
                </div>

                <!-- 기록 버튼 -->
                <div class="col-auto">
                  <q-btn
                    color="primary"
                    icon="save"
                    label="기록"
                    size="lg"
                    :disable="!balanceConnected"
                    @click="recordWeight"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- 원료 선택 chip (수동 선택) -->
          <div class="row q-gutter-xs q-mt-sm">
            <q-chip
              v-for="(ox, i) in activeComp.oxides"
              :key="ox.oxide"
              :color="chipColor(ox)"
              text-color="white"
              clickable
              :selected="currentOxideIdx === i"
              @click="currentOxideIdx = i"
            >
              {{ ox.oxide }}
              <q-icon v-if="isRecorded(ox)" name="check" class="q-ml-xs" size="xs" />
            </q-chip>
          </div>
        </div>

        <!-- 전체 원료 칭량 현황 테이블 -->
        <div class="text-subtitle2 q-mb-xs q-mt-md">
          {{ activeComp.name || `조성 #${activeComp.id}` }} — 원료별 칭량 현황
        </div>
        <q-markup-table flat bordered dense>
          <thead>
            <tr>
              <th class="text-left" style="width: 40px">#</th>
              <th class="text-left">원료</th>
              <th class="text-right">배합비 (%)</th>
              <th class="text-right">목표량 (g)</th>
              <th class="text-right">실칭량 (g)</th>
              <th class="text-right">오차 (g)</th>
              <th class="text-right">오차율</th>
              <th class="text-center">판정</th>
              <th class="text-center">조작</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(ox, i) in activeComp.oxides"
              :key="ox.oxide"
              :class="{ [isDark ? 'bg-blue-10' : 'bg-blue-1']: execution.status === 'running' && currentOxideIdx === i }"
            >
              <td class="text-center">{{ i + 1 }}</td>
              <td>
                {{ ox.oxide }}
                <q-icon
                  v-if="execution.status === 'running' && currentOxideIdx === i"
                  name="arrow_forward"
                  color="blue"
                  size="xs"
                  class="q-ml-xs"
                />
              </td>
              <td class="text-right">{{ ox.wt }}</td>
              <td class="text-right">{{ targetG(activeComp, ox) }}</td>
              <td class="text-right">{{ rowActualG(ox) ?? '-' }}</td>
              <td class="text-right">{{ rowErrorG(activeComp, ox) }}</td>
              <td class="text-right">{{ rowErrorPct(activeComp, ox) }}</td>
              <td class="text-center">
                <q-badge :color="passColor(activeComp, ox)">{{ passLabel(activeComp, ox) }}</q-badge>
              </td>
              <td class="text-center">
                <q-btn
                  v-if="isRecorded(ox) && execution.status === 'running'"
                  flat dense icon="refresh" size="xs" color="orange"
                  @click="currentOxideIdx = i"
                />
                <q-btn
                  v-else-if="!isRecorded(ox) && execution.status === 'running'"
                  flat dense icon="radio_button_unchecked" size="xs" color="grey"
                  @click="currentOxideIdx = i"
                />
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr :class="isDark ? 'bg-grey-10' : 'bg-grey-2'">
              <td colspan="4" class="text-right text-weight-bold">합계</td>
              <td class="text-right text-weight-bold">{{ totalActualG }}</td>
              <td class="text-right text-weight-bold">{{ totalErrorG }}</td>
              <td colspan="3"></td>
            </tr>
          </tfoot>
        </q-markup-table>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { useBalanceWs } from 'src/composables/useBalanceWs'
import type { CompositionData, CompositionRow, StepExecution, WeighingData } from 'src/components/workflow/types'

const stepData = defineModel<WeighingData>('stepData', { required: true })
const props = defineProps<{
  execution: StepExecution
  compositions: CompositionData[]
  canStart?: boolean
}>()

defineEmits<{
  start: []
  stop: []
}>()

// ── 저울 WebSocket ─────────────────────────────────────
const $q = useQuasar()
const isDark = computed(() => $q.dark.isActive)

const cardBgClass = computed(() => {
  const c = weightStateColor.value
  return isDark.value ? `bg-${c}-10` : `bg-${c}-1`
})
const { weight: balanceWeight, connected: balanceConnected, connect: connectBalance, disconnect: disconnectBalance } = useBalanceWs()

onMounted(() => { connectBalance() })
onUnmounted(() => disconnectBalance())

// ── rows 초기화 보장 (중첩 구조: { [compId]: { [oxide]: { actualG } } }) ──
if (!stepData.value.rows) stepData.value.rows = {}

// ── 조성 선택 ──────────────────────────────────────────
const activeCompId = ref<number>(props.compositions[0]?.id ?? 0)

const activeComp = computed<CompositionData | null>(() =>
  props.compositions.find(c => c.id === activeCompId.value) ?? null
)

const activeCompIdx = computed({
  get: () => props.compositions.findIndex(c => c.id === activeCompId.value),
  set: (idx: number) => {
    if (idx >= 0 && idx < props.compositions.length) {
      activeCompId.value = props.compositions[idx]!.id
    }
  }
})

const compOptions = computed(() =>
  props.compositions.map(comp => {
    const done = isCompComplete(comp)
    const partial = hasCompAnyRecord(comp)
    const recorded = comp.oxides.filter(ox => {
      const rows = stepData.value.rows?.[comp.id]
      return rows?.[ox.oxide]?.actualG != null
    }).length
    return {
      label: comp.name || `조성 #${comp.id}`,
      value: comp.id,
      done,
      partial,
      progress: `진행률: ${comp.oxides.length === 0 ? 0 : Math.round((recorded / comp.oxides.length) * 100)}%`,
    }
  })
)

const activeCompProgress = computed(() => {
  const comp = activeComp.value
  if (!comp || comp.oxides.length === 0) return '진행률: 0%'
  const rows = stepData.value.rows?.[comp.id]
  if (!rows) return '진행률: 0%'
  const recorded = comp.oxides.filter(ox => rows[ox.oxide]?.actualG != null).length
  return `진행률: ${Math.round((recorded / comp.oxides.length) * 100)}%`
})

// 조성별 rows 접근 헬퍼
function compRows(compId: number) {
  if (!stepData.value.rows[compId]) stepData.value.rows[compId] = {}
  return stepData.value.rows[compId]
}

function getRow(oxide: string) {
  const rows = compRows(activeCompId.value)
  if (!rows[oxide]) rows[oxide] = { actualG: null }
  return rows[oxide]
}

// ── 조성별 완료 상태 ───────────────────────────────────
function isCompComplete(comp: CompositionData): boolean {
  const rows = stepData.value.rows?.[comp.id]
  if (!rows) return false
  return comp.oxides.length > 0 && comp.oxides.every(ox => rows[ox.oxide]?.actualG != null)
}

function hasCompAnyRecord(comp: CompositionData): boolean {
  const rows = stepData.value.rows?.[comp.id]
  if (!rows) return false
  return comp.oxides.some(ox => rows[ox.oxide]?.actualG != null)
}

const completedCompCount = computed(() =>
  props.compositions.filter(c => isCompComplete(c)).length
)

// ── 현재 칭량 중인 원료 인덱스 ─────────────────────────
const currentOxideIdx = ref(0)

// 탭 변경 시 첫 미기록 원료로 이동
watch(activeCompId, () => {
  const comp = activeComp.value
  if (!comp) return
  const first = comp.oxides.findIndex(ox => !isRecorded(ox))
  currentOxideIdx.value = first >= 0 ? first : 0
})

// 시작 시 첫 미기록 원료로 이동
watch(() => props.execution.status, (status) => {
  if (status === 'running') {
    const first = activeComp.value?.oxides.findIndex(ox => !isRecorded(ox)) ?? 0
    currentOxideIdx.value = first >= 0 ? first : 0
  }
})

const currentOxide = computed<CompositionRow | null>(() =>
  activeComp.value?.oxides[currentOxideIdx.value] ?? null
)

// ── 목표량 계산 ────────────────────────────────────────
function targetG(comp: CompositionData, ox: CompositionRow): string {
  if (!comp.batchWeight) return '-'
  return ((ox.wt / 100) * comp.batchWeight).toFixed(3)
}

function targetGNum(comp: CompositionData, ox: CompositionRow): number | null {
  if (!comp.batchWeight) return null
  return (ox.wt / 100) * comp.batchWeight
}

// ── 실칭량/오차 ────────────────────────────────────────
function rowActualG(ox: CompositionRow): number | null {
  return getRow(ox.oxide).actualG
}

function rowErrorG(comp: CompositionData, ox: CompositionRow): string {
  const t = targetGNum(comp, ox)
  const a = rowActualG(ox)
  if (a == null || t == null) return '-'
  return (a - t).toFixed(3)
}

function rowErrorPct(comp: CompositionData, ox: CompositionRow): string {
  const t = targetGNum(comp, ox)
  const a = rowActualG(ox)
  if (a == null || t == null || t === 0) return '-'
  return ((a - t) / t * 100).toFixed(2) + '%'
}

function isRecorded(ox: CompositionRow): boolean {
  return getRow(ox.oxide).actualG != null
}

// ── 현재 무게 상태 ─────────────────────────────────────
const progressValue = computed(() => {
  if (!currentOxide.value || !activeComp.value) return 0
  const t = targetGNum(activeComp.value, currentOxide.value)
  if (t == null || t === 0) return 0
  return Math.min(balanceWeight.value / t, 1.1)
})

const progressPct = computed(() => {
  if (!currentOxide.value || !activeComp.value) return '0.0'
  const t = targetGNum(activeComp.value, currentOxide.value)
  if (t == null || t === 0) return '0.0'
  return Math.min((balanceWeight.value / t) * 100, 999.9).toFixed(1)
})

const weightStateColor = computed(() => {
  if (!currentOxide.value || !activeComp.value) return 'grey'
  const t = targetGNum(activeComp.value, currentOxide.value)
  if (t == null || t === 0) return 'grey'
  const pct = (balanceWeight.value / t) * 100
  if (pct > 102) return 'red'
  if (pct >= 98) return 'green'
  return 'blue'
})

const weightStateLabel = computed(() => {
  if (!currentOxide.value || !activeComp.value) return '-'
  const t = targetGNum(activeComp.value, currentOxide.value)
  if (t == null || t === 0) return '-'
  const pct = (balanceWeight.value / t) * 100
  if (pct > 102) return '초과'
  if (pct >= 98) return '목표 근접'
  return '부족'
})

const deviationLabel = computed(() => {
  if (!currentOxide.value || !activeComp.value) return ''
  const t = targetGNum(activeComp.value, currentOxide.value)
  if (t == null) return ''
  const diff = balanceWeight.value - t
  const sign = diff >= 0 ? '+' : ''
  return `${sign}${diff.toFixed(3)} g`
})

const deviationClass = computed(() => {
  if (!currentOxide.value || !activeComp.value) return 'text-grey'
  const t = targetGNum(activeComp.value, currentOxide.value)
  if (t == null || t === 0) return 'text-grey'
  const pct = (balanceWeight.value / t) * 100
  if (pct > 102) return 'text-red text-weight-bold'
  if (pct >= 98) return 'text-green'
  return 'text-blue'
})

// ── 기록 버튼 ──────────────────────────────────────────
function recordWeight() {
  if (!currentOxide.value || !activeComp.value) return
  if (balanceWeight.value <= 0) {
    $q.notify({ type: 'warning', message: '저울 값이 0 이하입니다. 확인해주세요.' })
    return
  }
  const recorded = Math.round(balanceWeight.value * 10000) / 10000
  getRow(currentOxide.value.oxide).actualG = recorded
  $q.notify({ type: 'positive', message: `${currentOxide.value.oxide}: ${recorded}g 기록 완료` })

  // 다음 미기록 원료로 자동 이동
  const oxides = activeComp.value.oxides
  const next = oxides.findIndex((ox, i) => i > currentOxideIdx.value && !isRecorded(ox))
  if (next >= 0) {
    currentOxideIdx.value = next
  } else {
    const first = oxides.findIndex(ox => !isRecorded(ox))
    if (first >= 0) {
      currentOxideIdx.value = first
    } else if (isCompComplete(activeComp.value)) {
      // 현재 조성 완료 → 다음 미완료 조성으로 자동 이동
      const nextComp = props.compositions.find(c => c.id !== activeCompId.value && !isCompComplete(c))
      if (nextComp) {
        $q.notify({ type: 'info', message: `${activeComp.value.name || `조성 #${activeComp.value.id}`} 완료! 다음 조성으로 이동합니다.` })
        activeCompId.value = nextComp.id
      }
    }
  }
}

// ── 판정 ───────────────────────────────────────────────
function passColor(comp: CompositionData, ox: CompositionRow): string {
  const a = rowActualG(ox)
  if (a == null) return 'grey'
  const t = targetGNum(comp, ox)
  if (t == null || t === 0) return 'grey'
  const pct = Math.abs((a - t) / t * 100)
  return pct <= 1 ? 'green' : pct <= 3 ? 'orange' : 'red'
}

function passLabel(comp: CompositionData, ox: CompositionRow): string {
  const a = rowActualG(ox)
  if (a == null) return '미측정'
  const t = targetGNum(comp, ox)
  if (t == null || t === 0) return '-'
  const pct = Math.abs((a - t) / t * 100)
  return pct <= 1 ? 'PASS' : pct <= 3 ? 'WARNING' : 'FAIL'
}

function chipColor(ox: CompositionRow): string {
  if (!activeComp.value) return 'grey'
  if (isRecorded(ox)) return passColor(activeComp.value, ox)
  return 'grey'
}

// ── 합계 ───────────────────────────────────────────────
const totalActualG = computed(() => {
  if (!activeComp.value) return '-'
  const vals = activeComp.value.oxides.map(ox => rowActualG(ox)).filter(v => v != null)
  if (vals.length === 0) return '-'
  return vals.reduce((a, b) => a + b, 0).toFixed(3)
})

const totalErrorG = computed(() => {
  if (!activeComp.value) return '-'
  const oxides = activeComp.value.oxides
  const errors = oxides.map(ox => {
    const a = rowActualG(ox)
    const t = targetGNum(activeComp.value!, ox)
    return a != null && t != null ? a - t : null
  }).filter(v => v != null)
  if (errors.length === 0) return '-'
  const sum = errors.reduce((a, b) => a + b, 0)
  return (sum >= 0 ? '+' : '') + sum.toFixed(3)
})
</script>
