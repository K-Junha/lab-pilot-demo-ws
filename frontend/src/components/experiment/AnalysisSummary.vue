<template>
  <div>
    <div v-if="!selectedComp" class="text-grey">조성이 선택되지 않았습니다</div>
    <div v-else>
      <div class="text-subtitle1 text-weight-bold q-mb-sm">
        {{ selectedComp.name || `조성 #${selectedComp.id}` }} — 측정/분석 결과
      </div>

      <!-- Controls -->
      <div class="row items-center q-gutter-md q-mb-md">
        <q-btn
          v-if="execution.status === 'pending'"
          color="primary"
          icon="play_arrow"
          label="분석 시작"
          @click="$emit('start')"
        />
        <q-btn
          v-if="execution.status === 'running'"
          color="negative"
          icon="stop"
          label="분석 중지"
          @click="$emit('stop')"
        />
        <q-badge v-if="execution.status === 'completed'" color="green" class="text-body2 q-pa-sm">
          <q-icon name="check_circle" class="q-mr-xs" /> 완료
        </q-badge>
        <span v-if="execution.elapsed > 0" class="text-caption text-grey">
          경과: {{ Math.floor(execution.elapsed / 60) }}분 {{ execution.elapsed % 60 }}초
        </span>
      </div>

      <!-- Property targets with PASS/FAIL -->
      <q-markup-table flat bordered dense>
        <thead>
          <tr>
            <th class="text-left">물성</th>
            <th>단위</th>
            <th>모드</th>
            <th>목표</th>
            <th>측정값</th>
            <th>판정</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pt in selectedComp.propertyTargets" :key="pt.property">
            <td class="text-left">{{ pt.property }}</td>
            <td class="text-center">{{ pt.unit }}</td>
            <td class="text-center">{{ pt.mode }}</td>
            <td class="text-center">
              <template v-if="pt.mode === '단일값'">{{ pt.target }}</template>
              <template v-else-if="pt.mode === '범위'">{{ pt.min }} ~ {{ pt.max }}</template>
              <template v-else-if="pt.mode === '최솟값'">클수록 좋음</template>
              <template v-else-if="pt.mode === '최댓값'">작을수록 좋음</template>
            </td>
            <td class="text-center">
              {{ getMeasured(pt.property) ?? '-' }}
            </td>
            <td class="text-center">
              <q-badge :color="judgeColor(pt)">{{ judgeLabel(pt) }}</q-badge>
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CompositionData, PropertyTarget, StepExecution } from 'src/components/workflow/types'

const props = defineProps<{
  execution: StepExecution
  stepData: any
  compositions: CompositionData[]
}>()

defineEmits<{ start: []; stop: [] }>()

const selectedComp = computed(() =>
  props.compositions.find(c => c.id === props.stepData?.compositionId) ?? null
)

function getMeasured(property: string) {
  return props.stepData?.measurements?.[property]?.measured ?? null
}

function judgePass(pt: PropertyTarget): boolean | null {
  const m = getMeasured(pt.property)
  if (m == null) return null
  if (pt.mode === '단일값' && pt.target != null) return m === pt.target
  if (pt.mode === '범위' && pt.min != null && pt.max != null) return m >= pt.min && m <= pt.max
  if (pt.mode === '최솟값' || pt.mode === '최댓값') return true // 방향성만 — 항상 기록
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
