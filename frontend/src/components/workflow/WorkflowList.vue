<template>
  <div class="lp-wf-list">
    <!-- Header -->
    <div class="lp-wf-list__head">
      <div class="lp-wf-list__title">워크플로우 목록</div>
      <q-btn unelevated no-caps icon="add" label="새 워크플로우" class="lp-btn-primary" @click="emit('create')" />
    </div>

    <!-- Empty state -->
    <div v-if="workflows.length === 0" class="lp-wf-list__empty">
      <q-icon name="account_tree" size="48px" style="color: var(--t4);" />
      <div class="lp-wf-list__empty-title">아직 워크플로우가 없습니다</div>
      <div class="lp-wf-list__empty-sub">'새 워크플로우' 버튼을 눌러 시작하세요</div>
    </div>

    <!-- Grouped list -->
    <template v-else>
      <div v-for="group in groups" :key="group.status" class="lp-wf-group">
        <!-- Group header -->
        <div v-if="group.items.length > 0" class="lp-wf-group__head">
          <span class="lp-wf-group__dot" :style="{ background: group.color, boxShadow: `0 0 6px ${group.color}80` }" />
          <span class="lp-wf-group__label lp-mono">{{ group.label }}</span>
          <span class="lp-wf-group__count lp-mono">({{ group.items.length }})</span>
          <div class="lp-wf-group__line" />
        </div>

        <!-- Workflow rows -->
        <div class="lp-wf-rows">
          <div
            v-for="(wf, idx) in group.items"
            :key="wf.id"
            class="lp-wf-row"
            :style="{ borderLeftColor: group.color }"
            @click="onRowClick(wf.id)"
          >
            <!-- Name + desc -->
            <div class="lp-wf-row__info">
              <div class="lp-wf-row__name">{{ wf.name || `워크플로우 #${wf.id}` }}</div>
              <div class="lp-wf-row__desc">
                {{ wf.compositions.length }}개 조성 · {{ wf.steps.length }}개 스텝
              </div>
            </div>

            <!-- Step dots -->
            <div class="lp-wf-row__dots">
              <span
                v-for="step in wf.steps"
                :key="step.uid"
                class="lp-wf-row__dot"
                :style="{ background: group.status !== '계획중' ? group.color : 'var(--bd)' }"
              />
              <span class="lp-wf-row__steps lp-mono">{{ wf.steps.length }}스텝</span>
            </div>

            <!-- Date -->
            <span class="lp-wf-row__date lp-mono">{{ fmtDate(wf.createdAt) }}</span>

            <!-- Status chip -->
            <span class="lp-status-chip" :class="statusChipClass(wf.status)">
              <span v-if="wf.status === '진행중'" class="lp-pulse-dot" />
              {{ wf.status }}
            </span>

            <!-- Actions -->
            <div class="lp-wf-row__actions" @click.stop>
              <q-btn
                v-if="wf.status === '계획중'"
                flat dense no-caps size="sm"
                icon="play_arrow" label="시작"
                class="lp-wf-action-btn lp-wf-action-btn--start"
                @click="emit('start', globalIndex(wf.id))"
              />
              <q-btn
                flat dense no-caps size="sm" icon="edit"
                class="lp-wf-action-btn"
                @click="emit('select', globalIndex(wf.id))"
              />
              <q-btn
                flat dense no-caps size="sm" icon="content_copy"
                class="lp-wf-action-btn"
                @click="emit('copy', globalIndex(wf.id))"
              />
              <q-btn
                flat dense no-caps size="sm" icon="delete"
                class="lp-wf-action-btn lp-wf-action-btn--danger"
                @click="emit('delete', globalIndex(wf.id))"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Workflow } from './types'

const props = defineProps<{ workflows: Workflow[] }>()

const emit = defineEmits<{
  create: []
  select: [index: number]
  start:  [index: number]
  copy:   [index: number]
  delete: [index: number]
}>()

const STATUS_GROUPS = [
  { status: '진행중', label: '진행 중', color: 'var(--blue)' },
  { status: '계획중', label: '계획 중', color: 'var(--orange)' },
  { status: '완료',   label: '완료',   color: 'var(--green)' },
]

const KNOWN_STATUSES = new Set(STATUS_GROUPS.map((g) => g.status))

const groups = computed(() =>
  STATUS_GROUPS.map((g) => ({
    ...g,
    items: props.workflows.filter((w) => {
      if (g.status === '계획중') return w.status === '계획중' || !KNOWN_STATUSES.has(w.status)
      return w.status === g.status
    }),
  }))
)

function globalIndex(id: number): number {
  return props.workflows.findIndex((w) => w.id === id)
}

function onRowClick(id: number) {
  emit('select', globalIndex(id))
}

function fmtDate(v: string): string {
  if (!v) return '-'
  const d = new Date(v)
  return isNaN(d.getTime()) ? v : d.toLocaleDateString('ko-KR')
}

function statusChipClass(status: string) {
  switch (status) {
    case '완료':   return 'lp-status-chip--green'
    case '진행중': return 'lp-status-chip--blue'
    case '계획중':
    default:       return 'lp-status-chip--orange'
  }
}
</script>

<style scoped>
.lp-wf-list {
  padding: 0;
}

/* ── Header ── */
.lp-wf-list__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.lp-wf-list__title {
  font-size: 17px;
  font-weight: 600;
  color: var(--t1);
  letter-spacing: -0.01em;
}

.lp-btn-primary {
  background: var(--accent) !important;
  color: white !important;
  font-size: 12px;
  border-radius: var(--r1) !important;
  padding: 6px 14px !important;
}

/* ── Empty ── */
.lp-wf-list__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 8px;
}

.lp-wf-list__empty-title {
  font-size: 15px;
  color: var(--t2);
  font-weight: 500;
}

.lp-wf-list__empty-sub {
  font-size: 12px;
  color: var(--t3);
}

/* ── Group ── */
.lp-wf-group {
  margin-bottom: 24px;
}

.lp-wf-group__head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.lp-wf-group__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  display: inline-block;
}

.lp-wf-group__label {
  font-size: 11px;
  font-weight: 600;
  color: var(--t2);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.lp-wf-group__count {
  font-size: 10px;
  color: var(--t3);
}

.lp-wf-group__line {
  flex: 1;
  height: 1px;
  background: var(--bd);
}

/* ── Rows ── */
.lp-wf-rows {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lp-wf-row {
  background: var(--s1);
  border: 1px solid var(--bd);
  border-radius: var(--r1);
  border-left-width: 2px;
  display: flex;
  align-items: center;
  padding: 10px 14px;
  gap: 14px;
  cursor: pointer;
  transition: background 0.12s;
}

.lp-wf-row:hover {
  background: var(--s2);
}

.lp-wf-row__info {
  flex: 1;
  min-width: 0;
}

.lp-wf-row__name {
  font-size: 13px;
  font-weight: 500;
  color: var(--t1);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lp-wf-row__desc {
  font-size: 11px;
  color: var(--t3);
}

.lp-wf-row__dots {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
}

.lp-wf-row__dot {
  width: 5px;
  height: 5px;
  border-radius: 1px;
  display: inline-block;
}

.lp-wf-row__steps {
  font-size: 10px;
  color: var(--t3);
  margin-left: 4px;
}

.lp-wf-row__date {
  font-size: 10px;
  color: var(--t3);
  min-width: 90px;
  text-align: right;
  flex-shrink: 0;
}

.lp-wf-row__actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.lp-wf-action-btn {
  color: var(--t3) !important;
  border-radius: var(--r1) !important;
  font-size: 12px !important;
  padding: 2px 6px !important;
}

.lp-wf-action-btn:hover {
  background: var(--s3) !important;
  color: var(--t1) !important;
}

.lp-wf-action-btn--start {
  color: var(--green) !important;
  background: var(--green-bg) !important;
  border: 1px solid var(--green-bd) !important;
}

.lp-wf-action-btn--danger {
  color: var(--red) !important;
}

.lp-wf-action-btn--danger:hover {
  background: var(--red-bg) !important;
  color: var(--red) !important;
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
