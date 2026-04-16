<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">관리자</div>

    <q-tabs v-model="tab" dense align="left" class="q-mb-md">
      <q-tab name="devices" label="장치 관리" />
      <q-tab name="users" label="사용자 관리" />
    </q-tabs>

    <q-tab-panels v-model="tab" animated>
      <!-- ── 장치 관리 탭 ─────────────────────────────────────────────── -->
      <q-tab-panel name="devices">
        <div class="text-subtitle1 q-mb-sm">ss_manager 목록</div>

        <q-table
          :rows="managers"
          :columns="managerColumns"
          row-key="id"
          flat
          bordered
          :loading="managersLoading"
          no-data-label="등록된 ss_manager가 없습니다"
          class="q-mb-lg"
        >
          <template #body-cell-online="props">
            <q-td :props="props">
              <q-badge :color="props.value ? 'positive' : 'grey'" :label="props.value ? '온라인' : '오프라인'" />
            </q-td>
          </template>
          <template #body-cell-actions="props">
            <q-td :props="props">
              <q-btn flat dense size="sm" label="삭제" color="negative" @click="deleteManager(props.row)" />
            </q-td>
          </template>
        </q-table>

        <div class="text-subtitle1 q-mb-sm">새 ss_manager 등록</div>
        <div class="row q-col-gutter-sm items-end">
          <div class="col-12 col-sm-3">
            <q-input v-model="form.name" label="이름" outlined dense />
          </div>
          <div class="col-12 col-sm-3">
            <q-input v-model="form.host" label="호스트 (IP)" outlined dense />
          </div>
          <div class="col-6 col-sm-2">
            <q-input v-model.number="form.ws_port" label="WS 포트" type="number" outlined dense />
          </div>
          <div class="col-6 col-sm-2">
            <q-input v-model="form.api_key" label="API Key" outlined dense />
          </div>
          <div class="col-12 col-sm-2">
            <q-btn label="등록" color="primary" unelevated :loading="registering" @click="registerManager" />
          </div>
        </div>
      </q-tab-panel>

      <!-- ── 사용자 관리 탭 ───────────────────────────────────────────── -->
      <q-tab-panel name="users">
        <div class="text-subtitle1 q-mb-sm">사용자 관리</div>

        <q-table
          :rows="users"
          :columns="userColumns"
          row-key="user_id"
          flat
          bordered
          :loading="usersLoading"
        >
          <template #body-cell-role="props">
            <q-td :props="props">
              <q-badge :color="props.value === 'admin' ? 'deep-purple' : 'teal'" :label="props.value" />
            </q-td>
          </template>
          <template #body-cell-actions="props">
            <q-td :props="props">
              <q-btn-group flat>
                <q-btn
                  flat
                  dense
                  size="sm"
                  :label="props.row.role === 'admin' ? '→ user' : '→ admin'"
                  :color="props.row.role === 'admin' ? 'orange' : 'deep-purple'"
                  :disable="props.row.user_id === authStore.user?.user_id"
                  @click="changeRole(props.row)"
                />
                <q-btn
                  flat
                  dense
                  size="sm"
                  label="삭제"
                  color="negative"
                  :disable="props.row.user_id === authStore.user?.user_id"
                  @click="deleteUser(props.row)"
                />
              </q-btn-group>
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import type { QTableColumn } from 'quasar'

const API_BASE = 'http://localhost:8000/api'

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

const managerColumns: QTableColumn[] = [
  { name: 'id', label: 'ID', field: 'id', align: 'left', sortable: true },
  { name: 'name', label: '이름', field: 'name', align: 'left', sortable: true },
  { name: 'host', label: '호스트', field: 'host', align: 'left' },
  { name: 'ws_port', label: 'WS 포트', field: 'ws_port', align: 'left' },
  { name: 'online', label: '상태', field: 'online', align: 'center' },
  { name: 'last_seen', label: '마지막 연결', field: 'last_seen', align: 'left',
    format: (v: string | null) => (v ? new Date(v).toLocaleString('ko-KR') : '-') },
  { name: 'actions', label: '관리', field: 'id', align: 'center' },
]

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

const userColumns: QTableColumn[] = [
  { name: 'user_id', label: 'ID', field: 'user_id', align: 'left', sortable: true },
  { name: 'username', label: '사용자명', field: 'username', align: 'left', sortable: true },
  { name: 'email', label: '이메일', field: 'email', align: 'left' },
  { name: 'role', label: 'Role', field: 'role', align: 'left', sortable: true },
  { name: 'created_at', label: '가입일', field: 'created_at', align: 'left',
    format: (v: string) => new Date(v).toLocaleDateString('ko-KR') },
  { name: 'actions', label: '관리', field: 'user_id', align: 'center' },
]

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
