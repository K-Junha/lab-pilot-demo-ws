const host = window.location.hostname
const port = import.meta.env.VITE_BACKEND_PORT

export const API_BASE = `http://${host}:${port}/api`
export const WS_BASE = `ws://${host}:${port}`
