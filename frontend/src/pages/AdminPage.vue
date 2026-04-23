<template>
  <q-page class="lp-page">
    <!-- Page header -->
    <div class="lp-page-head">
      <h1 class="lp-page-head__title">관리자</h1>
    </div>

    <!-- Tabs -->
    <div class="lp-tabs">
      <button
        class="lp-tab"
        :class="{ 'lp-tab--active': tab === 'devices' }"
        @click="tab = 'devices'"
      >장치 관리</button>
      <button
        class="lp-tab"
        :class="{ 'lp-tab--active': tab === 'users' }"
        @click="tab = 'users'"
      >사용자 관리</button>
    </div>

    <!-- ── 장치 관리 ── -->
    <div v-show="tab === 'devices'">
      <div class="lp-section-label">ss_manager 목록</div>

      <div v-if="managersLoading" class="lp-loading">
        <q-spinner size="24px" style="color: var(--accent);" />
      </div>

      <table v-else class="lp-table lp-table--mb">
        <thead>
          <tr>
            <th>ID</th>
            <th>이름</th>
            <th>호스트</th>
            <th>WS 포트</th>
            <th>상태</th>
            <th>마지막 연결</th>
            <th>관리</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="managers.length === 0">
            <td colspan="7" class="lp-table__empty">등록된 ss_manager가 없습니다</td>
          </tr>
          <tr v-for="row in managers" :key="row.id" class="lp-table__row">
            <td class="lp-mono lp-text-t3">{{ row.id }}</td>
            <td class="lp-table__name">{{ row.name }}</td>
            <td class="lp-mono lp-text-t2">{{ row.host }}</td>
            <td class="lp-mono lp-text-t3">{{ row.ws_port }}</td>
            <td>
              <span class="lp-status-chip" :class="row.online ? 'lp-status-chip--green' : 'lp-status-chip--grey'">
                <span v-if="row.online" class="lp-conn-dot lp-conn-dot--online" />
                {{ row.online ? '온라인' : '오프라인' }}
              </span>
            </td>
            <td class="lp-mono lp-text-t3">{{ row.last_seen ? new Date(row.last_seen).toLocaleString('ko-KR') : '-' }}</td>
            <td>
              <q-btn
                flat dense no-caps size="sm"
                icon="delete"
                class="lp-action-btn lp-action-btn--danger"
                @click="deleteManager(row)"
              />
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Register form -->
      <div class="lp-section-label">새 ss_manager 등록</div>
      <div class="lp-form-row">
        <q-input v-model="form.name" label="이름" outlined dense class="lp-input lp-input--flex" />
        <q-input v-model="form.host" label="호스트 (IP)" outlined dense class="lp-input lp-input--flex" />
        <q-input v-model.number="form.ws_port" label="WS 포트" type="number" outlined dense class="lp-input lp-input--sm" />
        <q-input v-model="form.api_key" label="API Key" outlined dense class="lp-input lp-input--flex" />
        <q-btn
          unelevated no-caps
          label="등록"
          class="lp-btn-primary"
          :loading="registering"
          @click="registerManager"
        />
      </div>
    </div>

    <!-- ── 사용자 관리 ── -->
    <div v-show="tab === 'users'">
      <div class="lp-section-label">사용자 목록</div>

      <div v-if="usersLoading" class="lp-loading">
        <q-spinner size="24px" style="color: var(--accent);" />
      </div>

      <table v-else class="lp-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>사용자명</th>
            <th>이메일</th>
            <th>Role</th>
            <th>가입일</th>
            <th>관리</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="users.length === 0">
            <td colspan="6" class="lp-table__empty">사용자가 없습니다</td>
          </tr>
          <tr v-for="user in users" :key="user.user_id" class="lp-table__row">
            <td class="lp-mono lp-text-t3">{{ user.user_id }}</td>
            <td class="lp-table__name">{{ user.username }}</td>
            <td class="lp-mono lp-text-t2">{{ user.email || '-' }}</td>
            <td>
              <span class="lp-role-chip" :class="user.role === 'admin' ? 'lp-role-chip--admin' : 'lp-role-chip--user'">
                {{ user.role === 'admin' ? '관리자' : '연구원' }}
              </span>
            </td>
            <td class="lp-mono lp-text-t3">{{ new Date(user.created_at).toLocaleDateString('ko-KR') }}</td>
            <td>
              <div class="lp-action-row" @click.stop>
                <q-btn
                  flat dense no-caps size="sm"
                  :label="user.role === 'admin' ? '→ user' : '→ admin'"
                  class="lp-action-btn"
                  :class="user.role === 'admin' ? 'lp-action-btn--orange' : 'lp-action-btn--purple'"
                  :disable="user.user_id === authStore.user?.user_id"
                  @click="changeRole(user)"
                />
                <q-btn
                  flat dense no-caps size="sm"
                  icon="delete"
                  class="lp-action-btn lp-action-btn--danger"
                  :disable="user.user_id === authStore.user?.user_id"
                  @click="deleteUser(user)"
                />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import { API_BASE } from 'src/config'

/* ── 공통 ── */
const $q = useQuasar()
const authStore = useAuthStore()
const tab = ref<'devices' | 'users'>('devices')

function authHeader(): Record<string, string> {
  return { Authorization: `Bearer ${authStore.token ?? ''}`, 'Content-Type': 'application/json' }
}

/* ── 장치 관리 ── */
interface ManagerRow {
  id: number
  name: string
  host: string
  ws_port: number
  online: boolean
  last_seen: string | null
}

interface ManagerForm {
  name: string
  host: string
  ws_port: number
  api_key: string
}

const managers = ref<ManagerRow[]>([])
const managersLoading = ref(false)
const registering = ref(false)
const form = ref<ManagerForm>({ name: '', host: '', ws_port: 8765, api_key: '' })

async function loadManagers() {
  managersLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/managers`, { headers: authHeader() })
    if (!res.ok) throw new Error()
    managers.value = (await res.json()) as ManagerRow[]
  } finally {
    managersLoading.value = false
  }
}

async function registerManager() {
  if (!form.value.name || !form.value.host) {
    $q.notify({ type: 'warning', message: '이름과 호스트를 입력해주세요.' })
    return
  }
  registering.value = true
  try {
    const res = await fetch(`${API_BASE}/admin/managers`, {
      method: 'POST',
      headers: authHeader(),
      body: JSON.stringify(form.value),
    })
    if (!res.ok) throw new Error()
    await loadManagers()
    form.value = { name: '', host: '', ws_port: 8765, api_key: '' }
    $q.notify({ type: 'positive', message: 'ss_manager가 등록되었습니다.' })
  } catch {
    $q.notify({ type: 'negative', message: '등록 실패' })
  } finally {
    registering.value = false
  }
}

async function _execDeleteManager(row: ManagerRow) {
  try {
    const res = await fetch(`${API_BASE}/admin/managers/${row.id}`, {
      method: 'DELETE',
      headers: authHeader(),
    })
    if (!res.ok) throw new Error()
    await loadManagers()
    $q.notify({ type: 'positive', message: '삭제되었습니다.' })
  } catch {
    $q.notify({ type: 'negative', message: '삭제 실패' })
  }
}

function deleteManager(row: ManagerRow) {
  $q.dialog({
    title: 'ss_manager 삭제',
    message: `'${row.name}'을(를) 삭제하시겠습니까?`,
    cancel: { flat: true, label: '취소' },
    ok: { color: 'negative', label: '삭제' },
  }).onOk(() => void _execDeleteManager(row))
}

/* ── 사용자 관리 ── */
interface UserRow {
  user_id: number
  username: string
  email: string | null
  role: string
  created_at: string
}

const users = ref<UserRow[]>([])
const usersLoading = ref(false)

async function loadUsers() {
  usersLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/admin/users`, { headers: authHeader() })
    if (!res.ok) throw new Error()
    users.value = (await res.json()) as UserRow[]
  } finally {
    usersLoading.value = false
  }
}

async function changeRole(user: UserRow) {
  const newRole = user.role === 'admin' ? 'user' : 'admin'
  try {
    const res = await fetch(`${API_BASE}/admin/users/${user.user_id}/role?role=${newRole}`, {
      method: 'PATCH',
      headers: authHeader(),
    })
    if (!res.ok) throw new Error()
    await loadUsers()
    $q.notify({ type: 'positive', message: `${user.username} → ${newRole}` })
  } catch {
    $q.notify({ type: 'negative', message: 'role 변경 실패' })
  }
}

async function _execDeleteUser(user: UserRow) {
  try {
    const res = await fetch(`${API_BASE}/admin/users/${user.user_id}`, {
      method: 'DELETE',
      headers: authHeader(),
    })
    if (!res.ok) throw new Error()
    await loadUsers()
    $q.notify({ type: 'positive', message: '계정이 삭제되었습니다.' })
  } catch {
    $q.notify({ type: 'negative', message: '삭제 실패' })
  }
}

function deleteUser(user: UserRow) {
  $q.dialog({
    title: '계정 삭제',
    message: `'${user.username}' 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`,
    cancel: { flat: true, label: '취소' },
    ok: { color: 'negative', label: '삭제' },
  }).onOk(() => void _execDeleteUser(user))
}

onMounted(() => {
  void loadManagers()
  void loadUsers()
})
</script>

<style scoped>
.lp-page { padding: 24px; }

/* ── Page head ── */
.lp-page-head {
  margin-bottom: 20px;
}

.lp-page-head__title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--t1);
  margin: 0;
}

/* ── Tabs ── */
.lp-tabs {
  display: flex;
  border-bottom: 1px solid var(--bd);
  margin-bottom: 24px;
}

.lp-tab {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 8px 16px;
  font-size: 13px;
  color: var(--t3);
  cursor: pointer;
  font-family: var(--sans);
  transition: color 0.15s, border-color 0.15s;
  margin-bottom: -1px;
}

.lp-tab:hover {
  color: var(--t1);
}

.lp-tab--active {
  color: var(--t1);
  border-bottom-color: var(--accent);
  font-weight: 600;
}

/* ── Section label ── */
.lp-section-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--t2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

/* ── Loading ── */
.lp-loading {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

/* ── Table ── */
.lp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-bottom: 32px;
}

.lp-table--mb {
  margin-bottom: 28px;
}

.lp-table th {
  background: var(--s2);
  color: var(--t3);
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid var(--bd);
  white-space: nowrap;
}

.lp-table__row {
  border-bottom: 1px solid var(--bd);
  transition: background 0.1s;
}

.lp-table__row:hover {
  background: var(--s2);
}

.lp-table td {
  padding: 9px 12px;
  color: var(--t1);
  vertical-align: middle;
}

.lp-table__name {
  font-weight: 500;
}

.lp-table__empty {
  text-align: center;
  color: var(--t3);
  padding: 32px 12px;
  font-size: 13px;
}

/* ── Form row ── */
.lp-form-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.lp-input :deep(.q-field__control) {
  background: var(--s2) !important;
  border-color: var(--bd) !important;
}

.lp-input :deep(.q-field__native),
.lp-input :deep(.q-field__input) {
  color: var(--t1) !important;
}

.lp-input :deep(.q-field__label) {
  color: var(--t3) !important;
}

.lp-input--flex {
  flex: 1;
  min-width: 120px;
}

.lp-input--sm {
  width: 110px;
  flex-shrink: 0;
}

/* ── Buttons ── */
.lp-btn-primary {
  background: var(--accent) !important;
  color: white !important;
  font-size: 12px;
  border-radius: var(--r1) !important;
  padding: 6px 16px !important;
  flex-shrink: 0;
}

/* ── Action row ── */
.lp-action-row {
  display: flex;
  gap: 4px;
  align-items: center;
}

.lp-action-btn {
  color: var(--t3) !important;
  border-radius: var(--r1) !important;
  font-size: 11px !important;
  padding: 2px 7px !important;
}

.lp-action-btn:hover {
  background: var(--s3) !important;
  color: var(--t1) !important;
}

.lp-action-btn--danger {
  color: var(--red) !important;
}

.lp-action-btn--danger:hover {
  background: var(--red-bg) !important;
}

.lp-action-btn--orange {
  color: var(--orange) !important;
  background: var(--orange-bg) !important;
  border: 1px solid var(--orange-bd) !important;
}

.lp-action-btn--purple {
  color: var(--accent) !important;
  background: var(--accent-bg) !important;
  border: 1px solid var(--accent-bd) !important;
}

/* ── Role chip ── */
.lp-role-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
  font-family: var(--mono);
}

.lp-role-chip--admin {
  background: rgba(139, 92, 246, 0.12);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.25);
}

.lp-role-chip--user {
  background: var(--accent-bg);
  color: var(--accent);
  border: 1px solid var(--accent-bd);
}

/* ── Connection dot ── */
.lp-conn-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
  display: inline-block;
}

.lp-conn-dot--online {
  animation: lp-pulse 1.4s ease infinite;
}

/* ── Text utilities ── */
.lp-text-t2 {
  color: var(--t2) !important;
}

.lp-text-t3 {
  color: var(--t3) !important;
}

/* ── Mono ── */
.lp-mono {
  font-family: var(--mono) !important;
}
</style>
