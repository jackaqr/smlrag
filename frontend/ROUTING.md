# 路由架构说明

## 📁 路由结构

项目采用 **SvelteKit 的文件系统路由**，每个页面对应一个独立的路由文件。

```
src/routes/
├── +layout.svelte          # 全局布局（包含 Topbar）
├── +page.svelte            # 根路径 / （自动重定向到 /chat）
├── chat/
│   └── +page.svelte       # /chat - 对话界面
├── documents/
│   └── +page.svelte       # /documents - 文档管理
├── analytics/
│   └── +page.svelte       # /analytics - 数据分析
└── settings/
    └── +page.svelte       # /settings - 系统设置
```

## 🎯 路由说明

### 根路径 `/`
- 自动重定向到 `/chat`
- 用户访问首页时会立即跳转到对话页面

### `/chat` - 对话界面
- 包含侧边栏（Sidebar）和聊天区域（Chat）
- 完整的对话管理功能
- 消息发送和历史记录

### `/documents` - 文档管理
- 文件扫描和上传功能
- 调用 `POST /api/scan` 接口
- 需要配置 Dify API 凭证

### `/analytics` - 数据分析
- 占位页面（待开发）
- 未来展示统计数据和分析图表

### `/settings` - 系统设置
- 占位页面（待开发）
- 未来包含主题、语言等设置

## 🧭 导航实现

### Topbar 导航栏

使用 `<a>` 标签实现路由跳转：

```svelte
<a href="/chat" class="nav-btn" class:active={isActive('/chat')}>
  <span class="nav-icon">💬</span>
  <span class="nav-label">对话</span>
</a>
```

### 激活状态

通过 `$page.url.pathname` 判断当前路由：

```typescript
import { page } from '$app/stores';

function isActive(href: string): boolean {
  return $page.url.pathname === href;
}
```

## 🎨 布局层次

```
+layout.svelte
  ├── Topbar（固定顶部）
  └── <slot />（页面内容插槽）
      ├── /chat → chat/+page.svelte
      ├── /documents → documents/+page.svelte
      ├── /analytics → analytics/+page.svelte
      └── /settings → settings/+page.svelte
```

## 🚀 优势

1. **清晰的代码组织** - 每个页面独立文件，职责明确
2. **更好的性能** - SvelteKit 自动代码分割，按需加载
3. **标准路由** - 支持浏览器前进/后退，可以分享 URL
4. **易于扩展** - 新增页面只需创建新的路由文件
5. **类型安全** - TypeScript 支持路由参数类型检查

## 📝 添加新路由

创建新路由非常简单：

1. 在 `src/routes/` 下创建新目录
2. 添加 `+page.svelte` 文件
3. 在 `topbar.svelte` 中添加导航项

例如，添加 `/profile` 页面：

```bash
mkdir src/routes/profile
```

```svelte
<!-- src/routes/profile/+page.svelte -->
<div class="profile-page">
  <h1>用户资料</h1>
</div>
```

```typescript
// topbar.svelte 中添加
const navItems = [
  // ... 其他导航项
  { href: '/profile', label: '资料', icon: '👤' }
];
```

## 🔗 相关文档

- [SvelteKit 路由文档](https://kit.svelte.dev/docs/routing)
- [SvelteKit 导航文档](https://kit.svelte.dev/docs/modules#$app-navigation)

