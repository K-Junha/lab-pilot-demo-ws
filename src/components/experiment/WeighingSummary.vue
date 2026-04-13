<template>
  <div>
    <div v-if="!selectedComp" class="text-grey">조성이 선택되지 않았습니다</div>
    <div v-else>
      <div class="text-subtitle1 text-weight-bold q-mb-sm">
        {{ selectedComp.name || `조성 #${selectedComp.id}` }} — 칭량 결과
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
          <tr v-for="ox in selectedComp.oxides" :key="ox.oxide">
            <td class="text-left">{{ ox.oxide }}</td>
            <td class="text-center">{{ ox.wt }}</td>
            <td class="text-center">{{ targetG(ox) }}</td>
            <td class="text-center">{{ actualG(ox) ?? '-' }}</td>
            <td class="text-center">{{ errorG(ox) }}</td>
            <td class="text-center">{{ errorPct(ox) }}</td>
            <td class="text-center">
              <q-badge :color="passColor(ox)">{{ passLabel(ox) }}</q-badge>
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CompositionData, CompositionRow } from 'src/components/workflow/types'

const props = defineProps<{
  stepData: any
  compositions: CompositionData[]
}>()

const selectedComp = computed(() =>
  props.compositions.find(c => c.id === props.stepData?.compositionId) ?? null
)

function targetG(ox: CompositionRow) {
  const comp = selectedComp.value
  if (!comp?.batchWeight) return '-'
  return ((ox.wt / 100) * comp.batchWeight).toFixed(3)
}

function actualG(ox: CompositionRow) {
  return props.stepData?.rows?.[ox.oxide]?.actualG ?? null
}

function errorG(ox: CompositionRow) {
  const t = Number(targetG(ox))
  const a = actualG(ox)
  if (a == null || isNaN(t)) return '-'
  return (a - t).toFixed(3)
}

function errorPct(ox: CompositionRow) {
  const t = Number(targetG(ox))
  const a = actualG(ox)
  if (a == null || isNaN(t) || t === 0) return '-'
  return ((a - t) / t * 100).toFixed(2) + '%'
}

function passColor(ox: CompositionRow) {
  const a = actualG(ox)
  if (a == null) return 'grey'
  const t = Number(targetG(ox))
  if (isNaN(t) || t === 0) return 'grey'
  const pct = Math.abs((a - t) / t * 100)
  return pct <= 1 ? 'green' : pct <= 3 ? 'orange' : 'red'
}

function passLabel(ox: CompositionRow) {
  const a = actualG(ox)
  if (a == null) return '미측정'
  const t = Number(targetG(ox))
  if (isNaN(t) || t === 0) return '-'
  const pct = Math.abs((a - t) / t * 100)
  return pct <= 1 ? 'PASS' : pct <= 3 ? 'WARNING' : 'FAIL'
}
</script>
