<script lang="ts">
  // 未来可以添加统计数据的 API 调用
</script>

<div class="analytics-page">
  <div class="content">
    <span class="icon">📊</span>
    <h1>数据分析</h1>
    <p class="subtitle">查看对话统计和使用分析</p>
    
    <div class="placeholder">
      <p>数据分析功能即将推出...</p>
      <p class="hint">将展示：</p>
      <ul>
        <li>对话数量统计</li>
        <li>消息发送趋势</li>
        <li>知识库使用情况</li>
        <li>用户活跃度分析</li>
      </ul>
    </div>
  </div>
</div>

<style>
  .analytics-page {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-surface);
  }
  
  .content {
    text-align: center;
    color: var(--text-primary);
    padding: 2rem;
    max-width: 600px;
  }
  
  .icon {
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
  
  h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    background: var(--gradient-accent);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: 2rem;
  }
  
  .placeholder {
    background: var(--color-primary-muted);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 2rem;
    margin-top: 2rem;
  }
  
  .placeholder p {
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }
  
  .hint {
    color: var(--text-secondary);
    font-size: 1rem;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
  }
  
  ul {
    text-align: left;
    display: inline-block;
    list-style: none;
    padding: 0;
  }
  
  li {
    padding: 0.5rem 0;
    padding-left: 1.5rem;
    position: relative;
    color: var(--text-primary);
  }
  
  li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: var(--color-primary);
  }
</style>

