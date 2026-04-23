<template>
  <div>
    <!-- 1. 유리 선택 -->
    <q-card>
      <q-card-section class="row items-center q-gutter-md">
        <div class="text-h6">1. 유리 종류 선택</div>
        <q-btn label="유리 선택" color="primary" @click="openGlassDialog" />
        <div v-if="data.glassType">선택: {{ data.glassType }}</div>
        <div v-if="data.batchWeight">요구량: {{ data.batchWeight }} g</div>
      </q-card-section>
    </q-card>

    <!-- 2. 목표 물성 -->
    <q-card class="q-mt-md">
      <q-card-section class="row items-center cursor-pointer" @click="section2Open = !section2Open">
        <div class="text-h6 col">2. 목표 물성 선택</div>
        <q-icon :name="section2Open ? 'keyboard_arrow_up' : 'keyboard_arrow_down'" size="sm" />
      </q-card-section>
      <q-slide-transition>
        <div v-show="section2Open">
          <q-card-section>
            <q-list bordered>
              <q-expansion-item
                v-for="cat in propertyCategories"
                :key="cat.label"
                :label="cat.label"
                :caption="cat.items.filter(p => data.selectedProperties.includes(p)).length + '/' + cat.items.length + ' 선택'"
                :icon="cat.icon"
                header-class="text-weight-medium"
              >
                <q-card>
                  <q-card-section class="q-pt-none">
                    <q-checkbox
                      v-for="p in cat.items"
                      :key="p"
                      v-model="data.selectedProperties"
                      :val="p"
                      :label="p"
                      class="q-mr-md"
                    />
                  </q-card-section>
                </q-card>
              </q-expansion-item>
            </q-list>
          </q-card-section>
        </div>
      </q-slide-transition>
    </q-card>

    <!-- 2-1. 목표 값 설정 -->
    <q-card class="q-mt-md" v-if="data.selectedProperties.length > 0">
      <q-card-section class="row items-center cursor-pointer" @click="section21Open = !section21Open">
        <div class="text-h6 col">2-1. 목표 값 설정</div>
        <q-icon :name="section21Open ? 'keyboard_arrow_up' : 'keyboard_arrow_down'" size="sm" />
      </q-card-section>
      <q-slide-transition>
        <div v-show="section21Open">
          <q-card-section>
            <AgGridVue
              style="height: 300px; width: 100%;"
              :theme="gridTheme"
              :rowData="data.propertyTargets"
              :columnDefs="propColumnDefs"
              :defaultColDef="defaultColDef"
              :rowDragManaged="true"
              :animateRows="true"
              @grid-ready="onPropGridReady"
              @cell-value-changed="onPropCellChanged"
              @row-drag-end="onPropRowDragEnd"
            />
          </q-card-section>
        </div>
      </q-slide-transition>
    </q-card>

    <!-- 3. 조성 설계 -->
    <q-card class="q-mt-md">
      <q-card-section class="row items-center cursor-pointer" @click="section3Open = !section3Open">
        <div class="text-h6 col">3. 조성 설계</div>
        <q-btn flat dense icon="add" label="산화물 추가" color="primary" class="q-mr-sm" @click.stop="addOxideDialog = true" />
        <q-icon :name="section3Open ? 'keyboard_arrow_up' : 'keyboard_arrow_down'" size="sm" />
      </q-card-section>
      <q-slide-transition>
        <div v-show="section3Open">
          <q-card-section>
            <AgGridVue
              style="height: 400px; width: 100%;"
              :theme="gridTheme"
              :rowData="data.oxides"
              :columnDefs="columnDefs"
              :defaultColDef="defaultColDef"
              @cell-value-changed="onCellValueChanged"
            />
            <div
              class="q-mt-sm"
              :class="totalWt === 100 ? 'text-green' : 'text-red'"
            >
              총합: {{ totalWt }} %
              <span v-if="totalWt !== 100">(100%가 되어야 합니다)</span>
            </div>
          </q-card-section>
        </div>
      </q-slide-transition>
    </q-card>

    <!-- 4. 추천 -->
    <q-card class="q-mt-md">
      <q-card-section class="row justify-between">
        <div class="text-h6">4. 조성 추천</div>
        <q-btn label="추천 받기" color="secondary" @click="recommendComposition" />
      </q-card-section>
    </q-card>

    <!-- Dialog: 유리 선택 + 요구량 입력 -->
    <q-dialog v-model="glassDialog">
      <q-card style="min-width: 440px">
        <q-card-section>
          <div class="text-h6">유리 종류 선택</div>
        </q-card-section>
        <q-card-section>
          <q-input v-model.number="tempWeight" type="number" label="요구량 (g)" outlined />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pt-sm">
          <q-list bordered separator>
            <q-item v-for="g in glassTypes" :key="g.key" clickable v-ripple @click="onGlassClick(g)">
              <q-item-section>
                <q-item-label>{{ g.label }}</q-item-label>
                <q-item-label caption>{{ g.desc }}</q-item-label>
              </q-item-section>
              <q-item-section side v-if="g.key === 'Chalcogenide'">
                <q-icon name="chevron_right" />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Chalcogenide 하위 선택 -->
    <q-dialog v-model="chalcoDialog">
      <q-card style="min-width: 380px">
        <q-card-section>
          <div class="text-h6">Chalcogenide 조성 선택</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-list bordered separator>
            <q-item v-for="c in chalcoOptions" :key="c.label" clickable v-ripple @click="confirmGlass('Chalcogenide - ' + c.label, c.oxides)">
              <q-item-section>{{ c.label }}</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Dialog: 산화물 추가 -->
    <q-dialog v-model="addOxideDialog" @show="loadOxideOptions">
      <q-card style="min-width: 380px">
        <q-card-section>
          <div class="text-h6">산화물 추가</div>
        </q-card-section>
        <q-card-section>
          <q-select
            v-model="selectedOxide"
            :options="filteredOxideOptions"
            label="산화물 선택"
            outlined
            use-input
            input-debounce="0"
            option-label="label"
            option-value="value"
            emit-value
            map-options
            :loading="oxideLoading"
            @filter="onOxideFilter"
            autofocus
          >
            <template #no-option>
              <q-item><q-item-section class="text-grey">결과 없음</q-item-section></q-item>
            </template>
            <template #option="{ opt, itemProps }">
              <q-item v-bind="itemProps">
                <q-item-section>
                  <q-item-label>{{ opt.label }}</q-item-label>
                  <q-item-label caption>{{ opt.caption }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-badge :color="categoryColor(opt.category)" :label="opt.categoryLabel" />
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="취소" v-close-popup />
          <q-btn label="추가" color="primary" :disable="!selectedOxide" @click="doAddOxide" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import { useMaterials } from '../../../composables/useMaterials'
import {
  ModuleRegistry,
  AllCommunityModule,
  type GridApi,
  type GridReadyEvent,
  type CellValueChangedEvent,
  type ValueGetterParams,
  type ICellRendererParams,
  type EditableCallbackParams,
  type CellClassParams,
  type ValueParserParams,
} from 'ag-grid-community'
import { useGridTheme } from '../gridTheme'

ModuleRegistry.registerModules([AllCommunityModule])

interface CompositionRow {
  oxide: string
  wt: number
}

interface PropertyTarget {
  property: string
  unit: string
  mode: '단일값' | '범위' | '최솟값' | '최댓값'
  target: number | null
  min: number | null
  max: number | null
}

export interface CompositionData {
  glassType: string | null
  batchWeight: number | null
  oxides: CompositionRow[]
  selectedProperties: string[]
  propertyTargets: PropertyTarget[]
}

const data = defineModel<CompositionData>('data', { required: true })

/* ===== UI State ===== */
const section2Open = ref(true)
const section21Open = ref(true)
const section3Open = ref(true)
const glassDialog = ref(false)
const chalcoDialog = ref(false)
const addOxideDialog = ref(false)
const tempWeight = ref<number | null>(null)
const selectedOxide = ref<string | null>(null)

/* ===== Materials (oxide list) ===== */
const { oxides: allOxides, loading: oxideLoading, fetchOxides } = useMaterials()

interface OxideOption {
  label: string
  value: string
  caption: string
  category: string
  categoryLabel: string
}

const CATEGORY_MAP: Record<string, { label: string; color: string }> = {
  network_former:   { label: '형성체', color: 'blue' },
  network_modifier: { label: '수식체', color: 'orange' },
  intermediate:     { label: '중간',   color: 'green' },
  other:            { label: '기타',   color: 'grey' },
}

function categoryColor(cat: string) { return CATEGORY_MAP[cat]?.color ?? 'grey' }

const oxideOptions = computed<OxideOption[]>(() => {
  const existing = new Set(data.value.oxides.map(o => o.oxide))
  return allOxides.value
    .filter(o => !existing.has(o.formula))
    .map(o => ({
      label: o.formula,
      value: o.formula,
      caption: o.name_ko,
      category: o.category,
      categoryLabel: CATEGORY_MAP[o.category]?.label ?? '기타',
    }))
})

let oxideFilterText = ''
const filteredOxideOptions = ref<OxideOption[]>([])

function onOxideFilter(val: string, update: (fn: () => void) => void) {
  oxideFilterText = val.toLowerCase()
  update(() => {
    if (!val) {
      filteredOxideOptions.value = oxideOptions.value
    } else {
      filteredOxideOptions.value = oxideOptions.value.filter(
        o => o.label.toLowerCase().includes(oxideFilterText)
          || o.caption.includes(oxideFilterText)
      )
    }
  })
}

async function loadOxideOptions() {
  selectedOxide.value = null
  await fetchOxides()
  filteredOxideOptions.value = oxideOptions.value
}

/* ===== Property categories ===== */
interface PropertyCategory {
  label: string
  icon: string
  items: string[]
}

const propertyCategories: PropertyCategory[] = [
  { label: '열적 특성', icon: 'thermostat', items: ['Tg', 'Ts', 'CTE', 'Tc'] },
  { label: '기계적 특성', icon: 'fitness_center', items: ['Density', "Young's modulus", 'Poisson ratio', 'Hardness'] },
  { label: '광학적 특성', icon: 'visibility', items: ['Nd', 'Vd'] },
  { label: '점도 특성', icon: 'water_drop', items: ['Viscosity'] },
  { label: '전기적 특성', icon: 'bolt', items: ['ε', 'tanδ'] },
]

const propertyUnits: Record<string, string> = {
  Tg: '°C', Ts: '°C', CTE: '×10⁻⁷/°C', Tc: '°C',
  Density: 'g/cm³', "Young's modulus": 'GPa', 'Poisson ratio': '-', Hardness: 'GPa',
  Nd: '-', Vd: '-',
  Viscosity: 'log(η/Pa·s)',
  'ε': '-', 'tanδ': '-',
}

/* ===== Property targets sync ===== */
watch(() => data.value.selectedProperties, (newProps) => {
  const existing = data.value.propertyTargets
  const kept = existing.filter((r) => newProps.includes(r.property))
  const keptNames = new Set(kept.map((r) => r.property))
  const added = newProps
    .filter((p) => !keptNames.has(p))
    .map((p): PropertyTarget => ({
      property: p,
      unit: propertyUnits[p] ?? '-',
      mode: '단일값',
      target: null,
      min: null,
      max: null,
    }))
  data.value.propertyTargets = [...kept, ...added]
}, { immediate: true, deep: true })

/* ===== Property Grid ===== */
const propColumnDefs = [
  { headerName: '', width: 50, rowDrag: true, sortable: false, filter: false, suppressHeaderMenuButton: true },
  { headerName: '우선순위', width: 100, editable: false, valueGetter: (params: ValueGetterParams<PropertyTarget>) => params.node?.rowIndex != null ? params.node.rowIndex + 1 : '' },
  { field: 'property', headerName: '물성', editable: false, width: 140 },
  { field: 'unit', headerName: '단위', editable: false, width: 120 },
  {
    field: 'mode', headerName: '모드', editable: true, cellEditor: 'agSelectCellEditor',
    cellEditorParams: { values: ['단일값', '범위', '최솟값', '최댓값'] },
    singleClickEdit: true,
    cellRenderer: (params: ICellRendererParams<PropertyTarget>) => `<div style="display:flex;align-items:center;justify-content:space-between;width:100%;cursor:pointer;"><span>${params.value ?? ''}</span><span style="font-size:10px;color:#888;">▼</span></div>`,
    width: 110,
  },
  {
    field: 'target', headerName: '목표값',
    editable: (params: EditableCallbackParams<PropertyTarget>) => params.data?.mode === '단일값',
    cellStyle: (params: CellClassParams<PropertyTarget>) => params.data?.mode !== '단일값' ? { display: 'none' } : {},
    cellRenderer: (params: ICellRendererParams<PropertyTarget>) => params.data?.mode === '단일값' ? (params.value ?? '') : '',
    valueParser: (p: ValueParserParams<PropertyTarget>) => p.newValue === '' ? null : Number(p.newValue),
  },
  {
    field: 'min', headerName: '최소',
    editable: (params: EditableCallbackParams<PropertyTarget>) => params.data?.mode === '범위',
    cellStyle: (params: CellClassParams<PropertyTarget>) => params.data?.mode !== '범위' ? { display: 'none' } : {},
    cellRenderer: (params: ICellRendererParams<PropertyTarget>) => params.data?.mode === '범위' ? (params.value ?? '') : '',
    valueParser: (p: ValueParserParams<PropertyTarget>) => p.newValue === '' ? null : Number(p.newValue),
  },
  {
    field: 'max', headerName: '최대',
    editable: (params: EditableCallbackParams<PropertyTarget>) => params.data?.mode === '범위',
    cellStyle: (params: CellClassParams<PropertyTarget>) => params.data?.mode !== '범위' ? { display: 'none' } : {},
    cellRenderer: (params: ICellRendererParams<PropertyTarget>) => params.data?.mode === '범위' ? (params.value ?? '') : '',
    valueParser: (p: ValueParserParams<PropertyTarget>) => p.newValue === '' ? null : Number(p.newValue),
  },
]

let propGridApi: GridApi | null = null

function onPropGridReady(params: GridReadyEvent) { propGridApi = params.api }

function onPropCellChanged(event: CellValueChangedEvent) {
  const d = event.data as PropertyTarget
  if (d.mode === '단일값') { d.min = null; d.max = null }
  else if (d.mode === '범위') { d.target = null }
  else if (d.mode === '최솟값') { d.target = null; d.min = null; d.max = null }
  else if (d.mode === '최댓값') { d.target = null; d.min = null; d.max = null }
  const idx = event.rowIndex
  if (idx != null) data.value.propertyTargets[idx] = { ...d }
  propGridApi?.refreshCells({ force: true })
}

function onPropRowDragEnd() {
  if (!propGridApi) return
  const newOrder: PropertyTarget[] = []
  propGridApi.forEachNode((node) => { if (node.data) newOrder.push(node.data) })
  data.value.propertyTargets.splice(0, data.value.propertyTargets.length, ...newOrder)
  propGridApi.refreshCells({ force: true })
}

/* ===== Glass types ===== */
interface GlassType { key: string; label: string; desc: string; oxides?: CompositionRow[] }

const glassTypes: GlassType[] = [
  { key: 'Silicate', label: 'Silicate', desc: 'SiO₂', oxides: [{ oxide: 'SiO₂', wt: 100 }] },
  { key: 'Aluminosilicate', label: 'Aluminosilicate', desc: 'SiO₂ + Al₂O₃ + (추가)', oxides: [{ oxide: 'SiO₂', wt: 0 }, { oxide: 'Al₂O₃', wt: 0 }] },
  { key: 'Borosilicate', label: 'Borosilicate', desc: 'SiO₂ + B₂O₃ + (추가)', oxides: [{ oxide: 'SiO₂', wt: 0 }, { oxide: 'B₂O₃', wt: 0 }] },
  { key: 'Phosphate', label: 'Phosphate glass', desc: 'P₂O₅ + (추가)', oxides: [{ oxide: 'P₂O₅', wt: 0 }] },
  { key: 'Chalcogenide', label: 'Chalcogenide glass', desc: '하위 조성 선택' },
  { key: 'Custom', label: '신규 유리 설계', desc: '빈 테이블에서 직접 설계', oxides: [] },
]

const chalcoOptions: { label: string; oxides: CompositionRow[] }[] = [
  { label: 'As + S', oxides: [{ oxide: 'As', wt: 0 }, { oxide: 'S', wt: 0 }] },
  { label: 'Ge + As + Se', oxides: [{ oxide: 'Ge', wt: 0 }, { oxide: 'As', wt: 0 }, { oxide: 'Se', wt: 0 }] },
  { label: 'Ge + Sb + Se', oxides: [{ oxide: 'Ge', wt: 0 }, { oxide: 'Sb', wt: 0 }, { oxide: 'Se', wt: 0 }] },
  { label: 'Ge + Te + Sb', oxides: [{ oxide: 'Ge', wt: 0 }, { oxide: 'Te', wt: 0 }, { oxide: 'Sb', wt: 0 }] },
]

/* ===== Composition Grid ===== */
const { gridTheme } = useGridTheme()
const columnDefs = [
  { field: 'oxide', headerName: '산화물' },
  { field: 'wt', headerName: 'wt (%)', editable: true, valueParser: (p: ValueParserParams<CompositionRow>) => Number(p.newValue) },
]
const defaultColDef = { flex: 1, resizable: true }

const totalWt = computed(() => data.value.oxides.reduce((sum, r) => sum + (Number(r.wt) || 0), 0))

function onCellValueChanged(event: CellValueChangedEvent) {
  const idx = event.rowIndex
  if (idx == null) return
  data.value.oxides[idx] = { ...event.data }
}

/* ===== Dialogs ===== */
function openGlassDialog() { tempWeight.value = 100; glassDialog.value = true }

function onGlassClick(g: GlassType) {
  if (!tempWeight.value || tempWeight.value <= 0) { alert('요구량을 입력하세요'); return }
  if (g.key === 'Chalcogenide') { glassDialog.value = false; chalcoDialog.value = true; return }
  confirmGlass(g.label, g.oxides ?? [])
}

function confirmGlass(label: string, oxides: CompositionRow[]) {
  if (!tempWeight.value || tempWeight.value <= 0) { alert('요구량을 입력하세요'); return }
  data.value.glassType = label
  data.value.batchWeight = tempWeight.value
  glassDialog.value = false
  chalcoDialog.value = false
  data.value.oxides.splice(0, data.value.oxides.length, ...oxides.map((r) => ({ ...r })))
}

function doAddOxide() {
  if (!selectedOxide.value) return
  data.value.oxides.push({ oxide: selectedOxide.value, wt: 0 })
  selectedOxide.value = null
  addOxideDialog.value = false
}

function recommendComposition() { console.log('추천 요청:', data.value.oxides) }
</script>
