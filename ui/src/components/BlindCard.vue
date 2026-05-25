<template>
  <article class="card">
    <header class="card-header">
      <h2>{{ title }}</h2>
    </header>

    <div class="window-shell">
      <div class="control-stack left-controls">
        <button
          class="side-control"
          type="button"
          aria-label="Move up"
          @click="moveUp()"
        >
          <span class="icon">▲</span>
        </button>
        <button
          class="side-control stop"
          type="button"
          aria-label="Stop"
          :disabled="isStopped"
          @click="stop"
        >
          <span class="icon">■</span>
        </button>
        <button
          class="side-control"
          type="button"
          aria-label="Move down"
          @click="moveDown()"
        >
          <span class="icon">▼</span>
        </button>
      </div>

      <button
        v-if="settingsEnabled"
        class="calibration warning top-calibration"
        type="button"
        @click="setTopPosition()"
      >
        ⤒ Set Top
      </button>

      <div class="window">
        <div class="frame" :style="frameStyle">
          <div class="glass"></div>
          <div class="blind" :style="blindStyle"></div>
          <div v-if="showTarget" class="target" :style="targetStyle"></div>
        </div>
      </div>

      <button
        v-if="settingsEnabled"
        class="calibration warning bottom-calibration"
        type="button"
        @click="setLimit()"
      >
        ⤓ Set Bottom
      </button>

      <div class="control-stack right-controls">
        <button
          class="side-control open-close-control"
          type="button"
          aria-label="Open blind"
          @click="openBlind"
        >
          <span class="icon">⇤</span>
        </button>
        <button
          class="side-control open-close-control"
          type="button"
          aria-label="Close blind"
          @click="closeBlind"
        >
          <span class="icon">⇥</span>
        </button>
      </div>
    </div>

    <div v-if="settingsEnabled" class="card-footer">
      <dl class="stats">
        <div>
          <dt>Position</dt>
          <dd>{{ blind.position }}</dd>
        </div>
        <div>
          <dt>Target</dt>
          <dd>{{ blind.target }}</dd>
        </div>
        <div>
          <dt>Limit</dt>
          <dd>{{ blind.limit }}</dd>
        </div>
      </dl>

      <button
        class="toggle"
        type="button"
        :class="blind.ignoreLimits ? 'danger' : 'success'"
        @click="toggleIgnoreLimits"
      >
        IGNORE LIMITS: {{ blind.ignoreLimits ? 'YES' : 'NO' }}
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed, type PropType } from 'vue'
import type { BlindState, SendCommand } from '@/types'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  motorId: {
    type: Number,
    required: true
  },
  frameWidthRem: {
    type: Number,
    required: true
  },
  frameAspectRatio: {
    type: Number,
    required: true
  },
  blind: {
    type: Object as PropType<BlindState>,
    required: true
  },
  password: {
    type: String,
    default: ''
  },
  settingsEnabled: {
    type: Boolean,
    default: false
  },
  send: {
    type: Function as PropType<SendCommand>,
    required: true
  }
})

const MIN_MOTOR_STEP = 5000

const isStopped = computed(() => props.blind.position === props.blind.target)
const showTarget = computed(() => props.blind.position !== props.blind.target)

const blindStyle = computed(() => ({
  transform: `scaleY(${clampScale(props.blind.position, props.blind.limit)})`
}))

const targetStyle = computed(() => ({
  transform: `scaleY(${clampScale(props.blind.target, props.blind.limit)})`
}))

const frameStyle = computed(() => ({
  width: `${props.frameWidthRem}rem`,
  aspectRatio: `${props.frameAspectRatio}`
}))

function clampScale(value: number, limit: number): number {
  if (!limit) {
    return 0
  }

  return Math.min(Math.max(value / limit, 0), 1)
}

function moveUp(steps: number = MIN_MOTOR_STEP): void {
  props.send(`up:${props.motorId}:${steps}`)
}

function moveDown(steps: number = MIN_MOTOR_STEP): void {
  props.send(`down:${props.motorId}:${steps}`)
}

function stop(): void {
  props.send(`stop:${props.motorId}`)
}

function openBlind(): void {
  props.send(`openBlind:${props.motorId}`)
}

function closeBlind(): void {
  props.send(`closeBlind:${props.motorId}`)
}

function setTopPosition(): void {
  props.send(`setTopPosition:${props.motorId}:${props.password}`)
}

function setLimit(): void {
  props.send(`setLimit:${props.motorId}:${props.password}`)
}

function toggleIgnoreLimits(): void {
  const next = props.blind.ignoreLimits === 1 ? 0 : 1
  props.send(`setIgnoreLimits:${next}:${props.password}`)
}
</script>

<style scoped>
.card {
  display: grid;
  gap: 1rem;
  padding: 1.2rem;
  align-content: start;
  min-height: 34rem;
  border: 1px solid var(--border);
  border-radius: 1.6rem;
  background: var(--surface);
  box-shadow: var(--shadow);
}

.card-header,
.card-footer,
.stats,
.stats div,
.window-shell,
.control-stack {
  display: flex;
}

.card-footer {
  margin-top: auto;
  flex-direction: column;
  gap: 1rem;
}

.card-header,
.stats {
  justify-content: space-between;
  gap: 1rem;
}

.card-header {
  align-items: center;
}

h2 {
  margin: 0;
  font-size: 1.2rem;
}

.side-control,
.toggle,
.calibration {
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  cursor: pointer;
}

.toggle,
.calibration {
  border-radius: 999px;
  padding: 0.7rem 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.window-shell {
  display: grid;
  grid-template-columns: auto auto auto;
  grid-template-rows: auto auto auto;
  min-height: 24rem;
  justify-content: center;
  align-items: center;
  justify-items: center;
  column-gap: 0.85rem;
  row-gap: 0.6rem;
}

.control-stack {
  flex-direction: column;
  justify-content: center;
  gap: 0.65rem;
  align-self: center;
}

.window {
  display: grid;
  justify-items: center;
}

.left-controls {
  grid-column: 1;
  grid-row: 2;
}

.window {
  grid-column: 2;
  grid-row: 2;
}

.right-controls {
  grid-column: 3;
  grid-row: 2;
}

.top-calibration {
  grid-column: 2;
  grid-row: 1;
}

.bottom-calibration {
  grid-column: 2;
  grid-row: 3;
}

.side-control {
  width: 3.6rem;
  min-height: 3.6rem;
  border-radius: 1.2rem;
  display: grid;
  place-items: center;
  font-size: 1.2rem;
}

.side-control.stop {
  color: #fecaca;
}

.frame {
  position: relative;
  border: 0.95rem solid var(--frame);
  border-radius: 1.5rem;
  overflow: hidden;
  background: var(--window);
}

.icon {
  display: inline-block;
  line-height: 1;
}

.open-close-control .icon {
  transform: rotate(90deg);
}

.glass,
.blind,
.target {
  position: absolute;
  inset: 0;
  transform-origin: top;
}

.blind {
  z-index: 2;
  background: var(--blind);
  transition: transform 0.8s ease;
}

.target {
  z-index: 1;
  background: var(--target);
  animation: pulse 1s linear infinite alternate;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
}

.stats div {
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.05);
}

.stats dt {
  color: var(--muted);
  font-size: 0.82rem;
}

.stats dd {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.toggle.success {
  color: #b7f7d8;
}

.toggle.danger {
  color: #fecdd3;
}

.calibration.warning {
  color: #fde68a;
  border-color: rgba(251, 191, 36, 0.45);
  background: rgba(251, 191, 36, 0.12);
}

@keyframes pulse {
  from {
    opacity: 0.18;
  }

  to {
    opacity: 0.45;
  }
}

@media (max-width: 640px) {
  .card {
    min-height: 30rem;
  }

  .window-shell {
    min-height: 22rem;
    column-gap: 0.65rem;
  }

  .frame {
    width: min(11rem, 62vw) !important;
  }

  .side-control {
    min-height: 3.2rem;
  }
}
</style>
