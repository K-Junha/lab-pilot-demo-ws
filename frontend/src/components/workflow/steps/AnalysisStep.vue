<template>
  <div>
    <!-- 장비 · 조성 선택 -->
    <div class="row items-center q-mb-md q-gutter-md">
      <DeviceSelector v-model="data.deviceId" />
      <q-select
        outlined
        dense
        v-model="data.compositionId"
        :options="compositionOptions"
        option-value="value"
        option-label="label"
        emit-value
        map-options
        label="조성 선택"
        style="min-width: 250px;"
      />
    </div>

    <div class="text-subtitle2 q-mb-sm">측정 항목</div>
    <div v-if="selectedComp && selectedComp.propertyTargets.length > 0">
      <div v-for="(pt, ai) in selectedComp.propertyTargets" :key="ai" class="row q-col-gutter-sm q-mb-xs items-center">
        <div class="col-3">
          <q-input dense outlined readonly :model-value="pt.property" label="물성" />
        </div>
        <div class="col-2">
          <q-input dense outlined readonly :model-value="pt.unit" label="단위" />
        </div>
        <div class="col-2">
          <q-input dense outlined readonly :model-value="pt.mode" label="모드" />
        </div>
        <div class="col-2">
          <q-input dense outlined v-model.number="getMeasurement(pt.property).measured" type="number" label="측정값" />
        </div>
        <div class="col-2">
          <q-badge :color="judgeColor(pt)">
            {{ judgeLabel(pt) }}
          </q-badge>
        </div>
      </div>
    </div>
    <div v-else class="text-grey text-caption">조성을 선택하면 목표 물성 측정 항목이 표시됩니다</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AnalysisData, CompositionData, PropertyTarget } from '../types'
import DeviceSelector from '../DeviceSelector.vue'

const data = defineModel<AnalysisData>('data', { required: true })
const props = defineProps<{ compositions: CompositionData[] }>()

const compositionOptions = computed(() =>
  props.compositions.map(c => ({ label: c.name || `조성 #${c.id}`, value: c.id }))
)

const selectedComp = computed(() =>
  props.compositions.find(c => c.id === data.value.compositionId) ?? null
)

if (!data.value.measurements) data.value.measurements = {}

function getMeasurement(property: string) {
  if (!data.value.measurements[property]) {
    data.value.measurements[property] = { measured: null }
  }
  return data.value.measurements[property]
}

function judgePass(pt: PropertyTarget): boolean | null {
  const m = getMeasurement(pt.property).measured
  if (m == null) return null
  if (pt.mode === '단일값' && pt.target != null) return m === pt.target
  if (pt.mode === '범위' && pt.min != null && pt.max != null) return m >= pt.min && m <= pt.max
  if (pt.mode === '최솟값' && pt.min != null) return m >= pt.min
  if (pt.mode === '최댓값' && pt.max != null) return m <= pt.max
  return null
}

function judgeColor(pt: PropertyTarget) {
  const pass = judgePass(pt)
  return pass === null ? 'grey' : pass ? 'green' : 'red'
}

function judgeLabel(pt: PropertyTarget) {
  const pass = judgePass(pt)
  return pass === null ? '-' : pass ? 'PASS' : 'FAIL'
}
</script>
