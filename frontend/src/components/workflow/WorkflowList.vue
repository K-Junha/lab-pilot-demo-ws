<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 col">워크플로우 목록</div>
      <q-btn color="primary" icon="add" label="새 워크플로우" @click="emit('create')" />
    </div>

    <AgGridVue
      v-if="workflows.length > 0"
      style="height: 500px; width: 100%;"
      :theme="gridTheme"
      :rowData="workflows"
      :columnDefs="columnDefs"
      :defaultColDef="defaultColDef"
      @grid-ready="onGridReady"
      @row-clicked="onRowClicked"
    />
    <div v-else class="text-center text-grey q-mt-xl">
      <q-icon name="account_tree" size="64px" class="q-mb-md" color="grey-5" />
      <div class="text-h6">아직 워크플로우가 없습니다</div>
      <div class="text-caption">'새 워크플로우' 버튼을 눌러 시작하세요</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3'
import {
  ModuleRegistry,
  AllCommunityModule,
  type ColDef,
  type GridApi,
  type GridReadyEvent,
  type RowClickedEvent,
  type ICellRendererParams,
  type ValueGetterParams,
} from 'ag-grid-community'
import type { Workflow } from './types'
import { useGridTheme } from './gridTheme'

ModuleRegistry.registerModules([AllCommunityModule])

const props = defineProps<{ workflows: Workflow[] }>()

const emit = defineEmits<{
  create: []
  select: [index: number]
  start: [index: number]
  copy: [index: number]
  delete: [index: number]
}>()

const { gridTheme } = useGridTheme()
const defaultColDef = { flex: 1, resizable: true, sortable: true }

function statusColor(status: string) {
  switch (status) {
    case '계획중': return 'orange'
    case '진행중': return 'blue'
    case '완료': return 'green'
    default: return 'grey'
  }
}

const columnDefs: ColDef[] = [
  { field: 'name', headerName: '워크플로우 이름', minWidth: 200 },
  {
    headerName: '조성 수',
    width: 100,
    valueGetter: (params: ValueGetterParams) => (params.data as Workflow)?.compositions?.length ?? 0,
  },
  {
    headerName: '유리 종류',
    minWidth: 180,
    valueGetter: (params: ValueGetterParams) => {
      const comps = (params.data as Workflow)?.compositions ?? []
      return comps.map((c) => c.glassType).filter(Boolean).join(', ') || '-'
    },
  },
  {
    headerName: '공정 스텝',
    width: 110,
    valueGetter: (params: ValueGetterParams) => (params.data as Workflow)?.steps?.length ?? 0,
  },
  {
    headerName: '상태',
    width: 110,
    field: 'status',
    cellRenderer: (params: ICellRendererParams) => {
      const status = (params.data as Workflow)?.status ?? ''
      const span = document.createElement('span')
      span.textContent = status
      span.style.fontWeight = '600'
      span.style.color = statusColor(status) === 'orange' ? '#f57c00'
        : statusColor(status) === 'blue' ? '#1565c0'
        : statusColor(status) === 'green' ? '#2e7d32'
        : '#757575'
      return span
    },
  },
  { field: 'createdAt', headerName: '생성일', width: 180 },
  {
    headerName: '액션',
    width: 180,
    sortable: false,
    cellRenderer: (params: ICellRendererParams) => {
      const wf = params.data as Workflow
      const idx = props.workflows.findIndex((w) => w.id === wf?.id)
      const container = document.createElement('div')
      container.style.cssText = 'display:flex; align-items:center; height:100%; gap:4px'

      const makeBtn = (label: string, bg: string, onClick: () => void) => {
        const btn = document.createElement('button')
        btn.textContent = label
        btn.style.cssText = `font-size:11px; padding:2px 6px; background:${bg}; color:white; border:none; border-radius:4px; cursor:pointer`
        btn.addEventListener('click', (e) => { e.stopPropagation(); onClick() })
        return btn
      }

      if (wf?.status === '계획중') {
        container.appendChild(makeBtn('시작', '#1976d2', () => emit('start', idx)))
      }
      container.appendChild(makeBtn('복사', '#546e7a', () => emit('copy', idx)))
      container.appendChild(makeBtn('삭제', '#c62828', () => emit('delete', idx)))

      return container
    },
  },
]

let gridApi: GridApi | null = null

function onGridReady(params: GridReadyEvent) {
  gridApi = params.api
}

function onRowClicked(event: RowClickedEvent) {
  const target = event.event?.target as HTMLElement | undefined
  if (target?.tagName === 'BUTTON') return
  if (event.rowIndex != null) {
    emit('select', event.rowIndex)
  }
}
</script>
