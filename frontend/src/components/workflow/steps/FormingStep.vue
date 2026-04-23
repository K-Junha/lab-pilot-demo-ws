<template>
  <div>
    <div class="row items-center q-mb-md">
      <DeviceSelector v-model="data.deviceId" />
    </div>
    <div class="row q-col-gutter-md items-center">
    <div class="col-3">
      <q-select outlined v-model="data.shape" :options="['원형', '바형']" label="타입" emit-value map-options />
    </div>
    <template v-if="data.shape === '원형'">
      <div class="col-3"><q-input outlined v-model.number="data.R" type="number" label="R (mm)" /></div>
      <div class="col-3"><q-input outlined v-model.number="data.T" type="number" label="T (mm)" /></div>
    </template>
    <template v-else>
      <div class="col-2"><q-input outlined v-model.number="data.W" type="number" label="W (mm)" /></div>
      <div class="col-2"><q-input outlined v-model.number="data.H" type="number" label="H (mm)" /></div>
      <div class="col-2"><q-input outlined v-model.number="data.T" type="number" label="T (mm)" /></div>
    </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FormingData } from '../types'
import DeviceSelector from '../DeviceSelector.vue'

const data = defineModel<FormingData>('data', { required: true })
</script>
