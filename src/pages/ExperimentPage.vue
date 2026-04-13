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
        v-if="selectedWorkflow && !currentRun"
        color="primary"
        icon="science"
        label="실험 생성"
        @click="onCreateRun"
      />
      <q-space />
      <q-badge v-if="currentRun" :color="runStatusColor" class="text-body2 q-pa-sm">
        {{ runStatusLabel }}
      </q-badge>
    </div>

    <!-- No workflow selected -->
    <div v-if="!currentRun" class="text-center text-grey q-mt-xl">
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
            active-class="bg-blue-1"
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

          <!-- Composition summary (virtual first view) -->
          <template v-else-if="activeExec.type === 'weighing' && activeWorkflowStep">
            <div class="text-h6 q-mb-md">
              <q-icon name="scale" color="blue" class="q-mr-sm" />
              원료 칭량 — 설계 결과
            </div>
            <WeighingSummary
              :step-data="activeWorkflowStep.data"
              :compositions="selectedWorkflow!.compositions"
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
import { ref, computed, onUnmounted, watch } from 'vue'
import { useWorkflows } from 'src/composables/useWorkflows'
import { useExperimentRunner } from 'src/composables/useExperimentRunner'
import { useSilaDevices } from 'src/composables/useSilaDevices'
import { stepDefs } from 'src/components/workflow/types'
import type { StepExecStatus, StepType } from 'src/components/workflow/types'

import WeighingSummary from 'src/components/experiment/WeighingSummary.vue'
import AnalysisSummary from 'src/components/experiment/AnalysisSummary.vue'
import StepRunner from 'src/components/experiment/StepRunner.vue'
import StepConfigSummary from 'src/components/experiment/StepConfigSummary.vue'

const { workflows } = useWorkflows()
const { currentRun, activeStepUid, createRun, startStep, stopStep, cleanup } = useExperimentRunner()
const { allDevices } = useSilaDevices()

const selectedWorkflowId = ref<number | null>(null)

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

// Run status
const runStatusColor = computed(() => {
  if (!currentRun.value) return 'grey'
  switch (currentRun.value.status) {
    case 'running': return 'blue'
    case 'completed': return 'green'
    default: return 'grey'
  }
})
const runStatusLabel = computed(() => {
  if (!currentRun.value) return ''
  switch (currentRun.value.status) {
    case 'running': return '실험 진행 중'
    case 'completed': return '실험 완료'
    default: return '대기 중'
  }
})

function onCreateRun() {
  if (!selectedWorkflow.value) return
  createRun(selectedWorkflow.value)
}

function onStartStep(uid: number) {
  const ws = selectedWorkflow.value?.steps.find(s => s.uid === uid)
  if (ws) startStep(uid, ws)
}

function onStopStep(uid: number) {
  stopStep(uid)
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
watch(selectedWorkflowId, () => {
  cleanup()
  currentRun.value = null
  activeStepUid.value = null
})

onUnmounted(() => cleanup())
</script>
