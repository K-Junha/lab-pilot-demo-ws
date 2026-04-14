<template>
  <q-select
    outlined
    dense
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :options="allDevices"
    option-value="serverId"
    option-label="device"
    emit-value
    map-options
    label="SiLA 장비 선택"
    clearable
    style="min-width: 300px;"
  >
    <template #option="{ opt, itemProps }">
      <q-item v-bind="itemProps">
        <q-item-section avatar>
          <q-icon :name="opt.icon" :color="opt.online ? 'primary' : 'grey'" />
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ opt.device }}</q-item-label>
          <q-item-label caption>
            {{ opt.managerLab }} · {{ opt.address }}
          </q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-badge :color="opt.online ? 'green' : 'red'" :label="opt.online ? 'Online' : 'Offline'" />
        </q-item-section>
      </q-item>
    </template>
    <template #selected-item="{ opt }">
      <div v-if="opt" class="row items-center q-gutter-xs">
        <q-icon :name="opt.icon" size="xs" :color="opt.online ? 'primary' : 'grey'" />
        <span>{{ opt.device }}</span>
        <span class="text-caption text-grey">({{ opt.managerLab }} · {{ opt.address }})</span>
      </div>
    </template>
  </q-select>
</template>

<script setup lang="ts">
import { useSilaDevices } from 'src/composables/useSilaDevices'

defineProps<{ modelValue: string | null }>()
defineEmits<{ 'update:modelValue': [value: string | null] }>()

const { allDevices } = useSilaDevices()
</script>
