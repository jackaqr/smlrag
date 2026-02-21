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
    background: var(--gradient-hero);
  }

  .main-content {
    flex: 1;
    display: flex;
    overflow: hidden;
    background: var(--bg-surface);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    box-shadow: var(--shadow-md);
  }
</style>


