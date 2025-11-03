<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  
  // 根路径重定向到 /chat
  onMount(() => {
    goto('/chat', { replaceState: true });
  });
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
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: rgba(255, 255, 255, 0.7);
  }
</style>
