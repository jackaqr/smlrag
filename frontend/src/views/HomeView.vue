<template>
  <div class="home">
    <div class="welcome-section">
      <h1>欢迎使用 Vue 3</h1>
      <p class="subtitle">这是一个基于 Vue 3 + TypeScript + Vite 的现代化前端框架</p>
    </div>

    <div class="features">
      <div class="feature-card">
        <h3>⚡️ Vite</h3>
        <p>极速的开发服务器和构建工具</p>
      </div>
      <div class="feature-card">
        <h3>🔷 Vue 3</h3>
        <p>渐进式 JavaScript 框架</p>
      </div>
      <div class="feature-card">
        <h3>📦 TypeScript</h3>
        <p>类型安全的 JavaScript 超集</p>
      </div>
      <div class="feature-card">
        <h3>🗂️ Vue Router</h3>
        <p>官方路由管理器</p>
      </div>
      <div class="feature-card">
        <h3>🍍 Pinia</h3>
        <p>现代化的状态管理库</p>
      </div>
    </div>

    <div class="counter-demo">
      <h2>状态管理示例 (Pinia)</h2>
      <div class="counter-container">
        <button @click="counterStore.decrement" class="btn btn-secondary">-</button>
        <span class="count">{{ counterStore.count }}</span>
        <button @click="counterStore.increment" class="btn btn-primary">+</button>
      </div>
      <p class="counter-info">双倍值: {{ counterStore.doubleCount }}</p>
      <button @click="counterStore.reset" class="btn btn-reset">重置</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCounterStore } from '@/stores/counter'

const counterStore = useCounterStore()
</script>

<style scoped>
.home {
  animation: fadeIn 0.5s;
}

.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-section h1 {
  font-size: 3rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.25rem;
  color: #7f8c8d;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.feature-card h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.feature-card p {
  margin: 0;
  color: #7f8c8d;
}

.counter-demo {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.counter-demo h2 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.counter-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.count {
  font-size: 2.5rem;
  font-weight: bold;
  color: #42b983;
  min-width: 80px;
}

.btn {
  padding: 0.75rem 1.5rem;
  font-size: 1.25rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.btn-primary {
  background-color: #42b983;
  color: white;
}

.btn-primary:hover {
  background-color: #35a372;
  transform: scale(1.05);
}

.btn-secondary {
  background-color: #e74c3c;
  color: white;
}

.btn-secondary:hover {
  background-color: #c0392b;
  transform: scale(1.05);
}

.btn-reset {
  background-color: #95a5a6;
  color: white;
  margin-top: 1rem;
}

.btn-reset:hover {
  background-color: #7f8c8d;
}

.counter-info {
  color: #7f8c8d;
  margin: 0.5rem 0;
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

