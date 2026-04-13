<template>
  <div>
    <!-- Controls -->
    <div class="row items-center q-gutter-md q-mb-md">
      <q-btn
        v-if="execution.status === 'pending'"
        color="primary"
        icon="play_arrow"
        label="실험 시작"
        @click="$emit('start')"
      />
      <q-btn
        v-if="execution.status === 'running'"
        color="negative"
        icon="stop"
        label="실험 중지"
        @click="$emit('stop')"
      />
      <q-badge v-if="execution.status === 'completed'" color="green" class="text-body2 q-pa-sm">
        <q-icon name="check_circle" class="q-mr-xs" /> 완료
      </q-badge>
      <q-badge v-if="execution.status === 'running'" color="blue" class="text-body2 q-pa-sm">
        <q-icon name="sensors" class="q-mr-xs" /> 수집 중
      </q-badge>
      <span v-if="execution.elapsed > 0" class="text-caption text-grey">
        경과: {{ formatElapsed(execution.elapsed) }}
      </span>
    </div>

    <!-- Live metrics cards -->
    <div v-if="execution.status !== 'pending'" class="row q-gutter-md q-mb-md">
      <q-card v-for="(label, key) in metricLabels" :key="key" bordered flat class="col-auto" style="min-width: 150px;">
        <q-card-section class="q-pa-sm text-center">
          <div class="text-caption text-grey">{{ label }}</div>
          <div class="text-h5 text-weight-bold">{{ currentValue(key as string) }}</div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Chart for temperature-based steps -->
    <div v-if="showChart && execution.status !== 'pending'" style="height: 300px;">
      <Line :data="chartData" :options="chartOptions" />
    </div>

    <!-- Data table for non-chart steps -->
    <div v-if="!showChart && execution.status !== 'pending' && hasData">
      <q-markup-table flat bordered dense>
        <thead>
          <tr>
            <th>시간 (s)</th>
            <th v-for="(label, key) in metricLabels" :key="key">{{ label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(_, i) in recentPoints" :key="i">
            <td class="text-center">{{ recentPoints[i]?.t ?? '' }}</td>
            <td v-for="(__, key) in metricLabels" :key="key" class="text-center">
              {{ getPointAt(key as string, i) }}
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import type { StepExecution, StepType } from 'src/components/workflow/types'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend, Filler)

const props = defineProps<{
  execution: StepExecution
}>()

defineEmits<{
  start: []
  stop: []
}>()

function formatElapsed(s: number) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}분 ${sec}초`
}

/* Metric labels per step type */
const metricMap: Record<string, Record<string, string>> = {
  mixing:    { rpm: 'RPM' },
  forming:   { pressure: '압력 (kN)', displacement: '변위 (mm)' },
  firing:    { temperature: '온도 (°C)', target: '목표 (°C)' },
  heattreat: { temperature: '온도 (°C)' },
  machining: { spindleRpm: '스핀들 RPM', feedRate: '이송속도 (mm/rev)' },
  analysis:  { measurement: '측정값' },
}

const metricLabels = computed(() => metricMap[props.execution.type] ?? {})

const showChart = computed(() =>
  ['firing', 'heattreat'].includes(props.execution.type)
)

const hasData = computed(() =>
  Object.values(props.execution.series).some(arr => arr.length > 0)
)

function currentValue(key: string) {
  const arr = props.execution.series[key]
  if (!arr || arr.length === 0) return '-'
  return arr[arr.length - 1]!.value
}

/* Recent 20 points for table */
const recentPoints = computed(() => {
  const firstKey = Object.keys(metricLabels.value)[0]
  if (!firstKey) return []
  const arr = props.execution.series[firstKey] ?? []
  return arr.slice(-20)
})

function getPointAt(key: string, index: number) {
  const arr = props.execution.series[key] ?? []
  const startIdx = Math.max(arr.length - 20, 0)
  return arr[startIdx + index]?.value ?? '-'
}

/* Chart data */
const chartColors: Record<string, string> = {
  temperature: '#f44336',
  target: '#2196f3',
}

const chartData = computed(() => {
  const labels = (props.execution.series['temperature'] ?? []).map(p => p.t)
  const datasets = Object.entries(metricLabels.value).map(([key, label]) => ({
    label: label as string,
    data: (props.execution.series[key] ?? []).map(p => p.value),
    borderColor: chartColors[key] ?? '#4caf50',
    backgroundColor: 'transparent',
    tension: 0.3,
    pointRadius: 0,
    borderWidth: 2,
  }))
  return { labels, datasets }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 0 },
  scales: {
    x: { title: { display: true, text: '시간 (s)' } },
    y: { title: { display: true, text: '°C' }, beginAtZero: true },
  },
  plugins: {
    legend: { position: 'top' as const },
  },
}
</script>
