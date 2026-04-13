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
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item clickable v-ripple to="/">
          <q-item-section>모니터링</q-item-section>
        </q-item>
        <q-item clickable v-ripple to="/workflow">
          <q-item-section>워크플로우</q-item-section>
        </q-item>
        <q-item clickable v-ripple to="/experiment">
          <q-item-section>실험 실행</q-item-section>
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

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>
