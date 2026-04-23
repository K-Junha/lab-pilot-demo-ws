<template>
  <div>
    <div class="row items-center q-mb-md">
      <DeviceSelector v-model="data.deviceId" />
    </div>
    <div class="row q-col-gutter-md">
    <div class="col-3"><q-input outlined v-model.number="data.temp" type="number" label="서냉 온도 (°C)" /></div>
    <div class="col-3"><q-input outlined v-model.number="data.duration" type="number" label="시간 (min)" /></div>
    <div class="col-3">
      <q-select outlined v-model="data.method" :options="['자연 냉각', '제어 냉각', '급냉']" label="방식" emit-value map-options />
    </div>
    <div class="col-12"><q-input outlined v-model="data.memo" label="메모" type="textarea" rows="2" /></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HeatTreatData } from '../types'
import DeviceSelector from '../DeviceSelector.vue'

const data = defineModel<HeatTreatData>('data', { required: true })
</script>
