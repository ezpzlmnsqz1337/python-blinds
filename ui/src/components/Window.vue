<template>
  <b-container fluid>
    <b-row>
      <b-col class="my-auto controls">
        <b-button-group vertical>
          <b-button variant="light" @click="up()" size="sm">
            <b-icon icon="chevron-up"></b-icon>
          </b-button>
          <b-button
            :variant="target == position ? 'light' : 'danger'"
            @click="stop()"
            size="sm"
            :disabled="target == position"
          >
            <b-icon icon="stop-fill"></b-icon>
          </b-button>
          <b-button variant="light" @click="down()" size="sm">
            <b-icon icon="chevron-down"></b-icon>
          </b-button>
        </b-button-group>
      </b-col>

      <b-col>
        <b-button
          size="sm"
          variant="warning"
          @click="setTopPosition()"
          v-if="settings"
        >
          <b-icon icon="align-top"></b-icon> SET TOP
        </b-button>
        <div
          class="window my-3"
          :style="{ width: `${width}rem`, height: `${height}rem` }"
        >
          <div class="frame">
            <div class="blind" ref="window"></div>
            <div
              v-show="target != position"
              class="blind pending"
              ref="windowTarget"
            ></div>
          </div>
        </div>
        <b-button
          size="sm"
          variant="warning"
          @click="setLimit()"
          v-if="settings"
        >
          <b-icon icon="align-bottom"></b-icon> SET BOTTOM
        </b-button>
      </b-col>

      <b-col class="my-auto controls">
        <b-button-group vertical>
          <b-button variant="light" @click="openBlind(0)" size="sm">
            <b-icon icon="chevron-bar-up"></b-icon>
          </b-button>
          <div class="spacer"></div>
          <b-button variant="light" @click="closeBlind(0)" size="sm">
            <b-icon icon="chevron-bar-down"></b-icon>
          </b-button>
        </b-button-group>
      </b-col>
    </b-row>

    <div class="w-100 mt-2" v-if="settings">
      Position: <b-badge>{{ position }}</b-badge>
    </div>
    <div class="w-100 mt-1" v-if="settings">
      Target: <b-badge>{{ target }}</b-badge>
    </div>

    <div class="w-100 mt-2">
      <b-button
        v-if="settings"
        :variant="ignoreLimits != 0 ? 'danger' : 'success'"
        @click="setIgnoreLimits()"
        size="sm"
      >
        <b-icon :icon="ignoreLimits != 0 ? 'check-square' : 'square'"></b-icon>
        Ignore limits
      </b-button>
    </div>

    <div class="w-100 mt-3">
      <b-button variant="light" @click="openLogin()" size="sm">
        <b-icon icon="gear-fill"></b-icon> Settings
      </b-button>
    </div>
  </b-container>
</template>

<script>
import ws from '@/shared'

export default {
  name: 'Window',
  props: {
    name: {
      type: String,
      default: 'Window',
    },
    width: {
      type: Number,
      default: 10,
    },
    height: {
      type: Number,
      default: 10,
    },
    motorId: {
      type: Number,
      default: 0,
    },
    settings: {
      type: Boolean,
      default: false,
    },
    password: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      position: 0,
      target: 0,
      limit: 0,
      ignoreLimits: 0,
      minMotorStep: 5000,
    }
  },
  methods: {
    redraw(opts) {
      this.position = opts.position
      this.target = opts.target
      this.limit = opts.limit
      this.ignoreLimits = opts.ignoreLimits

      let scale = Math.fround(this.position / this.limit)
      if (scale > 1) scale = 1
      if (scale < 0) scale = 0

      let scaleTarget = Math.fround(this.target / this.limit)
      if (scale > 1) scale = 1
      if (scale < 0) scale = 0

      this.$refs.window.style.transform = `scaleY(${scale})`
      this.$refs.windowTarget.style.transform = `scaleY(${scaleTarget})`
    },
    up(numOfSteps) {
      const steps = numOfSteps || this.minMotorStep
      ws.send(`up:${this.motorId}:${steps}`)
    },
    down(numOfSteps) {
      const steps = numOfSteps || this.minMotorStep
      ws.send(`down:${this.motorId}:${steps}`)
    },
    stop() {
      ws.send(`stop:${this.motorId}`)
    },
    openBlind() {
      ws.send(`openBlind:${this.motorId}`)
    },
    closeBlind() {
      ws.send(`closeBlind:${this.motorId}`)
    },
    setTopPosition() {
      ws.send(`setTopPosition:${this.motorId}:${this.password}`)
    },
    setLimit() {
      ws.send(`setLimit:${this.motorId}:${this.password}`)
    },
    setIgnoreLimits() {
      this.ignoreLimits = this.ignoreLimits === 1 ? 0 : 1
      ws.send(`setIgnoreLimits:${this.ignoreLimits}:${this.password}`)
    },
    setPosition(pos) {
      if (pos > this.position) {
        this.down(pos - this.position)
      } else if (pos < this.position) {
        this.up(this.position - pos)
      }
    },
    openLogin() {
      this.$bvModal.show('login')
    },
  },
}
</script>

<style scoped lang="scss">
.window {
  position: relative;
  margin: 0 auto;
}

.frame {
  position: absolute;
  height: 100%;
  width: 100%;
  border: 1rem solid var(--frame-color);
  background-color: var(--window-color2);
  z-index: 1;
}

.blind {
  position: absolute;
  z-index: 10;
  height: 100%;
  width: 100%;
  background-color: var(--blind-color);
  background-repeat: repeat;
  border-bottom: none;
  transform: scaleY(0);
  transform-origin: top;
  transition: transform 1s;
}

.blind.pending {
  z-index: 10;
  background-color: var(--target-position-color);
  background-image: none;
  animation: blinker 1s linear infinite;
}

.controls {
  padding-left: 0;
  padding-right: 0;
}

.controls button {
  height: 4rem;
  width: 3rem;
}

.spacer {
  border-bottom: 2px solid var(--bg-color);
}

@keyframes blinker {
  0% {
    opacity: 0.2;
  }
  100% {
    opacity: 0.1;
  }
}
</style>
