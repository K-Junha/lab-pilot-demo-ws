<template>
  <div class="flex flex-center" style="min-height: 100vh; background: #f5f5f5;">
    <q-card style="min-width: 360px; max-width: 400px; width: 100%">
      <q-card-section class="text-center q-pb-none">
        <div class="text-h5 q-mb-sm">LAB Pilot</div>
        <div class="text-subtitle2 text-grey">{{ isRegister ? '회원가입' : '로그인' }}</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit.prevent="onSubmit" class="q-gutter-md">
          <q-input
            v-model="username"
            label="사용자명"
            outlined
            dense
            autofocus
            :rules="[(v) => !!v || '사용자명을 입력하세요']"
          />
          <q-input
            v-if="isRegister"
            v-model="email"
            label="이메일 (선택)"
            type="email"
            outlined
            dense
          />
          <q-input
            v-model="password"
            label="비밀번호"
            :type="showPassword ? 'text' : 'password'"
            outlined
            dense
            :rules="[(v) => !!v || '비밀번호를 입력하세요']"
          >
            <template #append>
              <q-icon
                :name="showPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>

          <q-btn
            type="submit"
            :label="isRegister ? '회원가입' : '로그인'"
            color="primary"
            class="full-width"
            :loading="loading"
          />
        </q-form>
      </q-card-section>

      <q-card-section class="text-center q-pt-none">
        <q-btn
          flat
          dense
          no-caps
          :label="isRegister ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'"
          @click="isRegister = !isRegister"
        />
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from 'src/composables/useAuth'

const router = useRouter()
const { login, register } = useAuth()

const username = ref('')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isRegister = ref(false)
const loading = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    if (isRegister.value) {
      const ok = await register(username.value, password.value, email.value || undefined)
      if (ok) {
        isRegister.value = false
        password.value = ''
      }
    } else {
      const ok = await login(username.value, password.value)
      if (ok) {
        await router.push('/')
      }
    }
  } finally {
    loading.value = false
  }
}
</script>
