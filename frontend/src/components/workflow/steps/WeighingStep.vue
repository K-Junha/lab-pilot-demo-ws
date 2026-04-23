<template>
  <div>
    <div class="row items-center q-mb-md">
      <DeviceSelector v-model="data.deviceId" />
    </div>

    <div class="text-subtitle2 q-mb-sm">전체 조성 원료 목표량</div>

    <div v-if="compositions.length === 0" class="text-grey text-caption">
      조성이 등록되지 않았습니다. 조성을 먼저 추가하세요.
    </div>

    <div v-for="comp in compositions" :key="comp.id" class="q-mb-md">
      <div class="text-subtitle2 q-mb-xs">
        {{ comp.name || `조성 #${comp.id}` }}
        <span v-if="!comp.batchWeight" class="text-caption text-orange q-ml-sm">
          <q-icon name="warning" size="xs" /> 배치량 미설정
        </span>
      </div>
      <q-markup-table flat bordered dense v-if="comp.oxides.length > 0">
        <thead>
          <tr>
            <th class="text-left">원료</th>
            <th class="text-right">배합비 (%)</th>
            <th class="text-right">목표량 (g)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(oxide, ri) in comp.oxides" :key="ri">
            <td>{{ oxide.oxide }}</td>
            <td class="text-right">{{ oxide.wt }}</td>
            <td class="text-right">{{ calcTargetG(comp, oxide) }}</td>
          </tr>
        </tbody>
      </q-markup-table>
      <div v-else class="text-grey text-caption">원료가 없습니다</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CompositionData, WeighingData } from '../types'
import DeviceSelector from '../DeviceSelector.vue'

const data = defineModel<WeighingData>('data', { required: true })
defineProps<{ compositions: CompositionData[] }>()

function calcTargetG(comp: CompositionData, oxide: { oxide: string; wt: number }) {
  if (!comp.batchWeight) return '-'
  return ((oxide.wt / 100) * comp.batchWeight).toFixed(3)
}
</script>
