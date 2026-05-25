<template>
  <main class="page-shell">
    <section class="hero">
      <div class="status" :class="connected ? 'online' : 'offline'">
        <span class="dot"></span>
        {{
          connected ? 'Connected to controller' : 'Reconnecting to controller'
        }}
      </div>
    </section>

    <section class="tabs" aria-label="Blind selector">
      <template v-if="isCompactLayout">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="tab"
          :class="activeTab === tab.id ? 'active' : ''"
          @click="activeTab = tab.id"
        >
          {{ tab.title }}
        </button>
      </template>
      <button
        class="settings-pill"
        type="button"
        :aria-label="settingsEnabled ? 'Settings unlocked' : 'Unlock settings'"
        :title="settingsEnabled ? 'Settings unlocked' : 'Unlock settings'"
        @click="showLogin = true"
      >
        <span class="settings-icon" aria-hidden="true">⚙</span>
      </button>
    </section>

    <section class="cards">
      <BlindCard
        v-for="tab in visibleTabs"
        :key="tab.id"
        :title="tab.title"
        :motor-id="tab.id"
        :frame-width-rem="tab.frameWidthRem"
        :frame-aspect-ratio="tab.frameAspectRatio"
        :blind="socketState.blinds[tab.id]"
        :password="password"
        :settings-enabled="settingsEnabled"
        :send="send"
      />
    </section>

    <LoginModal
      :open="showLogin"
      @close="showLogin = false"
      @submit="unlockSettings"
    />
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import BlindCard from '@/components/BlindCard.vue'
import LoginModal from '@/components/LoginModal.vue'
import { useBlindsSocket } from '@/composables/useBlindsSocket'
import type { BlindTab } from '@/types'

const COMPACT_LAYOUT_WIDTH = 700

const tabs: BlindTab[] = [
  { id: 0, title: 'Balcony', frameWidthRem: 12, frameAspectRatio: 10 / 20 },
  { id: 1, title: 'Window', frameWidthRem: 12, frameAspectRatio: 10 / 11 }
]

const activeTab = ref(0)
const showLogin = ref(false)
const settingsEnabled = ref(false)
const password = ref('')
const isCompactLayout = ref(false)

const { state: socketState, connected, send } = useBlindsSocket()

const visibleTabs = computed(() =>
  isCompactLayout.value
    ? tabs.filter((tab) => tab.id === activeTab.value)
    : tabs
)

function updateLayoutMode(): void {
  isCompactLayout.value = window.innerWidth < COMPACT_LAYOUT_WIDTH
}

onMounted(() => {
  updateLayoutMode()
  window.addEventListener('resize', updateLayoutMode)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateLayoutMode)
})

function unlockSettings(nextPassword: string): void {
  password.value = nextPassword
  settingsEnabled.value = true
}
</script>

<style scoped>
.page-shell {
  min-height: 100vh;
  padding: 1rem 1.25rem 1.25rem;
  display: grid;
  gap: 0.85rem;
}

.hero,
.tabs,
.cards {
  display: flex;
}

.hero {
  justify-content: flex-end;
}

.status,
.tab,
.settings-pill {
  border: 1px solid var(--border);
  border-radius: 999px;
  backdrop-filter: blur(14px);
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.8rem 1rem;
  background: rgba(255, 255, 255, 0.06);
  white-space: nowrap;
}

.status.online {
  color: #b7f7d8;
}

.status.offline {
  color: #fecaca;
}

.status.offline .dot {
  animation: reconnect-pulse 1.2s ease-in-out infinite;
}

.dot {
  width: 0.7rem;
  height: 0.7rem;
  border-radius: 999px;
  background: currentColor;
  box-shadow: 0 0 0 0.4rem rgba(255, 255, 255, 0.08);
}

.tabs {
  gap: 0.7rem;
  flex-wrap: wrap;
  align-items: center;
  min-height: 3.5rem;
  width: 100%;
}

.tab,
.settings-pill {
  padding: 0.75rem 1rem;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
}

.settings-pill {
  margin-left: auto;
  width: 3rem;
  height: 3rem;
  padding: 0;
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
}

.settings-icon {
  display: inline-block;
  font-size: 1.2rem;
  line-height: 1;
}

.tab.active {
  background: linear-gradient(
    135deg,
    rgba(52, 211, 153, 0.18),
    rgba(16, 185, 129, 0.4)
  );
  border-color: rgba(52, 211, 153, 0.35);
}

.cards {
  gap: 1rem;
  flex-wrap: wrap;
}

.cards > * {
  flex: 1 1 min(100%, 32rem);
}

@keyframes reconnect-pulse {
  0% {
    transform: scale(0.9);
    opacity: 0.55;
    box-shadow: 0 0 0 0 rgba(254, 202, 202, 0.1);
  }

  70% {
    transform: scale(1.1);
    opacity: 1;
    box-shadow: 0 0 0 0.55rem rgba(254, 202, 202, 0.2);
  }

  100% {
    transform: scale(0.9);
    opacity: 0.55;
    box-shadow: 0 0 0 0 rgba(254, 202, 202, 0.1);
  }
}

@media (max-width: 899px) {
  .page-shell {
    padding: 0.85rem;
  }

  .hero {
    width: 100%;
    max-height: 3.5rem;
    align-items: flex-start;
  }

  .status {
    width: 100%;
    box-sizing: border-box;
  }

  .settings-pill {
    margin-left: auto;
  }
}
</style>
