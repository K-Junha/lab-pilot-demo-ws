import { ref } from 'vue'

export interface OxideInfo {
  formula: string
  name_ko: string
  molar_mass: number
  category: string
}

const BACKEND_URL = 'http://localhost:8000'

const oxideCache = ref<OxideInfo[]>([])
const loading = ref(false)

export function useMaterials() {
  async function fetchOxides(): Promise<OxideInfo[]> {
    if (oxideCache.value.length > 0) return oxideCache.value

    loading.value = true
    try {
      const res = await fetch(`${BACKEND_URL}/api/materials/oxides`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      oxideCache.value = await res.json()
      return oxideCache.value
    } finally {
      loading.value = false
    }
  }

  return {
    oxides: oxideCache,
    loading,
    fetchOxides,
  }
}
