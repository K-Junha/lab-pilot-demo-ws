<template>
  <div>
    <!-- Header -->
    <div class="row items-center q-mb-md">
      <q-btn flat icon="arrow_back" @click="emit('back')" />
      <div class="text-h5 col q-ml-sm">{{ workflow.name || '새 워크플로우' }}</div>
      <q-input
        v-model="workflow.name"
        label="워크플로우 이름"
        outlined
        dense
        style="min-width: 220px;"
        class="q-mr-md"
      />
      <q-btn flat label="취소" color="grey" class="q-mr-sm" @click="emit('back')" />
      <q-btn label="저장" color="primary" icon="save" @click="emit('save')" />
    </div>

    <!-- Tabs: 고정 조성 목록 탭 + 동적 공정 스텝 탭 -->
    <div class="row items-center q-mb-sm">
      <q-tabs v-model="activeTab" dense align="left" class="col" active-color="primary" indicator-color="primary" narrow-indicator>
        <!-- 고정: 조성 목록 -->
        <q-tab name="compositions" class="q-px-md">
          <div class="row items-center no-wrap q-gutter-xs">
            <q-icon name="science" color="purple" size="xs" />
            <span>조성 목록 ({{ workflow.compositions.length }})</span>
          </div>
        </q-tab>

        <!-- 동적: 공정 스텝 -->
        <q-tab
          v-for="(step, idx) in workflow.steps"
          :key="step.uid"
          :name="step.uid"
          class="q-px-md"
        >
          <div class="row items-center no-wrap q-gutter-xs">
            <q-icon :name="allStepDefs[step.type].icon" :color="allStepDefs[step.type].color" size="xs" />
            <span>{{ idx + 1 }}. {{ allStepDefs[step.type].label }}</span>
            <span class="step-close-btn" @pointerdown.stop.prevent @click.stop.prevent="removeStep(idx)">
              <q-icon name="close" size="14px" />
            </span>
          </div>
        </q-tab>
      </q-tabs>
      <q-btn flat dense icon="add" color="primary" data-testid="add-step-btn" @click="addStepDialog = true">
        <q-tooltip>공정 Step 추가</q-tooltip>
      </q-btn>
    </div>

    <q-separator class="q-mb-md" />

    <!-- Tab panels -->
    <q-tab-panels v-model="activeTab" animated keep-alive>
      <!-- 고정: 조성 목록 패널 -->
      <q-tab-panel name="compositions">
        <CompositionListStep :compositions="workflow.compositions" />
      </q-tab-panel>

      <!-- 동적: 공정 스텝 패널 -->
      <q-tab-panel
        v-for="step in workflow.steps"
        :key="step.uid"
        :name="step.uid"
      >
        <WeighingStep v-if="step.type === 'weighing'" :data="step.data" :compositions="workflow.compositions" />
        <MixingStep v-else-if="step.type === 'mixing'" :data="step.data" />
        <FormingStep v-else-if="step.type === 'forming'" :data="step.data" />
        <FiringStep v-else-if="step.type === 'firing'" :data="step.data" />
        <HeatTreatStep v-else-if="step.type === 'heattreat'" :data="step.data" />
        <MachiningStep v-else-if="step.type === 'machining'" :data="step.data" />
        <AnalysisStep v-else-if="step.type === 'analysis'" :data="step.data" :compositions="workflow.compositions" />
      </q-tab-panel>
    </q-tab-panels>

    <!-- Add Step Dialog -->
    <q-dialog v-model="addStepDialog">
      <q-card style="min-width: 420px">
        <q-card-section>
          <div class="text-h6">공정 Step 추가</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-list bordered separator>
            <q-item
              v-for="def in stepDefList"
              :key="def.key"
              clickable
              v-ripple
              @click="addStep(def.key)"
            >
              <q-item-section avatar>
                <q-icon :name="def.icon" :color="def.color" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ def.label }}</q-item-label>
                <q-item-label caption>{{ def.desc }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import CompositionListStep from './steps/CompositionListStep.vue'
import WeighingStep from './steps/WeighingStep.vue'
import MixingStep from './steps/MixingStep.vue'
import FormingStep from './steps/FormingStep.vue'
import FiringStep from './steps/FiringStep.vue'
import HeatTreatStep from './steps/HeatTreatStep.vue'
import MachiningStep from './steps/MachiningStep.vue'
import AnalysisStep from './steps/AnalysisStep.vue'
import {
  stepDefs as allStepDefs,
  createStepData,
  type Workflow,
  type WorkflowStep,
  type StepType,
} from './types'

const stepDefList = Object.values(allStepDefs)
const $q = useQuasar()

const props = defineProps<{ workflow: Workflow }>()
const emit = defineEmits<{
  back: []
  save: []
}>()

const activeTab = ref<string | number>('compositions')
const addStepDialog = ref(false)

let uidSeq = Math.max(Date.now(), ...props.workflow.steps.map(s => s.uid), 0)

function addStep(type: StepType) {
  const newStep: WorkflowStep = {
    uid: ++uidSeq,
    type,
    data: createStepData(type),
  }
  props.workflow.steps.push(newStep)
  activeTab.value = newStep.uid
  addStepDialog.value = false
}

function removeStep(idx: number) {
  $q.dialog({
    title: '스텝 삭제',
    message: '이 공정 스텝을 삭제하시겠습니까?',
    cancel: { flat: true, label: '취소' },
    ok: { color: 'negative', label: '삭제' },
  }).onOk(() => {
    const removed = props.workflow.steps.splice(idx, 1)[0]
    if (activeTab.value === removed?.uid) {
      activeTab.value = props.workflow.steps.length > 0
        ? props.workflow.steps[Math.min(idx, props.workflow.steps.length - 1)]!.uid
        : 'compositions'
    }
  })
}
</script>

<style scoped>
.step-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  opacity: 0.5;
  transition: opacity 0.2s, background-color 0.2s;
}
.step-close-btn:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.1);
}
</style>
