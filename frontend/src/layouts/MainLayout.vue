<template>
  <q-layout view="lHh Lpr lFf">

    <q-header>
      <q-toolbar class="lp-header">
        <!-- Hamburger (mobile) -->
        <q-btn flat dense round icon="menu" color="grey-5" class="lp-header__menu-btn" @click="toggleLeftDrawer" />

        <!-- Logo -->
        <div class="lp-logo">
          <div class="lp-logo__icon">
            <q-icon name="science" size="14px" color="white" />
          </div>
          <span class="lp-logo__text">LAB PILOT</span>
        </div>

        <div class="lp-header__divider" />

        <q-space />

        <!-- Theme selector -->
        <q-btn-dropdown
          flat dense no-caps
          icon="palette"
          :label="currentTheme.label"
          class="lp-header__ctrl-btn q-mr-xs"
        >
          <q-list dense style="min-width: 220px">
            <q-item
              v-for="t in themes"
              :key="t.key"
              clickable
              v-close-popup
              @click="currentThemeKey = t.key"
              :active="t.key === currentThemeKey"
            >
              <q-item-section side>
                <q-avatar size="20px" :style="{ background: t.colors.primary }" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ t.label }}</q-item-label>
                <q-item-label caption>{{ t.desc }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>

        <!-- Font selector -->
        <q-btn-dropdown
          flat dense no-caps
          icon="text_fields"
          :label="currentFont.label"
          class="lp-header__ctrl-btn q-mr-xs"
        >
          <q-list dense style="min-width: 220px">
            <q-item
              v-for="f in fonts"
              :key="f.key"
              clickable
              v-close-popup
              @click="currentFontKey = f.key"
              :active="f.key === currentFontKey"
            >
              <q-item-section>
                <q-item-label>{{ f.label }}</q-item-label>
                <q-item-label caption>{{ f.desc }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>

        <!-- Font size selector -->
        <q-btn-dropdown
          flat dense no-caps
          icon="format_size"
          :label="currentFontSize + 'px'"
          class="lp-header__ctrl-btn q-mr-sm"
        >
          <q-list dense>
            <q-item
              v-for="s in fontSizes"
              :key="s"
              clickable
              v-close-popup
              @click="currentFontSize = s"
              :active="s === currentFontSize"
            >
              <q-item-section>{{ s }}px</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>

        <div class="lp-header__vr" />

        <!-- User menu -->
        <q-btn flat dense no-caps class="lp-header__user-btn">
          <div class="lp-avatar">{{ authStore.user?.username?.charAt(0).toUpperCase() }}</div>
          <span class="lp-header__username q-mx-xs">{{ authStore.user?.username }}</span>
          <q-icon name="expand_more" size="14px" color="grey-5" />
          <q-menu class="lp-user-menu">
            <q-list dense style="min-width: 180px">
              <div class="lp-user-menu__info">
                <div class="lp-user-menu__name">{{ authStore.user?.username }}</div>
                <div class="lp-user-menu__role">{{ authStore.user?.role === 'admin' ? '관리자' : '연구원' }}</div>
              </div>
              <q-separator />
              <q-item clickable v-close-popup @click="logout" class="lp-user-menu__logout">
                <q-item-section avatar><q-icon name="logout" size="16px" /></q-item-section>
                <q-item-section>로그아웃</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above :width="208" class="lp-sidebar">
      <div class="lp-sidebar__inner">
        <nav class="lp-nav">
          <router-link to="/" custom v-slot="{ isActive, navigate }">
            <div class="lp-nav__item" :class="{ 'lp-nav__item--active': isActive }" @click="navigate">
              <q-icon name="monitor_heart" size="16px" class="lp-nav__icon" />
              <span class="lp-nav__label">모니터링</span>
            </div>
          </router-link>

          <router-link to="/workflow" custom v-slot="{ isActive, navigate }">
            <div class="lp-nav__item" :class="{ 'lp-nav__item--active': isActive }" @click="navigate">
              <q-icon name="account_tree" size="16px" class="lp-nav__icon" />
              <span class="lp-nav__label">워크플로우</span>
            </div>
          </router-link>

          <router-link to="/experiment" custom v-slot="{ isActive, navigate }">
            <div class="lp-nav__item" :class="{ 'lp-nav__item--active': isActive }" @click="navigate">
              <q-icon name="science" size="16px" class="lp-nav__icon" />
              <span class="lp-nav__label">실험 실행</span>
            </div>
          </router-link>

          <router-link to="/logs" custom v-slot="{ isActive, navigate }">
            <div class="lp-nav__item" :class="{ 'lp-nav__item--active': isActive }" @click="navigate">
              <q-icon name="list_alt" size="16px" class="lp-nav__icon" />
              <span class="lp-nav__label">실험 로그</span>
            </div>
          </router-link>

          <router-link to="/results" custom v-slot="{ isActive, navigate }">
            <div class="lp-nav__item" :class="{ 'lp-nav__item--active': isActive }" @click="navigate">
              <q-icon name="analytics" size="16px" class="lp-nav__icon" />
              <span class="lp-nav__label">결과</span>
            </div>
          </router-link>

          <router-link v-if="authStore.isAdmin" to="/admin" custom v-slot="{ isActive, navigate }">
            <div class="lp-nav__item" :class="{ 'lp-nav__item--active': isActive }" @click="navigate">
              <q-icon name="admin_panel_settings" size="16px" class="lp-nav__icon" />
              <span class="lp-nav__label">관리자</span>
            </div>
          </router-link>
        </nav>

        <div class="lp-sidebar__spacer" />

        <div class="lp-sidebar__footer">
          <div class="lp-avatar lp-avatar--lg">{{ authStore.user?.username?.charAt(0).toUpperCase() }}</div>
          <div class="lp-sidebar__user-info">
            <div class="lp-sidebar__user-name">{{ authStore.user?.username }}</div>
            <div class="lp-sidebar__user-role">{{ authStore.user?.role === 'admin' ? '관리자' : '연구원' }}</div>
          </div>
        </div>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useTheme } from 'src/composables/useTheme';
import { useAuthStore } from 'src/stores/auth';
import { useAuth } from 'src/composables/useAuth';

const {
  themes,
  fonts,
  fontSizes,
  currentThemeKey,
  currentFontKey,
  currentFontSize,
  currentTheme,
  currentFont,
} = useTheme();

const authStore = useAuthStore();
const { logout } = useAuth();

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>

<style scoped>
/* ── Header ── */
.lp-header {
  padding: 0 16px;
  gap: 8px;
}

.lp-header__menu-btn {
  display: none;
}

@media (max-width: 1023px) {
  .lp-header__menu-btn {
    display: inline-flex;
  }
}

.lp-header__divider {
  width: 1px;
  height: 20px;
  background: var(--bd);
  margin: 0 4px;
}

.lp-header__vr {
  width: 1px;
  height: 20px;
  background: var(--bd);
  margin: 0 8px;
}

.lp-header__ctrl-btn {
  color: var(--t2) !important;
  font-size: 12px;
  font-family: var(--sans);
}

.lp-header__ctrl-btn :deep(.q-btn__content) {
  gap: 4px;
}

.lp-header__user-btn {
  color: var(--t2) !important;
  border-radius: var(--r1);
  padding: 4px 8px !important;
}

.lp-header__user-btn:hover {
  background: var(--s2) !important;
}

.lp-header__username {
  font-size: 13px;
  color: var(--t1);
  font-family: var(--sans);
}

/* ── Logo ── */
.lp-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lp-logo__icon {
  width: 24px;
  height: 24px;
  background: var(--accent);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lp-logo__text {
  font-family: var(--mono);
  font-weight: 600;
  font-size: 13px;
  color: var(--t1);
  letter-spacing: 0.06em;
}

/* ── Avatar ── */
.lp-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--s4);
  color: var(--t2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.lp-avatar--lg {
  width: 28px;
  height: 28px;
  font-size: 12px;
}

/* ── User menu ── */
.lp-user-menu__info {
  padding: 10px 12px 8px;
}

.lp-user-menu__name {
  font-size: 13px;
  font-weight: 600;
  color: var(--t1);
  margin-bottom: 2px;
}

.lp-user-menu__role {
  font-size: 11px;
  color: var(--t3);
  font-family: var(--mono);
}

.lp-user-menu__logout {
  color: var(--t2) !important;
  font-size: 13px;
}

/* ── Sidebar ── */
.lp-sidebar :deep(.q-drawer__content) {
  display: flex;
  flex-direction: column;
}

.lp-sidebar__inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 10px 8px;
}

/* ── Nav ── */
.lp-nav {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.lp-nav__item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 10px;
  border-radius: var(--r1);
  border-left: 2px solid transparent;
  cursor: pointer;
  color: var(--t2);
  font-size: 13px;
  transition: background 0.12s, color 0.12s;
  user-select: none;
}

.lp-nav__item:hover {
  background: var(--s2);
  color: var(--t1);
}

.lp-nav__item--active {
  background: var(--accent-bg);
  border-left-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}

.lp-nav__item--active .lp-nav__icon {
  color: var(--accent) !important;
}

.lp-nav__icon {
  color: var(--t3);
  flex-shrink: 0;
}

.lp-nav__label {
  flex: 1;
}

/* ── Sidebar footer ── */
.lp-sidebar__spacer {
  flex: 1;
}

.lp-sidebar__footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 10px 4px;
  border-top: 1px solid var(--bd);
  margin-top: 8px;
}

.lp-sidebar__user-info {
  flex: 1;
  min-width: 0;
}

.lp-sidebar__user-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--t1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lp-sidebar__user-role {
  font-size: 10px;
  color: var(--t3);
  font-family: var(--mono);
}
</style>
