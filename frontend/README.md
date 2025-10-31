# Vue 3 前端框架

这是一个基于 Vue 3 + TypeScript + Vite 构建的现代化前端框架。

## 技术栈

- **Vue 3** - 采用 Composition API
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Vue Router** - 路由管理
- **Pinia** - 状态管理

## 项目结构

```
frontend/
├── public/          # 静态资源
├── src/
│   ├── assets/      # 资源文件（CSS、图片等）
│   ├── components/  # 可复用组件
│   ├── router/      # 路由配置
│   ├── stores/      # Pinia 状态管理
│   ├── views/       # 页面视图
│   ├── App.vue      # 根组件
│   └── main.ts      # 入口文件
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 安装依赖

```bash
npm install
# 或
pnpm install
# 或
yarn install
```

## 开发

启动开发服务器（默认在 http://localhost:3000）：

```bash
npm run dev
```

## 构建

构建生产版本：

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

## 预览

预览生产构建：

```bash
npm run preview
```

## 代码检查

运行 ESLint 检查：

```bash
npm run lint
```

## 功能特性

- ✅ Vue 3 Composition API
- ✅ TypeScript 支持
- ✅ Vue Router 路由管理
- ✅ Pinia 状态管理
- ✅ Vite 快速构建
- ✅ 路径别名 (@/ 指向 src/)
- ✅ API 代理配置
- ✅ 代码分割和懒加载

## 开发建议

1. 使用 `<script setup>` 语法编写组件
2. 遵循 TypeScript 类型规范
3. 组件放在 `src/components/` 目录
4. 页面视图放在 `src/views/` 目录
5. 使用 Pinia 进行状态管理
6. 路由配置在 `src/router/index.ts`

