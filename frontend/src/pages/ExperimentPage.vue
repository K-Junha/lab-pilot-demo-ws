<template>
  <q-page class="lp-page">
    <!-- Top bar -->
    <div class="lp-exp-topbar">
      <div class="lp-exp-topbar__left">
        <q-select
          outlined dense
          v-model="selectedWorkflowId"
          :options="workflowOptions"
          option-value="value"
          option-label="label"
          emit-value map-options
          label="워크플로우 선택"
          style="min-width: 260px;"
          :disable="!!currentRun && currentRun.status === 'running'"
          class="lp-select"
        />
        <span v-if="currentRun" class="lp-status-chip" :class="runStatusChipClass">
          <span v-if="currentRun.status === 'running'" class="lp-pulse-dot" />
          {{ runStatusLabel }}
        </span>
        <q-btn
          v-if="selectedWorkflow && selectedWorkflow.status === '진행중' && !currentRun"
          unelevated no-caps icon="science" label="실험 생성"
          class="lp-btn-primary"
          @click="onCreateRun"
        />
        <div
          v-if="selectedWorkflow && selectedWorkflow.status === '계획중'"
          class="lp-exp-topbar__hint"
        >
          <q-icon name="lock" size="13px" style="color: var(--orange);" />
          계획중 — 워크플로우 페이지에서 실험을 시작하세요
        </div>
      </div>
      <q-btn
        v-if="currentRun && allStepsCompleted && selectedWorkflow?.status === '진행중'"
        unelevated no-caps icon="check_circle" label="실험 완료"
        class="lp-btn-success"
        @click="onCompleteExperiment"
      />
    </div>

    <!-- Empty states -->
    <div v-if="!currentRun && workflows.length === 0" class="lp-empty">
      <q-icon name="account_tree" size="48px" style="color: var(--t4);" />
      <div class="lp-empty__title">먼저 워크플로우를 생성하세요</div>
      <q-btn flat no-caps label="워크플로우 페이지로 이동" icon="arrow_forward" style="color: var(--accent);" @click="router.push('/workflow')" />
    </div>
    <div v-else-if="!currentRun" class="lp-empty">
      <q-icon name="science" size="48px" style="color: var(--t4);" />
      <div class="lp-empty__title">워크플로우를 선택하고 실험을 생성하세요</div>
    </div>

    <template v-else>
      <!-- Step timeline track -->
      <div class="lp-card lp-timeline-card">
        <div class="lp-timeline">
          <template v-for="(exec, i) in currentRun.steps" :key="exec.uid">
            <!-- Step circle -->
            <div class="lp-timeline__step" @click="activeStepUid = exec.uid">
              <div
                class="lp-timeline__circle"
                :class="{
                  'lp-timeline__circle--done':    exec.status === 'completed',
                  'lp-timeline__circle--running': exec.status === 'running',
                  'lp-timeline__circle--active':  activeStepUid === exec.uid,
                }"
              >
                <q-icon v-if="exec.status === 'completed'" name="check" size="13px" style="color: white;" />
                <span v-else class="lp-timeline__num">{{ i + 1 }}</span>
              </div>
              <div class="lp-timeline__label" :class="{
                'lp-timeline__label--done':    exec.status === 'completed',
                'lp-timeline__label--running': exec.status === 'running',
              }">{{ stepLabel(exec.type) }}</div>
              <div v-if="exec.elapsed > 0" class="lp-timeline__elapsed lp-mono">{{ formatElapsed(exec.elapsed) }}</div>
            </div>
            <!-- Connector -->
            <div v-if="i < currentRun.steps.length - 1" class="lp-timeline__connector"
              :class="{ 'lp-timeline__connector--done': i < currentRun.steps.findIndex(s => s.status !== 'completed') }"
            />
          </template>
        </div>
      </div>

      <!-- Main area -->
      <div class="lp-exp-main">
        <!-- Step list panel -->
        <div class="lp-card lp-step-list">
          <div class="lp-step-list__header lp-mono">전체 스텝</div>
          <div
            v-for="(exec, i) in currentRun.steps"
            :key="exec.uid"
            class="lp-step-item"
            :class="{ 'lp-step-item--active': activeStepUid === exec.uid }"
            @click="activeStepUid = exec.uid"
          >
            <div
              class="lp-step-item__circle"
              :class="{
                'lp-step-item__circle--done':    exec.status === 'completed',
                'lp-step-item__circle--running': exec.status === 'running',
              }"
            >
              <q-icon v-if="exec.status === 'completed'" name="check" size="10px" style="color: white;" />
              <span v-else class="lp-mono" style="font-size: 9px; font-weight: 700;">{{ i + 1 }}</span>
            </div>
            <div class="lp-step-item__label" :class="{ 'lp-step-item__label--active': activeStepUid === exec.uid }">
              {{ stepLabel(exec.type) }}
            </div>
            <span v-if="exec.status === 'running'" class="lp-pulse-dot" style="background: var(--blue);" />
          </div>
        </div>

        <!-- Step detail -->
        <div class="lp-card lp-step-detail">
          <div v-if="!activeExec" class="lp-empty" style="padding: 40px 0;">
            <div style="color: var(--t3); font-size: 13px;">스텝을 선택하세요</div>
          </div>

          <template v-else>
            <!-- Step header -->
            <div class="lp-step-detail__head">
              <div class="lp-step-detail__icon"
                :class="{
                  'lp-step-detail__icon--done':    activeExec.status === 'completed',
                  'lp-step-detail__icon--running': activeExec.status === 'running',
                }"
              >
                <q-icon
                  :name="stepDefs[activeExec.type].icon"
                  size="18px"
                  :style="{ color: activeExec.status === 'completed' ? 'var(--green)' : activeExec.status === 'running' ? 'var(--blue)' : 'var(--t3)' }"
                />
              </div>
              <div class="lp-step-detail__meta">
                <div class="lp-step-detail__title">Step {{ (currentRun?.steps.findIndex(s => activeExec && s.uid === activeExec.uid) ?? 0) + 1 }}. {{ stepLabel(activeExec.type) }}</div>
                <div v-if="deviceName" class="lp-step-detail__device lp-mono">장비: {{ deviceName }}</div>
              </div>
              <span class="lp-status-chip" :class="stepStatusChipClass(activeExec.status)">
                <span v-if="activeExec.status === 'running'" class="lp-pulse-dot" />
                {{ statusLabel(activeExec.status) }}
              </span>
            </div>

            <!-- Sub-components (unchanged) -->
            <div class="lp-step-detail__content">
              <template v-if="activeExec.type === 'weighing' && activeWorkflowStep">
                <div class="lp-step-detail__subhead">
                  <q-icon name="scale" size="16px" style="color: var(--blue);" />
                  <span>원료 칭량</span>
                </div>
                <WeighingRunner
                  :execution="activeExec"
                  :step-data="asWeighing(activeWorkflowStep.data)"
                  :compositions="selectedWorkflow!.compositions"
                  :can-start="canStartActiveStep"
                  @start="onStartStep(activeExec.uid)"
                  @stop="onStopStep(activeExec.uid)"
                />
              </template>

              <template v-else-if="activeExec.type === 'analysis' && activeWorkflowStep">
                <div class="lp-step-detail__subhead">
                  <q-icon name="science" size="16px" style="color: var(--green);" />
                  <span>측정/분석</span>
                </div>
                <AnalysisSummary
                  :execution="activeExec"
                  :step-data="asAnalysis(activeWorkflowStep.data)"
                  :compositions="selectedWorkflow!.compositions"
                  @start="onStartStep(activeExec.uid)"
                  @stop="onStopStep(activeExec.uid)"
                />
              </template>

              <template v-else-if="activeWorkflowStep">
                <div class="lp-step-detail__subhead">
                  <q-icon :name="stepDefs[activeExec.type].icon" size="16px" :style="{ color: `var(--${stepDefs[activeExec.type].color})` }" />
                  <span>{{ stepDefs[activeExec.type].label }}</span>
                  <span v-if="deviceName" style="font-size: 11px; color: var(--t3); margin-left: 8px;">장비: {{ deviceName }}</span>
                </div>
                <div style="margin-bottom: 12px;">
                  <StepConfigSummary :step="activeWorkflowStep" />
                </div>
                <StepRunner
                  :execution="activeExec"
                  :can-start="canStartActiveStep"
                  @start="onStartStep(activeExec.uid)"
                  @stop="onStopStep(activeExec.uid)"
                />
              </template>
            </div>
          </template>
        </div>
      </div>
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useWorkflows } from 'src/composables/useWorkflows'
import { useExperimentRunner } from 'src/composables/useExperimentRunner'
import { useSilaDevices } from 'src/composables/useSilaDevices'
import { stepDefs } from 'src/components/workflow/types'
import type { AnalysisData, StepData, StepExecStatus, StepType, Workflow, WeighingData } from 'src/components/workflow/types'

const asWeighing = (d: StepData) => d as WeighingData
const asAnalysis = (d: StepData) => d as AnalysisData

import WeighingRunner from 'src/components/experiment/WeighingRunner.vue'
import AnalysisSummary from 'src/components/experiment/AnalysisSummary.vue'
import StepRunner from 'src/components/experiment/StepRunner.vue'
import StepConfigSummary from 'src/components/experiment/StepConfigSummary.vue'
import { API_BASE } from 'src/config'

const $q = useQuasar()
const router = useRouter()
const authStore = useAuthStore()
const { workflows, fetchAll } = useWorkflows()
const { currentRun, activeStepUid, createRun, startStep, stopStep, cleanup } = useExperimentRunner()
const { allDevices } = useSilaDevices()

const selectedWorkflowId = ref<number | null>(currentRun.value?.workflowId ?? null)

const allStepsCompleted = computed(() =>
  !!currentRun.value && currentRun.value.steps.length > 0 &&
  currentRun.value.steps.every((s) => s.status === 'completed')
)

onMounted(() => {
  void fetchAll()
  if (!currentRun.value || !selectedWorkflow.value) return
  const runUids = currentRun.value.steps.map(s => s.uid).sort().join(',')
  const wfUids  = selectedWorkflow.value.steps.map(s => s.uid).sort().join(',')
  if (runUids === wfUids) return
  $q.dialog({
    title: '워크플로우 변경 감지',
    message: '워크플로우의 스텝이 변경되었습니다. 실험을 초기화하고 새 스텝을 반영하시겠습니까?',
    cancel: { flat: true, label: '기존 유지' },
    ok: { color: 'primary', label: '초기화 및 반영' },
  }).onOk(() => {
    cleanup()
    currentRun.value = null
    activeStepUid.value = null
  })
})

const workflowOptions = computed(() =>
  workflows.value.map(w => ({ label: w.name || `워크플로우 #${w.id}`, value: w.id }))
)

const selectedWorkflow = computed(() =>
  workflows.value.find(w => w.id === selectedWorkflowId.value) ?? null
)

const activeExec = computed(() =>
  currentRun.value?.steps.find(s => s.uid === activeStepUid.value) ?? null
)

const activeWorkflowStep = computed(() =>
  selectedWorkflow.value?.steps.find(s => s.uid === activeStepUid.value) ?? null
)

const deviceName = computed(() => {
  const did = activeWorkflowStep.value?.data?.deviceId
  if (!did) return null
  return allDevices.value.find(d => d.serverId === did)?.device ?? null
})

const canStartActiveStep = computed(() => {
  if (!currentRun.value || !activeExec.value) return false
  const idx = currentRun.value.steps.findIndex(s => s.uid === activeExec.value!.uid)
  if (idx <= 0) return true
  return currentRun.value.steps[idx - 1]!.status === 'completed'
})

const runStatusChipClass = computed(() => {
  if (!currentRun.value) return 'lp-status-chip--grey'
  switch (currentRun.value.status) {
    case 'running':   return 'lp-status-chip--blue'
    case 'completed': return 'lp-status-chip--green'
    default:          return 'lp-status-chip--orange'
  }
})

const runStatusLabel = computed(() => {
  if (!currentRun.value) return ''
  switch (currentRun.value.status) {
    case 'running':   return '실험 진행 중'
    case 'completed': return '실험 완료'
    case 'idle':      return '실험 준비됨'
    default:          return '대기 중'
  }
})

function stepStatusChipClass(status: StepExecStatus) {
  switch (status) {
    case 'completed': return 'lp-status-chip--green'
    case 'running':   return 'lp-status-chip--blue'
    case 'failed':    return 'lp-status-chip--red'
    default:          return 'lp-status-chip--grey'
  }
}

function onCreateRun() {
  if (!selectedWorkflow.value) return
  createRun(selectedWorkflow.value)
  $q.notify({ type: 'positive', message: '실험이 생성되었습니다. 각 스텝을 순서대로 실행하세요.' })
}

function onStartStep(uid: number) {
  const ws = selectedWorkflow.value?.steps.find(s => s.uid === uid)
  if (ws) startStep(uid, ws)
}

function onCompleteExperiment() {
  const wf = selectedWorkflow.value
  if (!wf) return
  $q.dialog({
    title: '실험 완료',
    message: '실험을 완료 처리하시겠습니까? 완료 후에는 수정할 수 없습니다.',
    cancel: { flat: true, label: '취소' },
    ok: { color: 'positive', label: '완료' },
  }).onOk(() => { void _execComplete(wf) })
}

async function _execComplete(wf: Workflow) {
  try {
    const res = await fetch(`${API_BASE}/workflows/${wf.id}/complete`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${authStore.token ?? ''}` },
    })
    if (!res.ok) throw new Error()
    void fetchAll()
    $q.notify({ type: 'positive', icon: 'celebration', message: '실험이 완료되었습니다!' })
  } catch {
    $q.notify({ type: 'negative', message: '실험 완료 처리 실패' })
  }
}

function onStopStep(uid: number) {
  $q.dialog({
    title: '스텝 완료',
    message: '이 스텝을 완료 처리하시겠습니까?',
    cancel: { flat: true, label: '취소' },
    ok: { color: 'primary', label: '완료' },
  }).onOk(() => {
    stopStep(uid)
    $q.notify({ type: 'positive', message: '스텝이 완료되었습니다.' })
    if (currentRun.value?.status === 'completed') {
      $q.notify({ type: 'positive', icon: 'celebration', message: '모든 스텝이 완료되었습니다!' })
    }
  })
}

function stepLabel(type: StepType) {
  return stepDefs[type]?.label ?? type
}

function statusLabel(status: StepExecStatus) {
  switch (status) {
    case 'pending':   return '대기'
    case 'running':   return '실행 중'
    case 'completed': return '완료'
    case 'failed':    return '실패'
  }
}

function formatElapsed(s: number) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${String(sec).padStart(2, '0')}`
}

let suppressWatch = false
watch(selectedWorkflowId, (newId, oldId) => {
  if (suppressWatch) { suppressWatch = false; return }
  if (currentRun.value && oldId != null) {
    $q.dialog({
      title: '실험 초기화',
      message: '워크플로우를 변경하면 현재 실험 데이터가 초기화됩니다. 계속하시겠습니까?',
      cancel: { flat: true, label: '취소' },
      ok: { color: 'negative', label: '초기화' },
    }).onOk(() => {
      cleanup()
      currentRun.value = null
      activeStepUid.value = null
    }).onCancel(() => {
      suppressWatch = true
      selectedWorkflowId.value = oldId
    })
  } else {
    cleanup()
    currentRun.value = null
    activeStepUid.value = null
  }
})

onUnmounted(() => cleanup())
</script>

<style scoped>
.lp-page { padding: 24px; }

/* ── Top bar ── */
.lp-exp-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
}

.lp-exp-topbar__left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.lp-exp-topbar__hint {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--orange);
}

.lp-select :deep(.q-field__control) {
  background: var(--s2) !important;
}

/* ── Buttons ── */
.lp-btn-primary {
  background: var(--accent) !important;
  color: white !important;
  font-size: 12px;
  border-radius: var(--r1) !important;
}

.lp-btn-success {
  background: var(--green) !important;
  color: white !important;
  font-size: 12px;
  border-radius: var(--r1) !important;
}

/* ── Empty ── */
.lp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 10px;
}

.lp-empty__title {
  font-size: 15px;
  color: var(--t2);
  font-weight: 500;
}

/* ── Timeline ── */
.lp-card {
  background: var(--s1);
  border: 1px solid var(--bd);
  border-radius: var(--r2);
  box-shadow: var(--shadow);
}

.lp-timeline-card {
  padding: 16px 20px;
  margin-bottom: 14px;
}

.lp-timeline {
  display: flex;
  align-items: flex-start;
  gap: 0;
}

.lp-timeline__step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  flex: 1;
  min-width: 0;
}

.lp-timeline__circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--s3);
  border: 2px solid var(--bd);
  transition: all 0.2s;
  flex-shrink: 0;
}

.lp-timeline__circle--done {
  background: var(--green);
  border-color: var(--green);
}

.lp-timeline__circle--running {
  background: var(--blue-bg);
  border-color: var(--blue);
  box-shadow: 0 0 12px var(--blue-bd);
  animation: lp-pulse 1.4s ease infinite;
}

.lp-timeline__circle--active {
  border-color: var(--accent);
}

.lp-timeline__num {
  font-size: 10px;
  font-weight: 700;
  font-family: var(--mono);
  color: var(--t3);
}

.lp-timeline__label {
  font-size: 10px;
  color: var(--t3);
  white-space: nowrap;
  font-family: var(--sans);
}

.lp-timeline__label--done    { color: var(--green); }
.lp-timeline__label--running { color: var(--blue); font-weight: 600; }

.lp-timeline__elapsed {
  font-size: 9px;
  color: var(--t3);
}

.lp-timeline__connector {
  flex: 0 0 40px;
  height: 2px;
  background: var(--bd);
  border-radius: 1px;
  margin-bottom: 24px;
  flex-shrink: 0;
  align-self: center;
  margin-top: -18px;
}

.lp-timeline__connector--done {
  background: var(--green);
}

/* ── Main area ── */
.lp-exp-main {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

/* ── Step list ── */
.lp-step-list {
  width: 220px;
  flex-shrink: 0;
  overflow: hidden;
}

.lp-step-list__header {
  font-size: 10px;
  color: var(--t3);
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 12px 14px 8px;
  border-bottom: 1px solid var(--bd);
}

.lp-step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  cursor: pointer;
  border-left: 2px solid transparent;
  transition: background 0.12s;
}

.lp-step-item:hover {
  background: var(--s2);
}

.lp-step-item--active {
  background: var(--accent-bg);
  border-left-color: var(--accent);
}

.lp-step-item__circle {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--s3);
  border: 1.5px solid var(--bd);
  font-size: 9px;
  color: var(--t3);
}

.lp-step-item__circle--done {
  background: var(--green);
  border-color: var(--green);
}

.lp-step-item__circle--running {
  background: var(--blue-bg);
  border-color: var(--blue);
  color: var(--blue);
}

.lp-step-item__label {
  flex: 1;
  font-size: 12px;
  color: var(--t1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lp-step-item__label--active {
  color: var(--accent);
  font-weight: 600;
}

/* ── Step detail ── */
.lp-step-detail {
  flex: 1;
  padding: 18px;
}

.lp-step-detail__head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.lp-step-detail__icon {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: var(--s3);
  border: 1px solid var(--bd);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.lp-step-detail__icon--done {
  background: var(--green-bg);
  border-color: var(--green-bd);
}

.lp-step-detail__icon--running {
  background: var(--blue-bg);
  border-color: var(--blue-bd);
}

.lp-step-detail__meta {
  flex: 1;
}

.lp-step-detail__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--t1);
  margin-bottom: 2px;
}

.lp-step-detail__device {
  font-size: 11px;
  color: var(--t3);
}

.lp-step-detail__subhead {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--t1);
  margin-bottom: 12px;
}

.lp-step-detail__content {
  padding-top: 4px;
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
