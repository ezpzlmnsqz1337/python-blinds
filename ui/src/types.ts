export type MotorId = 0 | 1

export interface BlindState {
  position: number
  target: number
  limit: number
  ignoreLimits: number
}

export interface BlindsSocketState {
  connected: boolean
  blinds: Record<MotorId, BlindState>
}

export interface BlindTab {
  id: MotorId
  title: string
  frameWidthRem: number
  frameAspectRatio: number
}

export type SendCommand = (message: string) => boolean
