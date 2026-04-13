import { ref, watch, computed } from 'vue'
import { setCssVar, Dark } from 'quasar'

/* ── Theme definitions ── */

export interface ThemeDef {
  key: string
  label: string
  desc: string
  dark: boolean
  colors: {
    primary: string
    secondary: string
    accent: string
    dark: string
    'dark-page': string
    positive: string
    negative: string
    info: string
    warning: string
  }
}

export const themes: ThemeDef[] = [
  {
    key: 'navy',
    label: '네이비 다크',
    desc: '전문적 · 신뢰감',
    dark: true,
    colors: {
      primary: '#3AA6FF', secondary: '#163A4F', accent: '#5BB8FF',
      dark: '#0B1D2A', 'dark-page': '#0F2438',
      positive: '#2ECC71', negative: '#E74C3C', info: '#3498DB', warning: '#F1C40F',
    },
  },
  {
    key: 'charcoal',
    label: '차콜 그레이',
    desc: '모던 · 미니멀',
    dark: true,
    colors: {
      primary: '#6C63FF', secondary: '#16213E', accent: '#A29BFE',
      dark: '#1A1A2E', 'dark-page': '#16213E',
      positive: '#00C897', negative: '#FF6B6B', info: '#74B9FF', warning: '#FDCB6E',
    },
  },
  {
    key: 'midnight-green',
    label: '미드나이트 그린',
    desc: '자연 · 안정감',
    dark: true,
    colors: {
      primary: '#00BFA6', secondary: '#1B2838', accent: '#64FFDA',
      dark: '#0D1B2A', 'dark-page': '#1B2838',
      positive: '#00E676', negative: '#FF5252', info: '#40C4FF', warning: '#FFD740',
    },
  },
  {
    key: 'slate-blue',
    label: '슬레이트 블루',
    desc: '세련 · 차분',
    dark: true,
    colors: {
      primary: '#5C6BC0', secondary: '#181825', accent: '#89B4FA',
      dark: '#1E1E2E', 'dark-page': '#181825',
      positive: '#A6E3A1', negative: '#F38BA8', info: '#89B4FA', warning: '#F9E2AF',
    },
  },
  {
    key: 'deep-ocean',
    label: '딥 오션',
    desc: '고급 · 대비 강함',
    dark: true,
    colors: {
      primary: '#00B4D8', secondary: '#0A0E1A', accent: '#48CAE4',
      dark: '#03071E', 'dark-page': '#0A0E1A',
      positive: '#06D6A0', negative: '#EF476F', info: '#118AB2', warning: '#FFD166',
    },
  },
  {
    key: 'warm-dark',
    label: '웜 다크',
    desc: '따뜻함 · 편안함',
    dark: true,
    colors: {
      primary: '#FF8C42', secondary: '#212121', accent: '#FFB74D',
      dark: '#1A1A1A', 'dark-page': '#212121',
      positive: '#66BB6A', negative: '#EF5350', info: '#42A5F5', warning: '#FFCA28',
    },
  },
  {
    key: 'nordic',
    label: '노르딕',
    desc: '깔끔 · 북유럽 감성',
    dark: true,
    colors: {
      primary: '#88C0D0', secondary: '#3B4252', accent: '#81A1C1',
      dark: '#2E3440', 'dark-page': '#3B4252',
      positive: '#A3BE8C', negative: '#BF616A', info: '#81A1C1', warning: '#EBCB8B',
    },
  },
  {
    key: 'cyber',
    label: '사이버 테크',
    desc: '미래적 · 강렬',
    dark: true,
    colors: {
      primary: '#00FF88', secondary: '#111111', accent: '#00FF88',
      dark: '#0A0A0A', 'dark-page': '#111111',
      positive: '#00FF88', negative: '#FF0055', info: '#00D4FF', warning: '#FFE600',
    },
  },
  {
    key: 'default-light',
    label: '기본 라이트',
    desc: 'Quasar 기본',
    dark: false,
    colors: {
      primary: '#1976D2', secondary: '#26A69A', accent: '#9C27B0',
      dark: '#1D1D1D', 'dark-page': '#121212',
      positive: '#21BA45', negative: '#C10015', info: '#31CCEC', warning: '#F2C037',
    },
  },
]

/* ── Font definitions ── */

export interface FontDef {
  key: string
  label: string
  family: string
  url: string | null   // Google Fonts URL, null = system font
  desc: string
}

export const fonts: FontDef[] = [
  {
    key: 'roboto',
    label: 'Roboto',
    family: 'Roboto, sans-serif',
    url: null, // Already included via Quasar extras
    desc: '기본 · 깔끔',
  },
  {
    key: 'inter',
    label: 'Inter',
    family: 'Inter, sans-serif',
    url: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
    desc: 'UI 특화 · 가독성 우수',
  },
  {
    key: 'pretendard',
    label: 'Pretendard',
    family: 'Pretendard, sans-serif',
    url: 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css',
    desc: '한글 최적화 · 현대적',
  },
  {
    key: 'noto-sans-kr',
    label: 'Noto Sans KR',
    family: '"Noto Sans KR", sans-serif',
    url: 'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap',
    desc: '한글 표준 · 무난',
  },
  {
    key: 'ibm-plex',
    label: 'IBM Plex Sans',
    family: '"IBM Plex Sans", sans-serif',
    url: 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap',
    desc: '기술 문서 · 데이터 친화',
  },
  {
    key: 'jetbrains',
    label: 'JetBrains Mono',
    family: '"JetBrains Mono", monospace',
    url: 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap',
    desc: '모노스페이스 · 개발자 감성',
  },
]

export const fontSizes = [12, 13, 14, 15, 16, 18]

/* ── Persistence keys ── */
const THEME_KEY = 'lab-pilot-theme'
const FONT_KEY = 'lab-pilot-font'
const FONTSIZE_KEY = 'lab-pilot-fontsize'

/* ── State ── */
const currentThemeKey = ref(localStorage.getItem(THEME_KEY) ?? 'default-light')
const currentFontKey = ref(localStorage.getItem(FONT_KEY) ?? 'roboto')
const currentFontSize = ref(Number(localStorage.getItem(FONTSIZE_KEY)) || 14)

const currentTheme = computed(() =>
  themes.find(t => t.key === currentThemeKey.value) ?? themes[themes.length - 1]!
)
const currentFont = computed(() =>
  fonts.find(f => f.key === currentFontKey.value) ?? fonts[0]!
)

/* ── Font link loader ── */
const loadedFontUrls = new Set<string>()

function loadFontLink(url: string) {
  if (loadedFontUrls.has(url)) return
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = url
  document.head.appendChild(link)
  loadedFontUrls.add(url)
}

/* ── Apply functions ── */

function applyTheme(theme: ThemeDef) {
  Dark.set(theme.dark)
  const keys = Object.keys(theme.colors) as (keyof ThemeDef['colors'])[]
  for (const key of keys) {
    setCssVar(key, theme.colors[key])
  }
}

function applyFont(font: FontDef) {
  if (font.url) loadFontLink(font.url)
  document.body.style.fontFamily = font.family
}

function applyFontSize(size: number) {
  document.documentElement.style.fontSize = `${size}px`
}

/* ── Watchers ── */

watch(currentThemeKey, (key) => {
  localStorage.setItem(THEME_KEY, key)
  const theme = themes.find(t => t.key === key)
  if (theme) applyTheme(theme)
}, { immediate: true })

watch(currentFontKey, (key) => {
  localStorage.setItem(FONT_KEY, key)
  const font = fonts.find(f => f.key === key)
  if (font) applyFont(font)
}, { immediate: true })

watch(currentFontSize, (size) => {
  localStorage.setItem(FONTSIZE_KEY, String(size))
  applyFontSize(size)
}, { immediate: true })

/* ── Export ── */

export function useTheme() {
  return {
    themes,
    fonts,
    fontSizes,
    currentThemeKey,
    currentFontKey,
    currentFontSize,
    currentTheme,
    currentFont,
  }
}
