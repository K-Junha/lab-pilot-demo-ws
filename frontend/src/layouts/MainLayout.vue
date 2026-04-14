<template>
  <q-layout view="lHh Lpr lFf">

    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="toggleLeftDrawer" />
        <q-toolbar-title> LAB Pilot </q-toolbar-title>

        <!-- Theme selector -->
        <q-btn-dropdown flat dense icon="palette" :label="currentTheme.label" no-caps class="q-mr-sm">
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
        <q-btn-dropdown flat dense icon="text_fields" :label="currentFont.label" no-caps class="q-mr-sm">
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
        <q-btn-dropdown flat dense icon="format_size" :label="currentFontSize + 'px'" no-caps>
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

        <!-- User info + logout -->
        <q-btn flat dense no-caps class="q-ml-sm">
          <q-icon name="account_circle" class="q-mr-xs" />
          {{ authStore.user?.username }}
          <q-menu>
            <q-list dense style="min-width: 160px">
              <q-item-section class="q-pa-sm text-caption text-grey">
                {{ authStore.user?.role === 'admin' ? '관리자' : '연구원' }}
              </q-item-section>
              <q-separator />
              <q-item clickable v-close-popup @click="logout">
                <q-item-section avatar><q-icon name="logout" /></q-item-section>
                <q-item-section>로그아웃</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item
          clickable v-ripple to="/" exact
          active-class="side-menu-active"
        >
          <q-item-section avatar>
            <q-icon name="monitor_heart" />
          </q-item-section>
          <q-item-section>모니터링</q-item-section>
        </q-item>
        <q-item
          clickable v-ripple to="/workflow"
          active-class="side-menu-active"
        >
          <q-item-section avatar>
            <q-icon name="account_tree" />
          </q-item-section>
          <q-item-section>워크플로우</q-item-section>
        </q-item>
        <q-item
          clickable v-ripple to="/experiment"
          active-class="side-menu-active"
        >
          <q-item-section avatar>
            <q-icon name="science" />
          </q-item-section>
          <q-item-section>실험 실행</q-item-section>
        </q-item>
        <q-item
          clickable v-ripple to="/logs"
          active-class="side-menu-active"
        >
          <q-item-section avatar>
            <q-icon name="list_alt" />
          </q-item-section>
          <q-item-section>실험 로그</q-item-section>
        </q-item>
        <q-item
          clickable v-ripple to="/results"
          active-class="side-menu-active"
        >
          <q-item-section avatar>
            <q-icon name="analytics" />
          </q-item-section>
          <q-item-section>결과</q-item-section>
        </q-item>
        <q-item
          v-if="authStore.isAdmin"
          clickable v-ripple to="/admin"
          active-class="side-menu-active"
        >
          <q-item-section avatar>
            <q-icon name="admin_panel_settings" />
          </q-item-section>
          <q-item-section>관리자</q-item-section>
        </q-item>
      </q-list>
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
.side-menu-active {
  background: var(--q-primary);
  color: white;
  font-weight: 600;
  border-radius: 8px;
  margin: 4px 8px;
}
.side-menu-active .q-icon {
  color: white !important;
}
</style>
