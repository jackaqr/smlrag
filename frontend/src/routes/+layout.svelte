<script lang="ts">
  import '../app.css'
  import Topbar from '$lib/components/topbar.svelte'
</script>

<div class="app">
  <Topbar />
  <div class="main-content">
    <slot />
  </div>
</div>

<style>
  .app {
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .main-content {
    flex: 1;
    display: flex;
    overflow: hidden;
  }
</style>


