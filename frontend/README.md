# Svelte 5 + SvelteKit 前端项目

基于 Svelte 5 和 SvelteKit 的现代化前端应用，使用文件系统路由。

## 🚀 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器（端口 3001）
npm run dev
```

访问：http://localhost:3001

## 📋 其他命令

```bash
npm run build          # 构建生产版本
npm run preview        # 预览构建结果
npm run check          # TypeScript 类型检查

# Docker 部署
docker-compose up -d   # 启动容器
docker-compose down    # 停止容器
```

## 📁 项目结构

```
fesvelte/
├── src/
│   ├── routes/                # 路由层（仅负责路由转发）
│   │   ├── +layout.svelte    # 全局布局（导航栏）
│   │   ├── +page.svelte      # 首页路由 (/) → 渲染 HomePage
│   │   └── about/
│   │       └── +page.svelte  # 关于页路由 (/about) → 渲染 AboutPage
│   ├── lib/
│   │   ├── pages/            # 页面组件（实际页面内容）
│   │   │   ├── HomePage.svelte
│   │   │   └── AboutPage.svelte
│   │   └── components/       # 可复用组件
│   │       └── Counter.svelte
│   ├── app.css               # 全局样式
│   └── app.html              # HTML 模板
├── package.json
├── svelte.config.js          # SvelteKit 配置
├── vite.config.ts            # Vite 配置
└── Dockerfile
```

### 📂 架构说明

**分层设计 - 路由与页面分离：**

- **`routes/`** - 路由层，只负责路由定义和转发
  - 文件很简洁，只导入并渲染对应的页面组件
  - 利用 SvelteKit 的文件系统路由
  
- **`lib/pages/`** - 页面层，实现具体的页面内容
  - 包含完整的页面逻辑、样式和组件
  - 可以被路由层或其他地方复用
  
- **`lib/components/`** - 组件层，可复用的 UI 组件
  - 通用组件，可在多个页面中使用

## 🗂️ 文件系统路由

SvelteKit 使用文件系统路由，routes 负责转发，pages 负责实现。

### 添加新页面（推荐流程）

**步骤 1：创建页面组件**
```svelte
<!-- src/lib/pages/ContactPage.svelte -->
<script lang="ts">
  let email = $state('contact@example.com')
</script>

<svelte:head>
  <title>联系我们</title>
</svelte:head>

<div>
  <h1>联系我们</h1>
  <p>邮箱：{email}</p>
</div>

<style>
  h1 { color: #ff3e00; }
</style>
```

**步骤 2：创建路由（仅做转发）**
```svelte
<!-- src/routes/contact/+page.svelte -->
<script lang="ts">
  import ContactPage from '$lib/pages/ContactPage.svelte'
</script>

<ContactPage />
```

**完成！** 访问 `/contact` 即可看到页面。

### 使用 goto 进行导航

```svelte
<script lang="ts">
  import { goto } from '$app/navigation'
</script>

<button onclick={() => goto('/about')}>
  前往关于页
</button>
```

## 🎯 Svelte 5 核心语法

### 响应式状态
```svelte
<script lang="ts">
  let count = $state(0)           // 响应式变量
  let doubled = $derived(count * 2)  // 计算属性
  
  $effect(() => {
    console.log('count:', count)   // 副作用
  })
</script>

<button onclick={() => count++}>
  点击: {count} (双倍: {doubled})
</button>
```

### 组件传值
```svelte
<!-- 父组件 -->
<Child name="张三" age={25} />

<!-- 子组件 -->
<script lang="ts">
  let { name, age } = $props()
</script>
<p>{name} 今年 {age} 岁</p>
```

### 页面标题和 Meta
```svelte
<svelte:head>
  <title>页面标题</title>
  <meta name="description" content="页面描述" />
</svelte:head>
```

## ⚙️ 配置

### API 代理
`vite.config.ts` 中配置了 API 代理：
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

### 端口修改
修改 `vite.config.ts` 中的 `server.port`

### 静态导出
项目使用 `adapter-static`，构建后生成纯静态文件，可部署到任何静态服务器

## 📚 参考文档

- [SvelteKit 文档](https://kit.svelte.dev/)
- [Svelte 5 文档](https://svelte.dev/)
- [Svelte 5 Runes](https://svelte-5-preview.vercel.app/docs/runes)
