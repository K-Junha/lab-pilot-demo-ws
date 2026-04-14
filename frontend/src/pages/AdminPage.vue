<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">관리자 — 사용자 관리</div>

    <q-table
      :rows="users"
      :columns="columns"
      row-key="user_id"
      flat
      bordered
      :loading="loading"
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
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import type { QTableColumn } from 'quasar'

const API_BASE = 'http://localhost:8000/api'

interface UserRow {
  user_id: number
  username: string
  email: string | null
  role: string
  created_at: string
}

const $q = useQuasar()
const authStore = useAuthStore()
const users = ref<UserRow[]>([])
const loading = ref(false)

function authHeader() {
  return { Authorization: `Bearer ${authStore.token ?? ''}`, 'Content-Type': 'application/json' }
}

const columns: QTableColumn[] = [
  { name: 'user_id', label: 'ID', field: 'user_id', align: 'left', sortable: true },
  { name: 'username', label: '사용자명', field: 'username', align: 'left', sortable: true },
  { name: 'email', label: '이메일', field: 'email', align: 'left' },
  { name: 'role', label: 'Role', field: 'role', align: 'left', sortable: true },
  { name: 'created_at', label: '가입일', field: 'created_at', align: 'left', format: (v: string) => new Date(v).toLocaleDateString('ko-KR') },
  { name: 'actions', label: '관리', field: 'user_id', align: 'center' },
]

async function loadUsers() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/admin/users`, { headers: authHeader() })
    if (!res.ok) throw new Error()
    users.value = await res.json() as UserRow[]
  } finally {
    loading.value = false
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

function deleteUser(user: UserRow) {
  $q.dialog({
    title: '계정 삭제',
    message: `'${user.username}' 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`,
    cancel: { flat: true, label: '취소' },
    ok: { color: 'negative', label: '삭제' },
  }).onOk(async () => {
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
  })
}

onMounted(() => void loadUsers())
</script>
