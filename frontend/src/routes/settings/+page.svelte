<script lang="ts">
  // 未来可以添加设置相关的功能
</script>

<div class="settings-page">
  <div class="content">
    <span class="icon">⚙️</span>
    <h1>系统设置</h1>
    <p class="subtitle">配置系统参数和偏好</p>
    
    <div class="placeholder">
      <p>系统设置功能即将推出...</p>
      <p class="hint">将包含：</p>
      <ul>
        <li>主题设置（明暗模式）</li>
        <li>语言切换</li>
        <li>通知设置</li>
        <li>API 配置</li>
        <li>用户偏好</li>
      </ul>
    </div>
  </div>
</div>

<style>
  .settings-page {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }
  
  .content {
    text-align: center;
    color: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    max-width: 600px;
  }
  
  .icon {
    font-size: 5rem;
    display: block;
    margin-bottom: 1rem;
    animation: spin 10s linear infinite;
  }
  
  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  
  h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .subtitle {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 2rem;
  }
  
  .placeholder {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 2rem;
    margin-top: 2rem;
  }
  
  .placeholder p {
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }
  
  .hint {
    color: rgba(255, 255, 255, 0.7);
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
    color: rgba(255, 255, 255, 0.8);
  }
  
  li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: #667eea;
  }
</style>

