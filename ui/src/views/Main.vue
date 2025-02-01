<template>
  <b-container fluid class="text-center my-auto">
    <b-row class="connection" :class="connected ? 'success' : 'danger'">
      <b-col>
        {{ connected ? 'Connected' : 'Not connected' }}
      </b-col>
    </b-row>

    <h2 class="pt-2">Rolety</h2>

    <b-tabs
      pills
      align="center"
      content-class="mt-3"
      class="mt-2"
      small
      nav-class="text-light"
      active-nav-item-class="font-weight-bold text-uppercase bg-info"
    >
      <b-tab title="Balcony">
        <b-row>
          <b-col class="text-center">
            <Window
              ref="balcony"
              name="Balcony"
              :width="10"
              :height="20"
              :motorId="0"
              :password="password"
              :settings="isAuthenticated"
            />
          </b-col>
        </b-row>
      </b-tab>

      <b-tab title="Window">
        <b-row>
          <b-col class="text-center">
            <Window
              ref="window"
              name="Window"
              :width="10"
              :height="11"
              :motorId="1"
              :password="password"
              :settings="isAuthenticated"
            />
          </b-col>
        </b-row>
      </b-tab>
    </b-tabs>
    <LoginModal @login:ok="authenticate($event)" />
  </b-container>
</template>

<script>
import ws from '@/shared'
import Window from '@/components/Window'
import LoginModal from '@/components/LoginModal'

export default {
  name: 'Main',
  components: {
    Window,
    LoginModal
  },
  data() {
    return {
      ignoreLimits: 0,
      isAuthenticated: false,
      password: '',
      connected: false
    }
  },
  created() {
    ws.onopen = () => {
      this.connected = true
    }

    ws.onmessage = event => {
      // console.log('Response from server: ', event.data)
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

    ws.onclose = () => {
      this.connected = false
    }
  },
  methods: {
    authenticate(password) {
      this.isAuthenticated = true
      this.password = password
    }
  }
}
</script>

<style>
.connection {
  text-transform: uppercase;
}

.connection.success {
  background-color: #28a745;
}

.connection.danger {
  background-color: #dc3545;
}

.nav-pills .nav-item a {
  color: #ffffff;
}
</style>
