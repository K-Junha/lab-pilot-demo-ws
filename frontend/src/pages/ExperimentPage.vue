<template>
  <q-page padding>
    <!-- Header: workflow selector -->
    <div class="row items-center q-gutter-md q-mb-md">
      <div class="text-h5">실험 실행</div>
      <q-select
        outlined
        dense
        v-model="selectedWorkflowId"
        :options="workflowOptions"
        option-value="value"
        option-label="label"
        emit-value
        map-options
        label="워크플로우 선택"
        style="min-width: 280px;"
        :disable="!!currentRun && currentRun.status === 'running'"
      />
      <q-btn
        v-if="selectedWorkflow && selectedWorkflow.status === '진행중' && !currentRun"
        color="primary"
        icon="science"
        label="실험 생성"
        @click="onCreateRun"
      />
      <q-chip
        v-if="selectedWorkflow && selectedWorkflow.status === '계획중'"
        color="orange"
        text-color="white"
        icon="lock"
        label="계획중 — 워크플로우 페이지에서 실험을 시작하세요"
      />
      <q-space />
      <template v-if="currentRun">
        <q-badge :color="runStatusColor" class="text-body2 q-pa-sm q-mr-sm">
          {{ runStatusLabel }}
        </q-badge>
        <q-btn
          v-if="allStepsCompleted && selectedWorkflow?.status === '진행중'"
          color="positive"
          icon="check_circle"
          label="실험 완료"
          @click="onCompleteExperiment"
        />
      </template>
    </div>

    <!-- No workflow selected -->
    <div v-if="!currentRun && workflows.length === 0" class="text-center text-grey q-mt-xl">
      <q-icon name="account_tree" size="64px" class="q-mb-md" color="grey-5" />
      <div class="text-h6">먼저 워크플로우를 생성하세요</div>
      <q-btn flat color="primary" label="워크플로우 페이지로 이동" icon="arrow_forward" class="q-mt-md" @click="router.push('/workflow')" />
    </div>
    <div v-else-if="!currentRun" class="text-center text-grey q-mt-xl">
      <q-icon name="science" size="64px" class="q-mb-md" color="grey-5" />
      <div class="text-h6">워크플로우를 선택하고 실험을 생성하세요</div>
    </div>

    <!-- Experiment runner layout -->
    <div v-else class="row q-gutter-md" style="min-height: 500px;">
      <!-- Left: Step timeline -->
      <div class="col-3">
        <q-list bordered separator class="rounded-borders">
          <q-item
            v-for="(exec, i) in currentRun.steps"
            :key="exec.uid"
            clickable
            :active="activeStepUid === exec.uid"
            :active-class="$q.dark.isActive ? 'bg-blue-10' : 'bg-blue-1'"
            @click="activeStepUid = exec.uid"
          >
            <q-item-section avatar>
              <q-icon
                :name="statusIcon(exec.status)"
                :color="statusIconColor(exec.status)"
              />
            </q-item-section>
            <q-item-section>
              <q-item-label>
                {{ i + 1 }}. {{ stepLabel(exec.type) }}
              </q-item-label>
              <q-item-label caption>
                <q-badge
                  :color="statusBadgeColor(exec.status)"
                  :label="statusLabel(exec.status)"
                  dense
                />
                <span v-if="exec.elapsed > 0" class="q-ml-sm text-grey">
                  {{ formatElapsed(exec.elapsed) }}
                </span>
              </q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </div>

      <!-- Right: Step detail -->
      <div class="col">
        <q-card flat bordered class="q-pa-md">
          <div v-if="!activeExec" class="text-grey text-center q-pa-lg">
            스텝을 선택하세요
          </div>

          <!-- 칭량 스텝 — 실시간 저울 연동 칭량 실행 -->
          <template v-else-if="activeExec.type === 'weighing' && activeWorkflowStep">
            <div class="text-h6 q-mb-md">
              <q-icon name="scale" color="blue" class="q-mr-sm" />
              원료 칭량
            </div>
            <WeighingRunner
              :execution="activeExec"
              :step-data="activeWorkflowStep.data"
              :compositions="selectedWorkflow!.compositions"
              :can-start="canStartActiveStep"
              @start="onStartStep(activeExec.uid)"
              @stop="onStopStep(activeExec.uid)"
            />
          </template>

          <!-- Analysis step — special handling with PASS/FAIL -->
          <template v-else-if="activeExec.type === 'analysis' && activeWorkflowStep">
            <div class="text-h6 q-mb-md">
              <q-icon name="science" color="green" class="q-mr-sm" />
              측정/분석
            </div>
            <AnalysisSummary
              :execution="activeExec"
              :step-data="activeWorkflowStep.data"
              :compositions="selectedWorkflow!.compositions"
              @start="onStartStep(activeExec.uid)"
              @stop="onStopStep(activeExec.uid)"
            />
          </template>

          <!-- All other runnable steps -->
          <template v-else-if="activeWorkflowStep">
            <div class="text-h6 q-mb-md">
              <q-icon
                :name="stepDefs[activeExec.type].icon"
                :color="stepDefs[activeExec.type].color"
                class="q-mr-sm"
              />
              {{ stepDefs[activeExec.type].label }}
              <span v-if="deviceName" class="text-body2 text-grey q-ml-sm">
                장비: {{ deviceName }}
              </span>
            </div>

            <!-- Step config summary (read-only) -->
            <div class="q-mb-md">
              <StepConfigSummary :step="activeWorkflowStep" />
            </div>

            <StepRunner
              :execution="activeExec"
              :can-start="canStartActiveStep"
              @start="onStartStep(activeExec.uid)"
              @stop="onStopStep(activeExec.uid)"
            />
          </template>
        </q-card>
      </div>
    </div>
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
import type { StepExecStatus, StepType } from 'src/components/workflow/types'

import WeighingRunner from 'src/components/experiment/WeighingRunner.vue'
import AnalysisSummary from 'src/components/experiment/AnalysisSummary.vue'
import StepRunner from 'src/components/experiment/StepRunner.vue'
import StepConfigSummary from 'src/components/experiment/StepConfigSummary.vue'

const API_BASE = 'http://localhost:8000/api'

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

// 페이지 진입 시 워크플로우 변경 감지
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

// Active execution step
const activeExec = computed(() =>
  currentRun.value?.steps.find(s => s.uid === activeStepUid.value) ?? null
)

// Matching workflow step for data access
const activeWorkflowStep = computed(() =>
  selectedWorkflow.value?.steps.find(s => s.uid === activeStepUid.value) ?? null
)

// Device name for active step
const deviceName = computed(() => {
  const did = activeWorkflowStep.value?.data?.deviceId
  if (!did) return null
  return allDevices.value.find(d => d.serverId === did)?.device ?? null
})

// 이전 스텝 완료 여부 (순서 강제)
const canStartActiveStep = computed(() => {
  if (!currentRun.value || !activeExec.value) return false
  const idx = currentRun.value.steps.findIndex(s => s.uid === activeExec.value!.uid)
  if (idx <= 0) return true // 첫 번째 스텝은 항상 시작 가능
  return currentRun.value.steps[idx - 1]!.status === 'completed'
})

// Run status
const runStatusColor = computed(() => {
  if (!currentRun.value) return 'grey'
  switch (currentRun.value.status) {
    case 'running': return 'blue'
    case 'completed': return 'green'
    case 'idle': return 'orange'
    default: return 'grey'
  }
})
const runStatusLabel = computed(() => {
  if (!currentRun.value) return ''
  switch (currentRun.value.status) {
    case 'running': return '실험 진행 중'
    case 'completed': return '실험 완료'
    case 'idle': return '실험 준비됨'
    default: return '대기 중'
  }
})

function onCreateRun() {
  if (!selectedWorkflow.value) return
  createRun(selectedWorkflow.value)
  $q.notify({ type: 'positive', message: '실험이 생성되었습니다. 각 스텝을 순서대로 실행하세요.' })
}

function onStartStep(uid: number) {
  const ws = selectedWorkflow.value?.steps.find(s => s.uid === uid)
  if (ws) startStep(uid, ws)
}

async function onCompleteExperiment() {
  const wf = selectedWorkflow.value
  if (!wf) return
  $q.dialog({
    title: '실험 완료',
    message: '실험을 완료 처리하시겠습니까? 완료 후에는 수정할 수 없습니다.',
    cancel: { flat: true, label: '취소' },
    ok: { color: 'positive', label: '완료' },
  }).onOk(async () => {
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
  })
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
    // 전체 실험 완료 확인
    if (currentRun.value?.status === 'completed') {
      $q.notify({ type: 'positive', icon: 'celebration', message: '모든 스텝이 완료되었습니다!' })
    }
  })
}

function stepLabel(type: StepType) {
  return stepDefs[type]?.label ?? type
}

function statusIcon(status: StepExecStatus) {
  switch (status) {
    case 'pending': return 'radio_button_unchecked'
    case 'running': return 'sensors'
    case 'completed': return 'check_circle'
    case 'failed': return 'error'
  }
}

function statusIconColor(status: StepExecStatus) {
  switch (status) {
    case 'pending': return 'grey'
    case 'running': return 'blue'
    case 'completed': return 'green'
    case 'failed': return 'red'
  }
}

function statusBadgeColor(status: StepExecStatus) {
  switch (status) {
    case 'pending': return 'grey'
    case 'running': return 'blue'
    case 'completed': return 'green'
    case 'failed': return 'red'
  }
}

function statusLabel(status: StepExecStatus) {
  switch (status) {
    case 'pending': return '대기'
    case 'running': return '실행 중'
    case 'completed': return '완료'
    case 'failed': return '실패'
  }
}

function formatElapsed(s: number) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${String(sec).padStart(2, '0')}`
}

// Reset run when workflow changes
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
