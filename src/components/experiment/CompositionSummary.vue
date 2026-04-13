<template>
  <div>
    <div v-for="comp in compositions" :key="comp.id" class="q-mb-md">
      <div class="text-subtitle1 text-weight-bold q-mb-xs">
        {{ comp.name || `조성 #${comp.id}` }}
        <q-badge class="q-ml-sm">{{ comp.glassType ?? '미지정' }}</q-badge>
      </div>

      <!-- 산화물 배합비 -->
      <div class="text-caption text-grey q-mb-xs">산화물 배합비</div>
      <div class="row q-gutter-sm q-mb-sm">
        <q-chip v-for="ox in comp.oxides" :key="ox.oxide" dense outline color="primary">
          {{ ox.oxide }} {{ ox.wt }}%
        </q-chip>
        <span v-if="comp.oxides.length === 0" class="text-grey text-caption">없음</span>
      </div>

      <!-- 목표 물성 -->
      <div v-if="comp.propertyTargets.length > 0">
        <div class="text-caption text-grey q-mb-xs">목표 물성</div>
        <q-markup-table flat bordered dense class="q-mb-sm">
          <thead>
            <tr>
              <th class="text-left">물성</th>
              <th>단위</th>
              <th>모드</th>
              <th>목표</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pt in comp.propertyTargets" :key="pt.property">
              <td class="text-left">{{ pt.property }}</td>
              <td class="text-center">{{ pt.unit }}</td>
              <td class="text-center">{{ pt.mode }}</td>
              <td class="text-center">
                <template v-if="pt.mode === '단일값'">{{ pt.target }}</template>
                <template v-else-if="pt.mode === '범위'">{{ pt.min }} ~ {{ pt.max }}</template>
                <template v-else-if="pt.mode === '최솟값'">≥ {{ pt.min }}</template>
                <template v-else-if="pt.mode === '최댓값'">≤ {{ pt.max }}</template>
              </td>
            </tr>
          </tbody>
        </q-markup-table>
      </div>
    </div>

    <div v-if="compositions.length === 0" class="text-grey">조성 데이터 없음</div>
  </div>
</template>

<script setup lang="ts">
import type { CompositionData } from 'src/components/workflow/types'

defineProps<{ compositions: CompositionData[] }>()
</script>
