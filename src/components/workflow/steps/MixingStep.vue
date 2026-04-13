<template>
  <div>
    <div class="row items-center q-mb-md">
      <DeviceSelector v-model="data.deviceId" />
    </div>
    <div class="row q-col-gutter-md">
    <div class="col-4">
      <q-input outlined v-model.number="data.duration" type="number" label="믹싱 시간 (min)" />
    </div>
    <div class="col-8">
      <q-input outlined v-model="data.memo" label="메모" type="textarea" rows="2" />
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DeviceSelector from '../DeviceSelector.vue'

defineProps<{ data: any }>()
</script>
