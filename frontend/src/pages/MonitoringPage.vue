<template>
  <q-page class="lp-page">
    <!-- Page header -->
    <div class="lp-page-head">
      <div>
        <h1 class="lp-page-head__title">장치 모니터링</h1>
        <div v-if="managers.length > 0" class="lp-page-head__sub lp-mono">
          {{ managers[0]?.lab }} · {{ managers[0]?.name }}
        </div>
      </div>
      <div class="lp-page-head__actions">
        <q-btn flat dense no-caps icon="refresh" label="새로고침" class="lp-btn-ghost" @click="fetchManagers" />
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="managers.length === 0" class="lp-empty">
      <q-icon name="dns" size="48px" style="color: var(--t4);" />
      <div class="lp-empty__title">연결된 SiLA 서버가 없습니다</div>
      <div class="lp-empty__sub">서버 설정을 확인하세요</div>
    </div>

    <template v-else>
      <div v-for="manager in managers" :key="manager.id">
        <!-- Error banner -->
        <div v-if="offlineServers(manager).length > 0" class="lp-alert-banner">
          <q-icon name="warning" size="14px" style="color: var(--red); flex-shrink: 0;" />
          <div class="lp-alert-banner__body">
            <div class="lp-alert-banner__title">주의 필요 — {{ offlineServers(manager).length }}개 장치 오프라인</div>
            <div v-for="srv in offlineServers(manager)" :key="srv.id" class="lp-alert-banner__detail lp-mono">
              {{ srv.device }} ({{ srv.address }}) — 연결 끊김
            </div>
          </div>
        </div>

        <!-- Summary strip -->
        <div class="lp-summary-strip">
          <div class="lp-summary-card" v-for="item in summaryItems(manager)" :key="item.label">
            <div class="lp-summary-card__num" :style="{ color: item.color }">{{ item.value }}</div>
            <div class="lp-summary-card__label">{{ item.label }}</div>
          </div>
          <div class="lp-summary-card lp-summary-card--wide">
            <q-icon name="schedule" size="13px" style="color: var(--t3);" />
            <span class="lp-mono" style="font-size: 11px; color: var(--t3);">마지막 업데이트 {{ lastUpdated }}</span>
          </div>
        </div>

        <!-- Device grid -->
        <div class="lp-device-grid">
          <div
            v-for="server in manager.servers"
            :key="server.id"
            class="lp-device-card"
            :class="{
              'lp-device-card--error': !server.online,
              'lp-device-card--running': server.online && server.status === 'Running',
            }"
          >
            <!-- Top bar indicator -->
            <div class="lp-device-card__bar" />

            <div class="lp-device-card__body">
              <!-- Icon + status row -->
              <div class="lp-device-card__top">
                <div
                  class="lp-device-card__icon-wrap"
                  :class="{
                    'lp-device-card__icon-wrap--error':   !server.online,
                    'lp-device-card__icon-wrap--running': server.online && server.status === 'Running',
                  }"
                >
                  <q-icon
                    :name="server.icon || 'devices'"
                    size="16px"
                    :style="{ color: !server.online ? 'var(--red)' : server.status === 'Running' ? 'var(--blue)' : 'var(--t3)' }"
                  />
                </div>
                <div class="lp-device-card__status">
                  <span class="lp-status-chip" :class="statusChipClass(server)">
                    <span v-if="server.status === 'Running'" class="lp-pulse-dot" />
                    {{ statusLabel(server) }}
                  </span>
                </div>
              </div>

              <div class="lp-device-card__name">{{ server.device }}</div>
              <div class="lp-device-card__key lp-mono">{{ server.name }}</div>

              <div class="lp-device-card__divider" />

              <!-- Connection row -->
              <div class="lp-device-card__conn">
                <span
                  class="lp-conn-dot"
                  :style="{ background: server.online ? 'var(--green)' : 'var(--red)', boxShadow: server.online ? '0 0 6px var(--green)' : 'none' }"
                />
                <span :style="{ color: server.online ? 'var(--t1)' : 'var(--red)', fontWeight: server.online ? '400' : '600', fontSize: '12px' }">
                  {{ server.online ? '연결됨' : '연결 끊김' }}
                </span>
              </div>

              <!-- Error detail -->
              <div v-if="!server.online" class="lp-device-card__err lp-mono">
                연결 시간 초과 — 재시도 중
              </div>

              <!-- Address -->
              <div class="lp-device-card__addr lp-mono">{{ server.address }}</div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useSilaDevices } from 'src/composables/useSilaDevices'
import type { SilaServer } from 'src/components/workflow/types'

const { managers, fetchManagers } = useSilaDevices()

const lastUpdated = ref('—')

let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  void fetchManagers()
  lastUpdated.value = new Date().toLocaleTimeString('ko-KR')
  pollTimer = setInterval(() => {
    void fetchManagers()
    lastUpdated.value = new Date().toLocaleTimeString('ko-KR')
  }, 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

function offlineServers(manager: { servers: SilaServer[] }) {
  return manager.servers.filter((s) => !s.online)
}

function summaryItems(manager: { servers: SilaServer[] }) {
  const total = manager.servers.length
  const connected = manager.servers.filter((s) => s.online).length
  const running = manager.servers.filter((s) => s.status === 'Running').length
  const offline = total - connected
  return [
    { label: '전체 장치', value: total,     color: 'var(--t1)' },
    { label: '연결됨',    value: connected, color: 'var(--green)' },
    { label: '실행 중',   value: running,   color: 'var(--blue)' },
    { label: '오프라인',  value: offline,   color: offline > 0 ? 'var(--red)' : 'var(--t3)' },
  ]
}

function statusChipClass(server: SilaServer) {
  if (!server.online) return 'lp-status-chip--red'
  if (server.status === 'Running') return 'lp-status-chip--blue'
  return 'lp-status-chip--green'
}

function statusLabel(server: SilaServer) {
  if (!server.online) return '오프라인'
  if (server.status === 'Running') return '실행 중'
  return '대기'
}
</script>

<style scoped>
.lp-page { padding: 24px; }

/* ── Page head ── */
.lp-page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.lp-page-head__title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--t1);
  margin: 0 0 3px;
}

.lp-page-head__sub {
  font-size: 11px;
  color: var(--t3);
}

.lp-page-head__actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.lp-btn-ghost {
  color: var(--t2) !important;
  border: 1px solid var(--bd) !important;
  border-radius: var(--r1) !important;
  font-size: 12px;
}

/* ── Empty ── */
.lp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 8px;
}

.lp-empty__title {
  font-size: 15px;
  color: var(--t2);
  font-weight: 500;
}

.lp-empty__sub {
  font-size: 12px;
  color: var(--t3);
}

/* ── Alert banner ── */
.lp-alert-banner {
  background: var(--red-bg);
  border: 1px solid var(--red-bd);
  border-radius: var(--r1);
  padding: 10px 14px;
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.lp-alert-banner__body {
  flex: 1;
}

.lp-alert-banner__title {
  font-size: 12px;
  font-weight: 600;
  color: var(--red);
  margin-bottom: 3px;
}

.lp-alert-banner__detail {
  font-size: 11px;
  color: var(--t2);
}

/* ── Summary strip ── */
.lp-summary-strip {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.lp-summary-card {
  flex: 1;
  background: var(--s1);
  border: 1px solid var(--bd);
  border-radius: var(--r1);
  padding: 10px 14px;
  display: flex;
  gap: 10px;
  align-items: center;
  min-width: 100px;
}

.lp-summary-card--wide {
  flex: 2;
  gap: 6px;
}

.lp-summary-card__num {
  font-family: var(--mono);
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}

.lp-summary-card__label {
  font-size: 11px;
  color: var(--t3);
}

/* ── Device grid ── */
.lp-device-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

@media (max-width: 1200px) {
  .lp-device-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ── Device card ── */
.lp-device-card {
  background: var(--s1);
  border: 1px solid var(--bd);
  border-radius: var(--r2);
  overflow: hidden;
  box-shadow: var(--shadow);
  position: relative;
}

.lp-device-card--error {
  border-color: var(--red-bd);
  box-shadow: 0 0 0 1px var(--red-bg);
}

.lp-device-card--running {
  border-color: var(--accent-bd);
  box-shadow: 0 0 0 1px var(--accent-bg);
}

.lp-device-card__bar {
  height: 2px;
  background: var(--bd);
}

.lp-device-card--error .lp-device-card__bar {
  background: var(--red);
  opacity: 0.7;
}

.lp-device-card--running .lp-device-card__bar {
  background: var(--blue);
  opacity: 0.7;
}

.lp-device-card__body {
  padding: 16px;
}

.lp-device-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 14px;
}

.lp-device-card__icon-wrap {
  width: 34px;
  height: 34px;
  border-radius: 7px;
  background: var(--s3);
  border: 1px solid var(--bd);
  display: flex;
  align-items: center;
  justify-content: center;
}

.lp-device-card__icon-wrap--error {
  background: var(--red-bg);
  border-color: var(--red-bd);
}

.lp-device-card__icon-wrap--running {
  background: var(--blue-bg);
  border-color: var(--blue-bd);
}

.lp-device-card__name {
  font-weight: 600;
  font-size: 13px;
  color: var(--t1);
  margin-bottom: 2px;
}

.lp-device-card__key {
  font-size: 10px;
  color: var(--t3);
  margin-bottom: 12px;
}

.lp-device-card__divider {
  height: 1px;
  background: var(--bd);
  margin-bottom: 10px;
}

.lp-device-card__conn {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 6px;
}

.lp-conn-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  display: inline-block;
}

.lp-device-card__err {
  background: var(--red-bg);
  border: 1px solid var(--red-bd);
  border-radius: 3px;
  padding: 5px 8px;
  font-size: 10px;
  color: var(--red);
  line-height: 1.5;
  margin-bottom: 6px;
  word-break: break-all;
}

.lp-device-card__addr {
  font-size: 10px;
  color: var(--t3);
  margin-top: 8px;
}

.lp-device-card__status {
  display: flex;
}

/* ── Pulse dot ── */
.lp-pulse-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
  animation: lp-pulse 1.4s ease infinite;
}

/* ── Mono ── */
.lp-mono {
  font-family: var(--mono) !important;
}
</style>
