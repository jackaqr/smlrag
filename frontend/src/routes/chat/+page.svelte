<script lang="ts">
  import Sidebar from '$lib/components/Sidebar.svelte'
  import Chat from '$lib/components/Chat.svelte'
</script>

<div class="chat-page">
  <Sidebar />
  <Chat />
</div>

<style>
  .chat-page {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
</style>

