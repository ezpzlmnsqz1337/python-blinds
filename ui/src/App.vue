<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style lang="scss">
:root {
  --frame-color: #f8f9fa;
  --window-color: #007bff;
  --bg-color: #343a40;
  --window-color2: #17a2b8;
  --target-position-color: #ffc107;
  --blind-color: #6c757d;
}

#app {
  font-family: Inter, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #ffffff;
  background-color: var(--bg-color);
  height: 100vh;
}
</style>
