<template>
  <router-view />
</template>

<style>
:root {
  --surface: rgba(16, 24, 38, 0.82);
  --surface-strong: rgba(10, 15, 25, 0.92);
  --surface-soft: rgba(255, 255, 255, 0.08);
  --border: rgba(255, 255, 255, 0.14);
  --text: #f8fafc;
  --muted: #bfd0df;
  --accent: #34d399;
  --accent-strong: #10b981;
  --warning: #fbbf24;
  --danger: #fb7185;
  --window: linear-gradient(180deg, #9ad7ff 0%, #66b8f7 100%);
  --blind: linear-gradient(180deg, #d5dbe3 0%, #9ba7b4 100%);
  --target: rgba(251, 191, 36, 0.52);
  --frame: #f7fafc;
  --shadow: 0 24px 60px rgba(0, 0, 0, 0.32);
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
  color: var(--text);
  background:
    radial-gradient(
      circle at top left,
      rgba(52, 211, 153, 0.16),
      transparent 28%
    ),
    radial-gradient(
      circle at top right,
      rgba(59, 130, 246, 0.18),
      transparent 26%
    ),
    linear-gradient(180deg, #0f172a 0%, #111827 44%, #1f2937 100%);
}

* {
  box-sizing: border-box;
}

html,
body,
#app {
  margin: 0;
  min-height: 100%;
}

body {
  min-height: 100vh;
}

button,
input {
  font: inherit;
}
</style>
