<template>
  <div>
    <div class="row items-center q-mb-md">
      <DeviceSelector v-model="data.deviceId" />
    </div>
    <div class="text-subtitle2 q-mb-sm">다단계 온도 프로파일</div>
    <div v-for="(seg, si) in data.segments" :key="si" class="row q-col-gutter-sm q-mb-xs items-center">
      <div class="col"><q-badge>{{ Number(si) + 1 }}단계</q-badge></div>
      <div class="col-3"><q-input dense outlined v-model.number="seg.rampRate" type="number" label="승온속도 (°C/min)" /></div>
      <div class="col-2"><q-input dense outlined v-model.number="seg.temp" type="number" label="온도 (°C)" /></div>
      <div class="col-3"><q-input dense outlined v-model.number="seg.holdMin" type="number" label="유지시간 (min)" /></div>
      <div class="col-1">
        <q-btn flat dense round icon="close" color="red" size="sm" @click="data.segments.splice(si, 1)" />
      </div>
    </div>
    <q-btn flat dense icon="add" label="단계 추가" color="primary" class="q-mt-sm" @click="data.segments.push({ rampRate: null, temp: null, holdMin: null })" />
  </div>
</template>

<script setup lang="ts">
import DeviceSelector from '../DeviceSelector.vue'

defineProps<{ data: any }>()
</script>
