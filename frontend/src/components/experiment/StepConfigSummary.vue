<template>
  <div class="text-body2">
    <!-- Mixing -->
    <template v-if="step.type === 'mixing'">
      <div class="row q-gutter-md">
        <div><span class="text-grey">믹싱 시간:</span> {{ step.data.duration ?? '-' }} min</div>
        <div v-if="step.data.memo"><span class="text-grey">메모:</span> {{ step.data.memo }}</div>
      </div>
    </template>

    <!-- Forming -->
    <template v-else-if="step.type === 'forming'">
      <div class="row q-gutter-md">
        <div><span class="text-grey">타입:</span> {{ step.data.shape }}</div>
        <template v-if="step.data.shape === '원형'">
          <div><span class="text-grey">R:</span> {{ step.data.R ?? '-' }} mm</div>
          <div><span class="text-grey">T:</span> {{ step.data.T ?? '-' }} mm</div>
        </template>
        <template v-else>
          <div><span class="text-grey">W:</span> {{ step.data.W ?? '-' }} mm</div>
          <div><span class="text-grey">H:</span> {{ step.data.H ?? '-' }} mm</div>
          <div><span class="text-grey">T:</span> {{ step.data.T ?? '-' }} mm</div>
        </template>
      </div>
    </template>

    <!-- Firing -->
    <template v-else-if="step.type === 'firing'">
      <q-markup-table flat bordered dense>
        <thead>
          <tr><th>단계</th><th>승온속도 (°C/min)</th><th>온도 (°C)</th><th>유지시간 (min)</th></tr>
        </thead>
        <tbody>
          <tr v-for="(seg, i) in step.data.segments" :key="i">
            <td class="text-center">{{ Number(i) + 1 }}</td>
            <td class="text-center">{{ seg.rampRate ?? '-' }}</td>
            <td class="text-center">{{ seg.temp ?? '-' }}</td>
            <td class="text-center">{{ seg.holdMin ?? '-' }}</td>
          </tr>
        </tbody>
      </q-markup-table>
    </template>

    <!-- HeatTreat -->
    <template v-else-if="step.type === 'heattreat'">
      <div class="row q-gutter-md">
        <div><span class="text-grey">서냉 온도:</span> {{ step.data.temp ?? '-' }} °C</div>
        <div><span class="text-grey">시간:</span> {{ step.data.duration ?? '-' }} min</div>
        <div><span class="text-grey">방식:</span> {{ step.data.method ?? '-' }}</div>
        <div v-if="step.data.memo"><span class="text-grey">메모:</span> {{ step.data.memo }}</div>
      </div>
    </template>

    <!-- Machining -->
    <template v-else-if="step.type === 'machining'">
      <div class="row q-gutter-md">
        <div><span class="text-grey">타입:</span> {{ step.data.shape }}</div>
        <template v-if="step.data.shape === '원형'">
          <div><span class="text-grey">R:</span> {{ step.data.R ?? '-' }} mm</div>
          <div><span class="text-grey">T:</span> {{ step.data.T ?? '-' }} mm</div>
        </template>
        <template v-else>
          <div><span class="text-grey">W:</span> {{ step.data.W ?? '-' }} mm</div>
          <div><span class="text-grey">H:</span> {{ step.data.H ?? '-' }} mm</div>
          <div><span class="text-grey">T:</span> {{ step.data.T ?? '-' }} mm</div>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { WorkflowStep } from 'src/components/workflow/types'

defineProps<{ step: WorkflowStep }>()
</script>
