import { ref, computed, watch } from 'vue'
import type {
  Workflow, WorkflowStep, StepExecution, ExperimentRun, DataPoint,
  FiringData, HeatTreatData,
} from 'src/components/workflow/types'

const STORAGE_KEY = 'lab-pilot-experiment'

/* ── Simulator helpers ── */

function noise(base: number, pct = 0.02) {
  return base + base * pct * (Math.random() - 0.5) * 2
}

/** Generate next simulated data points per step type */
function simulate(step: StepExecution, ws: WorkflowStep, elapsed: number) {
  const t = elapsed
  switch (step.type) {
    case 'mixing': {
      const targetRpm = 300
      const rpm = noise(targetRpm, 0.05)
      push(step, 'rpm', { t, value: Math.round(rpm) })
      step.result = { currentRpm: Math.round(rpm) }
      break
    }
    case 'forming': {
      const maxPressure = 50 // kN
      const progress = Math.min(elapsed / 30, 1)
      const pressure = noise(maxPressure * progress, 0.03)
      const displacement = noise(progress * 10, 0.02) // mm
      push(step, 'pressure', { t, value: +pressure.toFixed(1) })
      push(step, 'displacement', { t, value: +displacement.toFixed(2) })
      step.result = { pressure: +pressure.toFixed(1), displacement: +displacement.toFixed(2) }
      break
    }
    case 'firing': {
      // switch case가 타입을 보장하므로 안전한 타입 단언
      const segs = (ws.data as FiringData).segments ?? [{ rampRate: 5, temp: 1500, holdMin: 60 }]
      const targetTemp = computeFiringTarget(segs, elapsed)
      const actual = noise(targetTemp, 0.01)
      push(step, 'temperature', { t, value: +actual.toFixed(1) })
      push(step, 'target', { t, value: +targetTemp.toFixed(1) })
      step.result = { currentTemp: +actual.toFixed(1), targetTemp: +targetTemp.toFixed(1) }
      break
    }
    case 'heattreat': {
      const startTemp = (ws.data as HeatTreatData).temp ?? 600
      const duration = ((ws.data as HeatTreatData).duration ?? 60) * 60 // seconds
      const progress = Math.min(elapsed / Math.max(duration, 1), 1)
      const temp = startTemp * (1 - progress * 0.9) + 25 * progress * 0.9
      const actual = noise(temp, 0.01)
      push(step, 'temperature', { t, value: +actual.toFixed(1) })
      step.result = { currentTemp: +actual.toFixed(1) }
      break
    }
    case 'machining': {
      const spindleRpm = 1200
      const feedRate = 0.05 // mm/rev
      push(step, 'spindleRpm', { t, value: Math.round(noise(spindleRpm, 0.03)) })
      push(step, 'feedRate', { t, value: +noise(feedRate, 0.05).toFixed(3) })
      step.result = { spindleRpm: Math.round(noise(spindleRpm, 0.03)), feedRate: +noise(feedRate, 0.05).toFixed(3) }
      break
    }
    case 'analysis': {
      // Analysis produces discrete measurement bursts
      if (elapsed % 5 < 1) {
        const value = noise(50, 0.1)
        push(step, 'measurement', { t, value: +value.toFixed(2) })
        step.result = { lastMeasurement: +value.toFixed(2) }
      }
      break
    }
    default:
      break
  }
}

function push(step: StepExecution, key: string, pt: DataPoint) {
  if (!step.series[key]) step.series[key] = []
  step.series[key].push(pt)
}

function computeFiringTarget(segments: { rampRate: number | null; temp: number | null; holdMin: number | null }[], elapsed: number): number {
  let time = 0
  let currentTemp = 25
  for (const seg of segments) {
    const rate = seg.rampRate ?? 5
    const target = seg.temp ?? 1000
    const hold = (seg.holdMin ?? 10) * 60

    const rampTime = (Math.abs(target - currentTemp) / rate) * 60  // °C/min → 초(sec) 변환
    if (elapsed <= time + rampTime) {
      const frac = (elapsed - time) / rampTime
      return currentTemp + (target - currentTemp) * frac
    }
    time += rampTime
    currentTemp = target

    if (elapsed <= time + hold) return currentTemp
    time += hold
  }
  return currentTemp
}

/* ── Composable ── */

const currentRun = ref<ExperimentRun | null>(loadRun())
const activeStepUid = ref<number | null>(currentRun.value?.steps[0]?.uid ?? null)
const timers: Map<number, ReturnType<typeof setInterval>> = new Map()
const elapsedTimers: Map<number, ReturnType<typeof setInterval>> = new Map()

function loadRun(): ExperimentRun | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const run = JSON.parse(raw) as ExperimentRun
    // running 상태였던 스텝은 중단된 것으로 처리
    run.steps.forEach(s => {
      if (s.status === 'running') {
        s.status = 'pending'
        s.startedAt = null
        s.elapsed = 0
        s.series = {}
      }
    })
    if (run.status === 'running') run.status = 'idle'
    return run
  } catch {
    return null
  }
}

function persistRun() {
  if (currentRun.value) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(currentRun.value))
    } catch { /* quota exceeded — ignore */ }
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

// 실험 상태 변경 시 자동 저장
watch(currentRun, persistRun, { deep: true })

export function useExperimentRunner() {

  function createRun(workflow: Workflow): ExperimentRun {
    const steps: StepExecution[] = workflow.steps.map(s => ({
      uid: s.uid,
      type: s.type,
      status: 'pending',
      startedAt: null,
      completedAt: null,
      elapsed: 0,
      series: {},
      result: null,
    }))

    const run: ExperimentRun = {
      id: Date.now(),
      workflowId: workflow.id,
      workflowName: workflow.name,
      steps,
      startedAt: new Date().toISOString(),
      status: 'idle',
    }
    currentRun.value = run
    activeStepUid.value = steps[0]?.uid ?? null
    return run
  }

  function startStep(uid: number, workflowStep: WorkflowStep) {
    if (!currentRun.value) return
    const step = currentRun.value.steps.find(s => s.uid === uid)
    if (!step || step.status === 'running' || step.status === 'completed') return

    step.status = 'running'
    step.startedAt = new Date().toISOString()
    step.elapsed = 0
    step.series = {}
    currentRun.value.status = 'running'
    activeStepUid.value = uid

    // Elapsed counter — every 1s
    const elTimer = setInterval(() => {
      step.elapsed++
    }, 1000)
    elapsedTimers.set(uid, elTimer)

    // 칭량 스텝은 시뮬레이션 불필요 (WeighingRunner가 직접 관리)
    if (step.type === 'weighing') return

    // Data simulation — every 1s
    const timer = setInterval(() => {
      try {
        simulate(step, workflowStep, step.elapsed)
      } catch (e) {
        console.error('[Experiment] Simulation error:', e)
        step.status = 'failed'
        clearTimer(uid)
      }
    }, 1000)
    timers.set(uid, timer)
  }

  function stopStep(uid: number) {
    if (!currentRun.value) return
    const step = currentRun.value.steps.find(s => s.uid === uid)
    if (!step) return

    step.status = 'completed'
    step.completedAt = new Date().toISOString()

    clearTimer(uid)

    // Check if all done
    if (currentRun.value.steps.every(s => s.status === 'completed')) {
      currentRun.value.status = 'completed'
    }
  }

  function clearTimer(uid: number) {
    const t = timers.get(uid)
    if (t) { clearInterval(t); timers.delete(uid) }
    const et = elapsedTimers.get(uid)
    if (et) { clearInterval(et); elapsedTimers.delete(uid) }
  }

  function cleanup() {
    timers.forEach(t => clearInterval(t))
    timers.clear()
    elapsedTimers.forEach(t => clearInterval(t))
    elapsedTimers.clear()
  }

  const activeStep = computed(() =>
    currentRun.value?.steps.find(s => s.uid === activeStepUid.value) ?? null
  )

  return {
    currentRun,
    activeStepUid,
    activeStep,
    createRun,
    startStep,
    stopStep,
    cleanup,
  }
}
