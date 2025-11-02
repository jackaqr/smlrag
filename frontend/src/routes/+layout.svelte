<script lang="ts">
  import '../app.css'
  import Sidebar from '$lib/components/Sidebar.svelte'
  import Chat from '$lib/components/Chat.svelte'
</script>

<div class="app">
  <Sidebar />
  <Chat />
</div>

<style>
  .app {
    min-height: 100vh;
    display: flex;
    overflow: hidden;
  }
</style>


