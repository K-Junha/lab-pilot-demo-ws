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

    <div class="text-subtitle2 q-mb-sm">원료별 칭량</div>
    <div v-if="selectedComp && selectedComp.oxides.length > 0">
      <div v-for="(oxide, ri) in selectedComp.oxides" :key="ri" class="row q-col-gutter-sm q-mb-xs items-center">
        <div class="col-3">
          <q-input dense outlined readonly :model-value="oxide.oxide" label="원료" />
        </div>
        <div class="col-2">
          <q-input dense outlined readonly :model-value="calcTargetG(oxide)" label="목표량 (g)" />
        </div>
        <div class="col-2">
          <q-input dense outlined v-model.number="getRow(oxide.oxide).actualG" type="number" label="실칭량 (g)" />
        </div>
        <div class="col-2">
          <q-input dense outlined readonly :model-value="calcError(oxide)" label="오차 (g)" />
        </div>
        <div class="col-2">
          <q-input dense outlined readonly :model-value="calcErrorPct(oxide)" label="오차율" />
        </div>
      </div>
    </div>
    <div v-else class="text-grey text-caption">조성을 선택하면 원료 목록이 표시됩니다</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CompositionData } from '../types'
import DeviceSelector from '../DeviceSelector.vue'

const props = defineProps<{
  data: any
  compositions: CompositionData[]
}>()

const compositionOptions = computed(() =>
  props.compositions.map(c => ({ label: c.name || `조성 #${c.id}`, value: c.id }))
)

const selectedComp = computed(() =>
  props.compositions.find(c => c.id === props.data.compositionId) ?? null
)

// Ensure rows map exists for actual weights
if (!props.data.rows) props.data.rows = {}

function getRow(oxide: string) {
  if (!props.data.rows[oxide]) {
    props.data.rows[oxide] = { actualG: null }
  }
  return props.data.rows[oxide]
}

function calcTargetG(oxide: { oxide: string; wt: number }) {
  const comp = selectedComp.value
  if (!comp?.batchWeight) return ''
  return ((oxide.wt / 100) * comp.batchWeight).toFixed(3)
}

function calcError(oxide: { oxide: string; wt: number }) {
  const targetG = Number(calcTargetG(oxide))
  const actual = getRow(oxide.oxide).actualG
  if (actual == null || !targetG) return ''
  return (actual - targetG).toFixed(3)
}

function calcErrorPct(oxide: { oxide: string; wt: number }) {
  const targetG = Number(calcTargetG(oxide))
  const actual = getRow(oxide.oxide).actualG
  if (actual == null || !targetG) return ''
  return ((actual - targetG) / targetG * 100).toFixed(2) + '%'
}
</script>
