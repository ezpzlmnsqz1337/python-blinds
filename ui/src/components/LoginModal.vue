<template>
  <b-modal
    id="login"
    title="Login"
    centered
    @shown="focusPassInput"
    body-bg-variant="dark"
    header-bg-variant="dark"
    footer-bg-variant="dark"
    header-text-variant="light"
    body-text-variant="light"
    footer-text-variant="light"
    header-border-variant="dark"
    footer-border-variant="dark"
    hide-header-close
    @ok="onOk()"
  >
    <div class="form-group">
      <label for="pass">Enter password to show settings</label>
      <b-form-input
        type="password"
        placeholder="Enter password..."
        v-model="pass"
        id="pass"
        ref="passInput"
      />
    </div>
  </b-modal>
</template>

<script>
import sha256 from 'crypto-js/sha256'

export default {
  data() {
    return {
      pass: ''
    }
  },
  created() {
    window.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        this.$bvModal.hide('login')
      }
      if (e.key === 'Enter') {
        this.onOk()
        this.$bvModal.hide('login')
      }
    })
  },
  methods: {
    focusPassInput() {
      this.$refs.passInput.focus()
    },
    onOk() {
      this.$emit('login:ok', sha256(this.pass).toString())
    }
  }
}
</script>

<style></style>
