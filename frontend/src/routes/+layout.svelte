<script lang="ts">
  import { page } from '$app/stores'
  import '../app.css'
  import Topbar from '$lib/components/topbar.svelte'
  import { log } from '$lib/logger'

  $effect(() => {
    const path = $page.url.pathname
    log('导航', { path })
  })
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


