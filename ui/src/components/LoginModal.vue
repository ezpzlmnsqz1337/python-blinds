<template>
  <div v-if="open" class="overlay" @click.self="close">
    <div
      class="dialog"
      role="dialog"
      aria-modal="true"
      aria-labelledby="login-title"
    >
      <div class="header">
        <div>
          <p class="eyebrow">Settings</p>
          <h2 id="login-title">Unlock calibration</h2>
        </div>
        <button class="ghost" type="button" @click="close">Close</button>
      </div>

      <form class="body" @submit.prevent="submit">
        <label class="label" for="password">Password hash input</label>
        <input
          id="password"
          ref="passwordInput"
          v-model="password"
          class="input"
          type="password"
          placeholder="Enter password"
        />

        <div class="actions">
          <button class="ghost" type="button" @click="close">Cancel</button>
          <button class="primary" type="submit">Unlock</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import sha256 from 'crypto-js/sha256'
import { nextTick, ref, watch } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close', 'submit'])

const password = ref('')
const passwordInput = ref<HTMLInputElement | null>(null)

watch(
  () => props.open,
  async (isOpen) => {
    if (!isOpen) {
      password.value = ''
      return
    }

    await nextTick()
    passwordInput.value?.focus()
  }
)

function close() {
  emit('close')
}

function submit() {
  emit('submit', sha256(password.value).toString())
  emit('close')
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(2, 6, 23, 0.74);
  backdrop-filter: blur(14px);
  padding: 1.25rem;
  z-index: 20;
}

.dialog {
  width: min(100%, 26rem);
  border: 1px solid var(--border);
  border-radius: 1.5rem;
  background: var(--surface-strong);
  box-shadow: var(--shadow);
}

.header,
.body,
.actions {
  display: flex;
}

.header {
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.25rem 0;
}

.eyebrow {
  margin: 0 0 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.72rem;
  color: var(--muted);
}

h2 {
  margin: 0;
  font-size: 1.25rem;
}

.body {
  flex-direction: column;
  gap: 0.9rem;
  padding: 1.25rem;
}

.label {
  color: var(--muted);
  font-size: 0.95rem;
}

.input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 0.9rem;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text);
  padding: 0.85rem 1rem;
}

.actions {
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.primary,
.ghost {
  border-radius: 999px;
  border: 1px solid var(--border);
  padding: 0.72rem 1rem;
  cursor: pointer;
}

.primary {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #052e25;
  border-color: transparent;
  font-weight: 700;
}

.ghost {
  background: transparent;
  color: var(--text);
}
</style>
