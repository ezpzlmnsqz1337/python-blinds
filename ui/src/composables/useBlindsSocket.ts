import { computed, reactive, readonly, type ComputedRef } from 'vue'
import type {
  BlindState,
  BlindsSocketState,
  MotorId,
  SendCommand
} from '@/types'

const STEP_MESSAGE_PREFIX = 'blindsPosition'

const defaultBlindState = (): BlindState => ({
  position: 0,
  target: 0,
  limit: 0,
  ignoreLimits: 0
})

const state = reactive<BlindsSocketState>({
  connected: false,
  blinds: {
    0: defaultBlindState(),
    1: defaultBlindState()
  }
})

let socket: WebSocket | undefined
let reconnectTimer: number | undefined
let reconnectDelay = 1000

function getSocketUrls(): string[] {
  if (import.meta.env.VITE_WS_URL) {
    return [import.meta.env.VITE_WS_URL]
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const currentUrl = new URL(window.location.href)
  const proxyUrl = new URL(window.location.href)
  proxyUrl.protocol = protocol
  proxyUrl.pathname = '/ws'
  proxyUrl.search = ''
  proxyUrl.hash = ''

  const directUrl = new URL(window.location.href)
  directUrl.protocol = protocol
  directUrl.port = '8082'
  directUrl.pathname = '/'
  directUrl.search = ''
  directUrl.hash = ''

  const isLiteralIpv4 = /^\d{1,3}(?:\.\d{1,3}){3}$/.test(currentUrl.hostname)
  const isDirectHost =
    currentUrl.hostname === 'localhost' ||
    currentUrl.hostname === '127.0.0.1' ||
    isLiteralIpv4 ||
    currentUrl.port === '3000'

  return isDirectHost ? [directUrl.toString()] : [proxyUrl.toString()]
}

function getSocketUrl(): string {
  return getSocketUrls()[0]
}

function ensureSocket(): WebSocket {
  if (
    socket &&
    (socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING)
  ) {
    return socket
  }

  socket = new WebSocket(getSocketUrl())

  socket.onopen = () => {
    state.connected = true
    reconnectDelay = 1000
    if (reconnectTimer !== undefined) {
      window.clearTimeout(reconnectTimer)
      reconnectTimer = undefined
    }
  }

  socket.onmessage = (event: MessageEvent<string>) => {
    const payload = parseBlindMessage(event.data)
    if (!payload) {
      return
    }

    state.blinds[payload.motorId] = payload.blind
  }

  socket.onclose = () => {
    state.connected = false
    scheduleReconnect()
  }

  socket.onerror = () => {
    socket?.close()
  }

  return socket
}

function scheduleReconnect(): void {
  if (reconnectTimer !== undefined) {
    return
  }

  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = undefined
    reconnectDelay = Math.min(reconnectDelay * 2, 10000)
    ensureSocket()
  }, reconnectDelay)
}

function isMotorId(value: number): value is MotorId {
  return value === 0 || value === 1
}

function parseBlindMessage(
  message: string
): { motorId: MotorId; blind: BlindState } | null {
  if (!message.startsWith(STEP_MESSAGE_PREFIX)) {
    return null
  }

  const parts = message.split(':')
  const motorId = Number.parseInt(parts[2] ?? '', 10)

  if (!isMotorId(motorId)) {
    return null
  }

  return {
    motorId,
    blind: {
      position: Number.parseInt(parts[4] ?? '', 10),
      target: Number.parseInt(parts[6] ?? '', 10),
      limit: Number.parseInt(parts[8] ?? '', 10),
      ignoreLimits: Number.parseInt(parts[10] ?? '', 10)
    }
  }
}

const send: SendCommand = (message) => {
  const activeSocket = ensureSocket()
  if (activeSocket.readyState !== WebSocket.OPEN) {
    return false
  }

  activeSocket.send(message)
  return true
}

export function useBlindsSocket(): {
  state: Readonly<BlindsSocketState>
  connected: ComputedRef<boolean>
  send: SendCommand
} {
  ensureSocket()

  return {
    state: readonly(state) as Readonly<BlindsSocketState>,
    connected: computed(() => state.connected),
    send
  }
}
