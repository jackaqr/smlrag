<script lang="ts">
  import '../app.css'
</script>

<div class="app">
  <slot />
</div>

<style>
  .app {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }
</style>


