<template>
  <div>
    <!-- List mode -->
    <template v-if="!editingComp">
      <div class="row items-center q-mb-md">
        <div class="text-h6 col">조성 목록 ({{ compositions.length }})</div>
        <q-btn color="primary" icon="add" label="조성 추가" @click="addComposition" />
      </div>

      <AgGridVue
        v-if="compositions.length > 0"
        style="height: 350px; width: 100%;"
        :theme="gridTheme"
        :rowData="compositions"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        @row-clicked="onRowClicked"
      />

      <div v-else class="text-center text-grey q-pa-xl">
        조성을 추가하세요
      </div>
    </template>

    <!-- Edit mode -->
    <template v-else>
      <div class="row items-center q-mb-md">
        <q-btn flat icon="arrow_back" @click="closeEditor" />
        <div class="text-h6 col q-ml-sm">{{ editingComp.name || '새 조성' }}</div>
        <q-input
          v-model="editingComp.name"
          label="조성 이름"
          outlined
          dense
          style="min-width: 200px;"
          class="q-mr-md"
        />
        <q-btn flat label="삭제" color="red" icon="delete" class="q-mr-sm" @click="deleteCurrentComp" />
        <q-btn flat label="닫기" color="grey" @click="closeEditor" />
      </div>

      <CompositionStep :data="editingComp" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useQuasar } from 'quasar'
import { AgGridVue } from 'ag-grid-vue3'
import {
  ModuleRegistry,
  AllCommunityModule,
  type RowClickedEvent,
} from 'ag-grid-community'
import type { CompositionData } from '../types'
import { createEmptyComposition } from '../types'
import CompositionStep from './CompositionStep.vue'
import { useGridTheme } from '../gridTheme'

ModuleRegistry.registerModules([AllCommunityModule])

const $q = useQuasar()
const props = defineProps<{ compositions: CompositionData[] }>()

const editingComp = ref<CompositionData | null>(null)
const editIndex = ref<number | null>(null)

let compIdSeq = props.compositions.reduce((max, c) => Math.max(max, c.id), 0)

watch(() => props.compositions, (comps) => {
  compIdSeq = comps.reduce((max, c) => Math.max(max, c.id), 0)
})

const { gridTheme } = useGridTheme()
const defaultColDef = { flex: 1, resizable: true, sortable: true }

const columnDefs = [
  { field: 'name', headerName: '조성 이름', minWidth: 160 },
  { field: 'glassType', headerName: '유리 종류', minWidth: 140, valueFormatter: (p: any) => p.value ?? '-' },
  {
    headerName: '산화물',
    minWidth: 200,
    valueGetter: (p: any) => p.data?.oxides?.map((o: any) => o.oxide).join(', ') || '-',
  },
  {
    headerName: '총합 (wt%)',
    width: 120,
    valueGetter: (p: any) => p.data?.oxides?.reduce((s: number, o: any) => s + (Number(o.wt) || 0), 0) ?? 0,
  },
  { field: 'batchWeight', headerName: '요구량 (g)', width: 120, valueFormatter: (p: any) => p.value ?? '-' },
]

function addComposition() {
  const comp = createEmptyComposition(++compIdSeq)
  comp.name = `조성 ${props.compositions.length + 1}`
  props.compositions.push(comp)
  editingComp.value = comp
  editIndex.value = props.compositions.length - 1
}

function onRowClicked(event: RowClickedEvent) {
  if (event.rowIndex != null) {
    editIndex.value = event.rowIndex
    editingComp.value = props.compositions[event.rowIndex]!
  }
}

function closeEditor() {
  editingComp.value = null
  editIndex.value = null
}

function deleteCurrentComp() {
  if (editIndex.value == null) return
  $q.dialog({
    title: '조성 삭제',
    message: '이 조성을 삭제하시겠습니까?',
    cancel: { flat: true, label: '취소' },
    ok: { color: 'negative', label: '삭제' },
  }).onOk(() => {
    props.compositions.splice(editIndex.value!, 1)
    closeEditor()
  })
}
</script>
