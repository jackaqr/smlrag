<script lang="ts">
  import Counter from '$lib/components/Counter.svelte'
  
  let message = $state('欢迎使用 Svelte 5 + SvelteKit！')
</script>

<svelte:head>
  <title>首页 - Svelte 5 App</title>
</svelte:head>

<div class="home">
  <h1>Svelte 5 首页</h1>
  <p class="intro">{message}</p>
  
  <div class="features">
    <div class="feature-card">
      <h3>⚡ 极致性能</h3>
      <p>Svelte 编译时优化，无虚拟 DOM，运行时体积小</p>
    </div>
    
    <div class="feature-card">
      <h3>🎯 简洁语法</h3>
      <p>使用 Runes 实现响应式，代码更简洁直观</p>
    </div>
    
    <div class="feature-card">
      <h3>🚀 文件路由</h3>
      <p>SvelteKit 文件系统路由，开发更高效</p>
    </div>
  </div>

  <div class="demo">
    <h2>计数器示例</h2>
    <Counter />
  </div>
</div>

<style>
  .home {
    padding: 2rem 0;
  }

  h1 {
    color: #ff3e00;
    margin-bottom: 1rem;
  }

  .intro {
    font-size: 1.2rem;
    margin-bottom: 3rem;
    opacity: 0.9;
  }

  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
  }

  .feature-card {
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s, border-color 0.3s;
  }

  .feature-card:hover {
    transform: translateY(-4px);
    border-color: #ff3e00;
  }

  .feature-card h3 {
    margin-bottom: 0.5rem;
    font-size: 1.3rem;
  }

  .feature-card p {
    opacity: 0.8;
    line-height: 1.6;
  }

  .demo {
    margin-top: 3rem;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
  }

  .demo h2 {
    margin-bottom: 1.5rem;
  }
</style>

