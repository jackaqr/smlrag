<template>
  <div class="about">
    <h1>关于项目</h1>
    <div class="content">
      <section>
        <h2>技术栈</h2>
        <ul>
          <li><strong>Vue 3</strong> - 采用 Composition API 和 <code>&lt;script setup&gt;</code> 语法</li>
          <li><strong>TypeScript</strong> - 提供类型安全保障</li>
          <li><strong>Vite</strong> - 快速的构建工具和开发服务器</li>
          <li><strong>Vue Router</strong> - 官方路由管理器</li>
          <li><strong>Pinia</strong> - 下一代 Vue 状态管理库</li>
        </ul>
      </section>

      <section>
        <h2>项目结构</h2>
        <pre><code>frontend/
├── public/          # 静态资源
├── src/
│   ├── assets/      # 资源文件
│   ├── components/  # 组件
│   ├── router/      # 路由配置
│   ├── stores/      # Pinia 状态管理
│   ├── views/       # 页面视图
│   ├── App.vue      # 根组件
│   └── main.ts      # 入口文件
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts</code></pre>
      </section>

      <section>
        <h2>快速开始</h2>
        <ol>
          <li>安装依赖：<code>npm install</code> 或 <code>pnpm install</code></li>
          <li>启动开发服务器：<code>npm run dev</code></li>
          <li>构建生产版本：<code>npm run build</code></li>
          <li>预览生产构建：<code>npm run preview</code></li>
        </ol>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
// About 页面
</script>

<style scoped>
.about {
  animation: fadeIn 0.5s;
}

.about h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
}

.content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.content section {
  margin-bottom: 2rem;
}

.content section:last-child {
  margin-bottom: 0;
}

.content h2 {
  color: #42b983;
  margin-bottom: 1rem;
  border-bottom: 2px solid #42b983;
  padding-bottom: 0.5rem;
}

.content ul,
.content ol {
  line-height: 1.8;
  color: #2c3e50;
}

.content li {
  margin-bottom: 0.5rem;
}

.content code {
  background-color: #f4f4f4;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.content pre {
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}

.content pre code {
  background-color: transparent;
  color: inherit;
  padding: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

