<template>
  <b-container fluid>
    <h2>{{ name }}</h2>
    <b-row>
      <b-col class="my-auto controls">
        <b-button-group vertical>
          <b-button variant="primary" @click="up(0)" size="sm">
            Up
          </b-button>
          <b-button variant="dark" @click="stop(0)" size="sm">
            stop
          </b-button>
          <b-button variant="primary" @click="down(0)" size="sm">
            down
          </b-button>
        </b-button-group>
      </b-col>

      <b-col>
        <div
          class="window mt-3"
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
          <!-- <b-form-input
            type="range"
            :min="0"
            :max="limit"
            step="5000"
            class="handle"
            :style="{ height: `${height - 1}rem` }"
            :value="target"
            @change="setPosition($event)"
          /> -->
        </div>
      </b-col>

      <b-col class="my-auto controls">
        <b-button-group vertical>
          <b-button variant="dark" @click="openBlind(0)" size="sm">
            Open
          </b-button>
          <b-button variant="dark" @click="closeBlind(0)" size="sm">
            Close
          </b-button>
        </b-button-group>
      </b-col>
    </b-row>

    <div class="w-100 mt-3" v-if="settings">
      <b-button-group vertical>
        <b-button variant="danger" @click="setTopPosition()">
          Set top position
        </b-button>
        <b-button variant="danger" @click="setLimit()">
          Set bottom position
        </b-button>
        <b-button variant="danger" @click="setIgnoreLimits()">
          Ignore limits
        </b-button>
      </b-button-group>
    </div>
    <div class="w-100 mt-1">
      Current position: <b-badge>{{ position }}</b-badge>
    </div>
    <div class="w-100 mt-1">
      Target position: <b-badge>{{ target }}</b-badge>
    </div>
  </b-container>
</template>

<script>
import ws from '@/shared'
import sha256 from 'crypto-js/sha256'

export default {
  name: 'Window',
  props: {
    name: {
      type: String,
      default: 'Window'
    },
    width: {
      type: Number,
      default: 10
    },
    height: {
      type: Number,
      default: 10
    },
    motorId: {
      type: Number,
      default: 0
    },
    settings: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      position: 0,
      target: 0,
      limit: 0,
      ignoreLimits: 0,
      minMotorStep: 5000
    }
  },
  methods: {
    redraw(opts) {
      this.position = opts.position
      this.target = opts.target
      this.limit = opts.limit
      // this.ignoreLimits = opts.ignoreLimits

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
      const pass = document.getElementById('pass').value
      ws.send(`setTopPosition:${this.motorId}:${sha256(pass).toString()}`)
    },
    setLimit() {
      const pass = document.getElementById('pass').value
      ws.send(`setLimit:${this.motorId}:${sha256(pass).toString()}`)
    },
    setIgnoreLimits() {
      const pass = document.getElementById('pass').value
      ws.send(`setIgnoreLimits:${this.ignoreLimits}:${sha256(pass).toString()}`)
      this.ignoreLimits = this.ignoreLimits === 1 ? 0 : 1
    },
    setPosition(pos) {
      if (pos > this.position) {
        this.down(pos - this.position)
      } else if (pos < this.position) {
        this.up(this.position - pos)
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.window {
  position: relative;
  margin: 0 auto;
}

.frame {
  position: absolute;
  height: 100%;
  width: 100%;
  border: 1rem solid #5c5c5c;
  background-color: #d9f6ff;
  z-index: 1;
}

.blind {
  position: absolute;
  z-index: 10;
  height: 100%;
  width: 100%;
  background-color: #a8a6b9;
  background-repeat: repeat;
  border-bottom: none;
  transform: scaleY(0);
  transform-origin: top;
  transition: transform 1s;
}

.blind.pending {
  z-index: 10;
  background-color: #fbff1f;
  background-image: none;
  animation: blinker 2s linear infinite;
}

.controls {
  padding-left: 0;
  padding-right: 0;
}

.controls button {
  height: 4rem;
}

@keyframes blinker {
  0% {
    opacity: 0.9;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 0.9;
  }
}

.handle {
  width: 1rem;
  margin-top: 0.5rem;
  position: absolute;
  right: -1.5rem;
  z-index: 999;
  color: gray;
  border-radius: 30%;
  transform: rotate(180deg);
  cursor: pointer;
  -webkit-appearance: slider-vertical; /* WebKit */
}

input[type='range']::-webkit-slider-thumb {
  border: 1px solid #00001e;
  border-radius: 15px;
  cursor: pointer;
}

input[type='range']::-webkit-slider-runnable-track {
  background: rgba(0, 0, 0, 0);
  cursor: pointer;
}
</style>
