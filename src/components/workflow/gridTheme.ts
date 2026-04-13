import { computed } from 'vue'
import { themeQuartz } from 'ag-grid-community'
import { useTheme, type ThemeDef } from 'src/composables/useTheme'

function buildGridTheme(theme: ThemeDef) {
  if (!theme.dark) return themeQuartz

  const c = theme.colors
  return themeQuartz.withParams({
    backgroundColor: c.dark,
    foregroundColor: '#E6EEF3',
    headerBackgroundColor: c.secondary,
    headerTextColor: '#9FB3C8',
    borderColor: c.secondary,
    rowHoverColor: c.secondary,
    selectedRowBackgroundColor: `${c.primary}1F`,
    oddRowBackgroundColor: c.dark,
    headerFontWeight: 600,
    wrapperBorderRadius: 8,
    checkboxCheckedBackgroundColor: c.primary,
    checkboxCheckedBorderColor: c.primary,
    checkboxCheckedShapeColor: '#ffffff',
    inputFocusBorder: { color: c.primary },
    rangeSelectionBackgroundColor: `${c.primary}26`,
    columnDropCellBackgroundColor: c.secondary,
    modalOverlayBackgroundColor: `${c['dark-page']}B3`,
  })
}

export function useGridTheme() {
  const { currentTheme } = useTheme()
  const gridTheme = computed(() => buildGridTheme(currentTheme.value!))
  return { gridTheme }
}
