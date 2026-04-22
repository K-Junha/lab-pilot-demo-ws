<template>
  <div class="lp-login-wrap">
    <div class="lp-login-box">
      <!-- Logo -->
      <div class="lp-login-logo">
        <div class="lp-login-logo__icon">
          <q-icon name="science" size="18px" color="white" />
        </div>
        <div>
          <div class="lp-login-logo__title">LAB PILOT</div>
          <div class="lp-login-logo__sub">실험실 자동화 플랫폼</div>
        </div>
      </div>

      <!-- Card -->
      <div class="lp-login-card">
        <div class="lp-login-card__head">
          <div class="lp-login-card__title">{{ isRegister ? '회원가입' : '로그인' }}</div>
          <div class="lp-login-card__desc">계정 정보를 입력해주세요</div>
        </div>

        <q-form @submit.prevent="onSubmit" class="lp-login-form">
          <q-input
            v-model="username"
            label="사용자명"
            outlined
            dense
            autofocus
            :rules="[(v) => !!v || '사용자명을 입력하세요']"
            class="lp-input"
          />
          <q-input
            v-if="isRegister"
            v-model="email"
            label="이메일 (선택)"
            type="email"
            outlined
            dense
            class="lp-input"
          />
          <q-input
            v-model="password"
            label="비밀번호"
            :type="showPassword ? 'text' : 'password'"
            outlined
            dense
            :rules="[(v) => !!v || '비밀번호를 입력하세요']"
            class="lp-input"
          >
            <template #append>
              <q-icon
                :name="showPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                style="color: var(--t3);"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>

          <q-btn
            type="submit"
            :label="isRegister ? '회원가입' : '로그인'"
            unelevated
            class="lp-login-btn full-width"
            :loading="loading"
          />
        </q-form>

        <div class="lp-login-card__footer">
          <button class="lp-login-toggle" @click="isRegister = !isRegister">
            {{ isRegister ? '이미 계정이 있으신가요? ' : '계정이 없으신가요? ' }}
            <span class="lp-login-toggle__link">{{ isRegister ? '로그인 →' : '회원가입 →' }}</span>
          </button>
        </div>
      </div>

      <!-- Bottom -->
      <div class="lp-login-bottom">
        <span>v2.4.1</span>
        <span class="lp-login-status">
          <span class="lp-login-status__dot" />
          시스템 정상
        </span>
      </div>
    </div>
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

<style scoped>
.lp-login-wrap {
  min-height: 100vh;
  background: var(--bg);
  background-image: radial-gradient(ellipse 60% 50% at 50% 0%, rgba(79, 142, 247, 0.06) 0%, transparent 60%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.lp-login-box {
  width: 360px;
  animation: lp-fade-up 0.4s ease;
}

/* ── Logo ── */
.lp-login-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
}

.lp-login-logo__icon {
  width: 36px;
  height: 36px;
  background: var(--accent);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(79, 142, 247, 0.3);
  flex-shrink: 0;
}

.lp-login-logo__title {
  font-family: var(--mono);
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.08em;
  color: var(--t1);
}

.lp-login-logo__sub {
  font-size: 11px;
  color: var(--t3);
  letter-spacing: 0.03em;
  margin-top: 1px;
}

/* ── Card ── */
.lp-login-card {
  background: var(--s1);
  border: 1px solid var(--bd);
  border-radius: var(--r2);
  box-shadow: var(--shadow);
  padding: 24px;
  margin-bottom: 16px;
}

.lp-login-card__head {
  margin-bottom: 20px;
}

.lp-login-card__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--t1);
  margin-bottom: 4px;
}

.lp-login-card__desc {
  font-size: 12px;
  color: var(--t3);
}

/* ── Form ── */
.lp-login-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lp-input :deep(.q-field__control) {
  background: var(--s2) !important;
}

/* ── Login button ── */
.lp-login-btn {
  background: var(--accent) !important;
  color: white !important;
  font-weight: 500;
  font-size: 13px;
  padding: 10px 0 !important;
  border-radius: var(--r1) !important;
  margin-top: 6px;
}

/* ── Footer ── */
.lp-login-card__footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--bd);
  text-align: center;
}

.lp-login-toggle {
  background: none;
  border: none;
  color: var(--t3);
  font-size: 11px;
  cursor: pointer;
  font-family: var(--sans);
  padding: 0;
}

.lp-login-toggle__link {
  color: var(--accent);
}

/* ── Bottom bar ── */
.lp-login-bottom {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--t4);
  font-family: var(--mono);
}

.lp-login-status {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--green);
}

.lp-login-status__dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--green);
  display: inline-block;
}
</style>
