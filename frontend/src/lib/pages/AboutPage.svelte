<script lang="ts">
  let features = [
    'Svelte 5 最新特性',
    'SvelteKit 文件路由',
    'TypeScript 支持',
    'Vite 构建工具',
    'Docker 支持',
    '响应式设计'
  ]
</script>

<svelte:head>
  <title>关于 - Svelte 5 App</title>
</svelte:head>

<div class="about">
  <h1>关于项目</h1>
  
  <section class="section">
    <h2>📦 项目简介</h2>
    <p>
      这是一个基于 Svelte 5 和 SvelteKit 的前端项目，使用最新的 Runes API 和文件系统路由，
      提供现代化的开发体验和极致的运行性能。
    </p>
  </section>

  <section class="section">
    <h2>✨ 主要特性</h2>
    <ul class="feature-list">
      {#each features as feature}
        <li>{feature}</li>
      {/each}
    </ul>
  </section>

  <section class="section">
    <h2>🛠️ 技术栈</h2>
    <div class="tech-stack">
      <span class="tech-badge">Svelte 5</span>
      <span class="tech-badge">SvelteKit</span>
      <span class="tech-badge">TypeScript</span>
      <span class="tech-badge">Vite</span>
      <span class="tech-badge">Docker</span>
    </div>
  </section>

  <section class="section">
    <h2>📚 快速开始</h2>
    <div class="code-block">
      <pre><code>npm install
npm run dev</code></pre>
    </div>
  </section>
</div>

<style>
  .about {
    padding: 2rem 0;
  }

  h1 {
    color: #ff3e00;
    margin-bottom: 2rem;
  }

  .section {
    margin-bottom: 3rem;
  }

  .section h2 {
    margin-bottom: 1rem;
    font-size: 1.5rem;
  }

  .section p {
    line-height: 1.8;
    opacity: 0.9;
    font-size: 1.1rem;
  }

  .feature-list {
    list-style: none;
    padding: 0;
  }

  .feature-list li {
    padding: 0.8rem 0;
    padding-left: 2rem;
    position: relative;
    font-size: 1.1rem;
  }

  .feature-list li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: #ff3e00;
    font-weight: bold;
  }

  .tech-stack {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .tech-badge {
    padding: 0.5rem 1rem;
    background: rgba(255, 62, 0, 0.1);
    border: 1px solid #ff3e00;
    border-radius: 20px;
    font-weight: 500;
    color: #ff3e00;
  }

  .code-block {
    background: #1a1a1a;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .code-block pre {
    margin: 0;
    font-family: 'Courier New', monospace;
  }

  .code-block code {
    color: #a9dc76;
  }
</style>


