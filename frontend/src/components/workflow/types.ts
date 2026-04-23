export interface CompositionRow {
  oxide: string
  wt: number
}

export interface SilaServer {
  id: string
  name: string
  device: string
  icon: string
  address: string
  online: boolean
  status: 'Idle' | 'Running' | 'Error' | 'Offline'
}

export interface SilaManager {
  id: string
  name: string
  lab: string
  online: boolean
  servers: SilaServer[]
}

export interface PropertyTarget {
  property: string
  unit: string
  mode: '단일값' | '범위' | '최솟값' | '최댓값'
  target: number | null
  min: number | null
  max: number | null
}

export interface CompositionData {
  id: number
  name: string
  glassType: string | null
  batchWeight: number | null
  oxides: CompositionRow[]
  selectedProperties: string[]
  propertyTargets: PropertyTarget[]
}

export type StepType = 'weighing' | 'mixing' | 'forming' | 'firing' | 'heattreat' | 'machining' | 'analysis'

export interface StepDef {
  key: StepType
  label: string
  desc: string
  icon: string
  color: string
}

/* ── 각 스텝별 data 타입 — WorkflowStep.data가 이 중 하나 ── */

export interface WeighingRowEntry { actualG: number | null }
export interface WeighingData {
  deviceId: string | null
  // compId → 산화물키 → 실측량 엔트리 (중첩 Record)
  rows: Record<string | number, Record<string, WeighingRowEntry>>
}

export interface MixingData {
  deviceId: string | null
  duration: number | null
  memo: string
}

export type ShapeType = '원형' | '바형'
export interface FormingData {
  deviceId: string | null; shape: ShapeType
  R: number | null; T: number | null; W: number | null; H: number | null
}

export interface FiringSegment { rampRate: number | null; temp: number | null; holdMin: number | null }
export interface FiringData { deviceId: string | null; segments: FiringSegment[] }

export interface HeatTreatData {
  deviceId: string | null
  temp: number | null; duration: number | null; method: string; memo: string
}

export interface MachiningData {
  deviceId: string | null; shape: ShapeType
  R: number | null; T: number | null; W: number | null; H: number | null
}

export interface AnalysisMeasurement { measured: number | null; unit?: string }
export interface AnalysisData {
  deviceId: string | null
  compositionId: number | null
  measurements: Record<string, AnalysisMeasurement>
}

// 모든 공정 스텝 데이터의 유니언 타입 — WorkflowStep.data의 실제 타입
export type StepData =
  | WeighingData | MixingData | FormingData | FiringData
  | HeatTreatData | MachiningData | AnalysisData

export interface WorkflowStep {
  uid: number
  type: StepType
  data: StepData
}

export interface Workflow {
  id: number
  name: string
  compositions: CompositionData[]
  steps: WorkflowStep[]
  createdAt: string
  status: string
}

export const stepDefs: Record<StepType, StepDef> = {
  weighing:  { key: 'weighing',  label: '원료 칭량', desc: '원료별 목표량 vs 실칭량, 오차 계산',   icon: 'scale',                  color: 'blue' },
  mixing:    { key: 'mixing',    label: '믹싱',     desc: '믹싱 시간, 메모',                     icon: 'blender',                color: 'teal' },
  forming:   { key: 'forming',   label: '성형',     desc: '원형/바형 치수 입력',                  icon: 'view_in_ar',             color: 'orange' },
  firing:    { key: 'firing',    label: '소성/용융', desc: '다단계 승온·온도·유지시간',            icon: 'local_fire_department',   color: 'red' },
  heattreat: { key: 'heattreat', label: '열처리',   desc: '서냉 온도·시간·방식',                 icon: 'thermostat',             color: 'deep-purple' },
  machining: { key: 'machining', label: '가공',     desc: '원형/바형 최종 치수',                  icon: 'precision_manufacturing', color: 'brown' },
  analysis:  { key: 'analysis',  label: '측정/분석', desc: '목표 특성 측정 및 판정',               icon: 'science',                color: 'green' },
}

export function createStepData(type: StepType): StepData {
  switch (type) {
    case 'weighing':
      return { deviceId: null, rows: {} } as WeighingData
    case 'mixing':
      return { deviceId: null, duration: null, memo: '' }
    case 'forming':
      return { deviceId: null, shape: '원형', R: null, T: null, W: null, H: null }
    case 'firing':
      return { deviceId: null, segments: [{ rampRate: null, temp: null, holdMin: null }] }
    case 'heattreat':
      return { deviceId: null, temp: null, duration: null, method: '자연 냉각', memo: '' }
    case 'machining':
      return { deviceId: null, shape: '원형', R: null, T: null, W: null, H: null }
    case 'analysis':
      return { deviceId: null, compositionId: null, measurements: {} }
  }
}

export function createEmptyComposition(id: number): CompositionData {
  return {
    id,
    name: '',
    glassType: null,
    batchWeight: null,
    oxides: [],
    selectedProperties: [],
    propertyTargets: [],
  }
}

/* ── Experiment execution types ── */

export type StepExecStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface DataPoint {
  t: number          // elapsed seconds
  value: number
  label?: string
}

export interface StepExecution {
  uid: number        // matches WorkflowStep.uid
  type: StepType
  status: StepExecStatus
  startedAt: string | null
  completedAt: string | null
  elapsed: number    // seconds
  series: Record<string, DataPoint[]>   // e.g. { temperature: [...], pressure: [...] }
  result: Record<string, unknown> | null
}

export interface ExperimentRun {
  id: number
  workflowId: number
  workflowName: string
  steps: StepExecution[]
  startedAt: string
  status: 'idle' | 'running' | 'completed'
}
