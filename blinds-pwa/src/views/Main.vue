<template>
  <b-container fluid class="text-center my-auto" style="height: 100%">
    <h1>Blinds control</h1>
    <b-tabs pills align="center" content-class="mt-3" class="mt-3" small>
      <!-- Text slides with image -->
      <b-tab title="Balcony">
        <b-row>
          <b-col class="text-center">
            <Window
              ref="balcony"
              name="Balcony"
              :width="10"
              :height="20"
              :motorId="0"
              :settings="pass.length > 5"
            />
          </b-col>
        </b-row>
      </b-tab>

      <!-- Slides with custom text -->
      <b-tab title="Window">
        <b-row>
          <b-col class="text-center">
            <Window
              ref="window"
              name="Window"
              :width="10"
              :height="11"
              :motorId="1"
              :settings="pass.length > 5"
            />
          </b-col>
        </b-row>
      </b-tab>
      <b-tab title="Login">
        <b-row>
          <b-col mt="5">
            <div class="form-group">
              <label for="pass">Password for calibration</label>
              <b-form-input
                type="password"
                placeholder="Enter password..."
                v-model="pass"
                id="pass"
              />
            </div>
          </b-col>
        </b-row>
      </b-tab>
    </b-tabs>
  </b-container>
</template>

<script>
import ws from '@/shared'
import Window from '@/components/Window'

export default {
  name: 'Main',
  components: {
    Window
  },
  data() {
    return {
      ignoreLimits: 0,
      pass: '',
      slide: 0,
      sliding: null
    }
  },
  created() {
    ws.onopen = () => {
      ws.send('getBlindsPosition')
    }

    ws.onmessage = event => {
      console.log('Response from server: ', event.data)
      if (event.data.includes('blindsPosition')) {
        const motorId = parseInt(event.data.split(':')[2])
        const position = parseInt(event.data.split(':')[4])
        const target = parseInt(event.data.split(':')[6])
        const limit = parseInt(event.data.split(':')[8])
        const ignoreLimits = parseInt(event.data.split(':')[10])
        const imageElementId = motorId === 0 ? 'balcony' : 'window'

        this.$refs[imageElementId].redraw({
          position,
          target,
          limit,
          ignoreLimits
        })
      }
    }
  },
  methods: {
    onSlideStart(slide) {
      console.log(slide)
      this.sliding = true
    },
    onSlideEnd(slide) {
      console.log(slide)
      this.sliding = false
    }
  }
}
</script>

<style></style>
