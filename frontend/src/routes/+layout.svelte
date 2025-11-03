<script lang="ts">
  import '../app.css'
  import Topbar from '$lib/components/topbar.svelte'
  import Sidebar from '$lib/components/Sidebar.svelte'
  import Chat from '$lib/components/Chat.svelte'
  import { currentView } from '$lib/stores/navigationStore'
</script>

<div class="app">
  <Topbar />
  <div class="main-content">
    {#if $currentView === 'chat'}
      <Sidebar />
      <Chat />
    {:else if $currentView === 'documents'}
      <div class="placeholder-view">
        <div class="placeholder-content">
          <span class="placeholder-icon">📚</span>
          <h2>文档管理</h2>
          <p>文档管理界面即将推出...</p>
        </div>
      </div>
    {:else if $currentView === 'analytics'}
      <div class="placeholder-view">
        <div class="placeholder-content">
          <span class="placeholder-icon">📊</span>
          <h2>数据分析</h2>
          <p>数据分析界面即将推出...</p>
        </div>
      </div>
    {:else if $currentView === 'settings'}
      <div class="placeholder-view">
        <div class="placeholder-content">
          <span class="placeholder-icon">⚙️</span>
          <h2>系统设置</h2>
          <p>设置界面即将推出...</p>
        </div>
      </div>
    {/if}
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
  
  .placeholder-view {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }
  
  .placeholder-content {
    text-align: center;
    color: rgba(255, 255, 255, 0.9);
    padding: 2rem;
  }
  
  .placeholder-icon {
    font-size: 5rem;
    display: block;
    margin-bottom: 1rem;
    animation: float 3s ease-in-out infinite;
  }
  
  @keyframes float {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-20px);
    }
  }
  
  .placeholder-content h2 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .placeholder-content p {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.6);
  }
</style>


