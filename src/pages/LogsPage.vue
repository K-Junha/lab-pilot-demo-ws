<template>
  <q-page padding class="column" style="height: calc(100vh - 50px);">
    <!-- Toolbar -->
    <div class="row items-center q-gutter-sm q-mb-sm">
      <div class="text-h5">Logs</div>
      <q-space />
      <q-select
        v-model="levelFilter"
        :options="levelOptions"
        label="Level"
        outlined
        dense
        clearable
        style="min-width: 130px;"
      />
      <q-input
        v-model="keyword"
        label="검색"
        outlined
        dense
        clearable
        style="min-width: 200px;"
      >
        <template v-slot:prepend><q-icon name="search" /></template>
      </q-input>
      <q-toggle v-model="autoScroll" label="Auto-scroll" dense />
      <q-btn flat dense icon="delete_sweep" color="red" @click="clearLogs" />
    </div>

    <!-- Terminal -->
    <div
      ref="termRef"
      class="col terminal-box"
      @scroll="onScroll"
    >
      <div
        v-for="log in filteredLogs"
        :key="log.id"
        class="log-line"
      >
        <span class="log-ts">{{ log.ts }}</span>
        <span :class="'log-level log-level--' + log.level">{{ padLevel(log.level) }}</span>
        <span class="log-src">{{ log.source }}</span>
        <span class="log-msg">{{ log.message }}</span>
      </div>
      <div v-if="filteredLogs.length === 0" class="log-empty">No logs</div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

type LogLevel = 'INFO' | 'WARN' | 'ERROR' | 'DEBUG'

interface LogEntry {
  id: number
  ts: string
  level: LogLevel
  source: string
  message: string
}

const levelOptions: LogLevel[] = ['DEBUG', 'INFO', 'WARN', 'ERROR']

const levelFilter = ref<LogLevel | null>(null)
const keyword = ref('')
const autoScroll = ref(true)
const termRef = ref<HTMLElement | null>(null)

let idSeq = 0
const logs = ref<LogEntry[]>([])

const filteredLogs = computed(() => {
  let result = logs.value
  if (levelFilter.value) {
    result = result.filter((l) => l.level === levelFilter.value)
  }
  if (keyword.value) {
    const kw = keyword.value.toLowerCase()
    result = result.filter(
      (l) =>
        l.message.toLowerCase().includes(kw) ||
        l.source.toLowerCase().includes(kw),
    )
  }
  return result
})

function padLevel(level: string) {
  return level.padEnd(5, ' ')
}

function now() {
  return new Date().toISOString().replace('T', ' ').substring(0, 23)
}

function addLog(level: LogLevel, source: string, message: string) {
  logs.value.push({ id: ++idSeq, ts: now(), level, source, message })
}

function clearLogs() {
  logs.value = []
}

function scrollToBottom() {
  if (!autoScroll.value || !termRef.value) return
  nextTick(() => {
    if (termRef.value) {
      termRef.value.scrollTop = termRef.value.scrollHeight
    }
  })
}

function onScroll() {
  if (!termRef.value) return
  const el = termRef.value
  const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40
  autoScroll.value = atBottom
}

watch(
  () => logs.value.length,
  () => scrollToBottom(),
)

/* -- Mock: 데모용 로그 생성 -- */
const mockSources = ['SiLA-Manager-1', 'SiLA-Server-1', 'SiLA-Server-2', 'SiLA-Manager-2', 'SiLA-Server-3', 'SiLA-Server-4', 'System']
const mockMessages: Record<LogLevel, string[]> = {
  INFO:  ['Server connected', 'Command executed successfully', 'Temperature reached target', 'Weighing complete', 'Workflow step finished'],
  WARN:  ['Temperature deviation detected', 'Response timeout, retrying...', 'Disk usage above 80%', 'Calibration due soon'],
  ERROR: ['Connection lost to device', 'Command failed: TIMEOUT', 'Sensor reading out of range', 'Emergency stop triggered'],
  DEBUG: ['Heartbeat sent', 'Polling sensors...', 'Buffer flushed', 'gRPC channel opened', 'Received ACK'],
}

let mockTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // Seed some initial logs
  addLog('INFO', 'System', 'Log system initialized')
  addLog('INFO', 'SiLA-Manager-1', 'Connected to SiLA Server Manager 1')
  addLog('INFO', 'SiLA-Manager-2', 'Connected to SiLA Server Manager 2')
  addLog('DEBUG', 'SiLA-Server-1', 'Heartbeat sent')
  addLog('WARN', 'SiLA-Server-4', 'Response timeout, retrying...')
  addLog('ERROR', 'SiLA-Server-4', 'Connection lost to device')
  addLog('INFO', 'SiLA-Server-2', 'Temperature reached target')

  // Auto-generate mock logs
  mockTimer = setInterval(() => {
    const levels: LogLevel[] = ['DEBUG', 'DEBUG', 'INFO', 'INFO', 'INFO', 'WARN', 'ERROR']
    const level = levels[Math.floor(Math.random() * levels.length)] ?? 'INFO'
    const source = mockSources[Math.floor(Math.random() * mockSources.length)] ?? 'System'
    const msgs = mockMessages[level]
    const msg = msgs[Math.floor(Math.random() * msgs.length)] ?? ''
    addLog(level, source, msg)
  }, 2000)
})

onUnmounted(() => {
  if (mockTimer) clearInterval(mockTimer)
})
</script>

<style scoped>
.terminal-box {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  padding: 12px 16px;
  border-radius: 6px;
  overflow-y: auto;
  overflow-x: hidden;
}

.log-line {
  white-space: pre-wrap;
  word-break: break-all;
}

.log-ts {
  color: #6a9955;
  margin-right: 8px;
}

.log-level {
  font-weight: bold;
  margin-right: 8px;
  display: inline-block;
  width: 50px;
}

.log-level--INFO  { color: #4ec9b0; }
.log-level--WARN  { color: #dcdcaa; }
.log-level--ERROR { color: #f44747; }
.log-level--DEBUG { color: #808080; }

.log-src {
  color: #569cd6;
  margin-right: 8px;
}

.log-msg {
  color: #d4d4d4;
}

.log-empty {
  color: #555;
  text-align: center;
  padding: 40px;
}
</style>