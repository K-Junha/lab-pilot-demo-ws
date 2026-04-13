<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">SiLA Server Monitoring</div>

    <div v-for="manager in managers" :key="manager.id" class="q-mb-lg">
      <!-- Manager Header -->
      <q-card class="q-mb-sm">
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="dns" size="sm" color="primary" />
          <div class="text-h6 text-weight-bold">{{ manager.lab }}</div>
          <q-badge :color="manager.online ? 'green' : 'red'" class="q-ml-sm">
            {{ manager.online ? 'Online' : 'Offline' }}
          </q-badge>
          <q-space />
          <div class="text-caption text-grey">{{ manager.name }}</div>
        </q-card-section>
      </q-card>

      <!-- Server Cards -->
      <div class="row q-col-gutter-md">
        <div
          v-for="server in manager.servers"
          :key="server.id"
          class="col-12 col-sm-6 col-md-3"
        >
          <q-card bordered>
            <q-card-section>
              <div class="row items-center q-gutter-sm">
                <q-icon :name="server.icon" size="sm" :color="server.online ? 'primary' : 'grey'" />
                <div class="text-subtitle1 text-weight-bold">{{ server.device }}</div>
              </div>
              <div class="text-caption text-grey q-mt-xs">{{ server.name }}</div>
            </q-card-section>

            <q-separator />

            <q-card-section class="q-py-sm">
              <div class="row items-center q-gutter-xs">
                <q-icon
                  name="circle"
                  size="10px"
                  :color="server.online ? 'green' : 'red'"
                />
                <span class="text-body2">{{ server.online ? 'Connected' : 'Disconnected' }}</span>
              </div>
              <div class="text-caption text-grey q-mt-xs">{{ server.address }}</div>
            </q-card-section>

            <q-separator />

            <q-card-section class="q-py-sm">
              <div class="row justify-between text-caption">
                <span>Status</span>
                <q-badge
                  :color="statusColor(server.status)"
                  :label="server.status"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { useSilaDevices } from 'src/composables/useSilaDevices'

const { managers } = useSilaDevices()

function statusColor(status: string): string {
  switch (status) {
    case 'Idle': return 'blue-grey'
    case 'Running': return 'green'
    case 'Error': return 'red'
    case 'Offline': return 'grey'
    default: return 'grey'
  }
}
</script>