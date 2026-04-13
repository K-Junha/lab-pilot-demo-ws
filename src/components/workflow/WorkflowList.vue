<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 col">워크플로우 목록</div>
      <q-btn color="primary" icon="add" label="새 워크플로우" @click="emit('create')" />
    </div>

    <AgGridVue
      style="height: 500px; width: 100%;"
      :theme="gridTheme"
      :rowData="workflows"
      :columnDefs="columnDefs"
      :defaultColDef="defaultColDef"
      @grid-ready="onGridReady"
      @row-clicked="onRowClicked"
    />
  </div>
</template>

<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3'
import {
  ModuleRegistry,
  AllCommunityModule,
  type GridApi,
  type GridReadyEvent,
  type RowClickedEvent,
} from 'ag-grid-community'
import type { Workflow } from './types'
import { useGridTheme } from './gridTheme'

ModuleRegistry.registerModules([AllCommunityModule])

defineProps<{ workflows: Workflow[] }>()

const emit = defineEmits<{
  create: []
  select: [index: number]
}>()

const { gridTheme } = useGridTheme()
const defaultColDef = { flex: 1, resizable: true, sortable: true }

const columnDefs = [
  { field: 'name', headerName: '워크플로우 이름', minWidth: 200 },
  {
    headerName: '조성 수',
    width: 100,
    valueGetter: (params: any) => params.data?.compositions?.length ?? 0,
  },
  {
    headerName: '유리 종류',
    minWidth: 180,
    valueGetter: (params: any) => {
      const comps = params.data?.compositions ?? []
      return comps.map((c: any) => c.glassType).filter(Boolean).join(', ') || '-'
    },
  },
  {
    headerName: '공정 스텝',
    width: 110,
    valueGetter: (params: any) => params.data?.steps?.length ?? 0,
  },
  { field: 'status', headerName: '상태', width: 110 },
  { field: 'createdAt', headerName: '생성일', width: 180 },
]

let gridApi: GridApi | null = null

function onGridReady(params: GridReadyEvent) {
  gridApi = params.api
}

function onRowClicked(event: RowClickedEvent) {
  if (event.rowIndex != null) {
    emit('select', event.rowIndex)
  }
}
</script>
