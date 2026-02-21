<script lang="ts">
  import { goto } from '$app/navigation'
  import { onMount } from 'svelte'
  import { log } from '$lib/logger'

  onMount(() => {
    log('首页重定向', { to: '/chat' })
    goto('/chat', { replaceState: true })
  })
</script>

<div class="redirect-page">
  <p>正在跳转到对话页面...</p>
</div>

<style>
  .redirect-page {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-surface);
    color: var(--text-muted);
  }
</style>
