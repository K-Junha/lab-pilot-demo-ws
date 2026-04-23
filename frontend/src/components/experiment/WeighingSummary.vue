<template>
  <div>
    <div v-if="compositions.length === 0" class="text-grey">조성이 등록되지 않았습니다</div>
    <div v-else>
      <div v-for="comp in compositions" :key="comp.id" class="q-mb-lg">
        <div class="text-subtitle1 text-weight-bold q-mb-sm">
          {{ comp.name || `조성 #${comp.id}` }} — 칭량 결과
          <q-badge v-if="isCompComplete(comp)" color="green" class="q-ml-sm">완료</q-badge>
          <q-badge v-else color="grey" class="q-ml-sm">미완료</q-badge>
        </div>

        <q-markup-table flat bordered dense>
          <thead>
            <tr>
              <th class="text-left">원료</th>
              <th>배합비 (%)</th>
              <th>목표량 (g)</th>
              <th>실칭량 (g)</th>
              <th>오차 (g)</th>
              <th>오차율</th>
              <th>판정</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ox in comp.oxides" :key="ox.oxide">
              <td class="text-left">{{ ox.oxide }}</td>
              <td class="text-center">{{ ox.wt }}</td>
              <td class="text-center">{{ targetG(comp, ox) }}</td>
              <td class="text-center">{{ actualG(comp, ox) ?? '-' }}</td>
              <td class="text-center">{{ errorG(comp, ox) }}</td>
              <td class="text-center">{{ errorPct(comp, ox) }}</td>
              <td class="text-center">
                <q-badge :color="passColor(comp, ox)">{{ passLabel(comp, ox) }}</q-badge>
              </td>
            </tr>
          </tbody>
        </q-markup-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CompositionData, CompositionRow, WeighingData } from 'src/components/workflow/types'

const props = defineProps<{
  stepData: WeighingData
  compositions: CompositionData[]
}>()

function compRows(compId: number) {
  return props.stepData?.rows?.[compId] ?? {}
}

function isCompComplete(comp: CompositionData): boolean {
  const rows = compRows(comp.id)
  return comp.oxides.length > 0 && comp.oxides.every(ox => rows[ox.oxide]?.actualG != null)
}

function targetG(comp: CompositionData, ox: CompositionRow) {
  if (!comp.batchWeight) return '-'
  return ((ox.wt / 100) * comp.batchWeight).toFixed(3)
}

function actualG(comp: CompositionData, ox: CompositionRow) {
  return compRows(comp.id)[ox.oxide]?.actualG ?? null
}

function errorG(comp: CompositionData, ox: CompositionRow) {
  const t = Number(targetG(comp, ox))
  const a = actualG(comp, ox)
  if (a == null || isNaN(t)) return '-'
  return (a - t).toFixed(3)
}

function errorPct(comp: CompositionData, ox: CompositionRow) {
  const t = Number(targetG(comp, ox))
  const a = actualG(comp, ox)
  if (a == null || isNaN(t) || t === 0) return '-'
  return ((a - t) / t * 100).toFixed(2) + '%'
}

function passColor(comp: CompositionData, ox: CompositionRow) {
  const a = actualG(comp, ox)
  if (a == null) return 'grey'
  const t = Number(targetG(comp, ox))
  if (isNaN(t) || t === 0) return 'grey'
  const pct = Math.abs((a - t) / t * 100)
  return pct <= 1 ? 'green' : pct <= 3 ? 'orange' : 'red'
}

function passLabel(comp: CompositionData, ox: CompositionRow) {
  const a = actualG(comp, ox)
  if (a == null) return '미측정'
  const t = Number(targetG(comp, ox))
  if (isNaN(t) || t === 0) return '-'
  const pct = Math.abs((a - t) / t * 100)
  return pct <= 1 ? 'PASS' : pct <= 3 ? 'WARNING' : 'FAIL'
}
</script>
