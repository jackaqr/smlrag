<script lang="ts">
  import { scanFiles } from '$lib/api/dataset'
  
  let scanning = $state(false)
  let result = $state<string>('')
  let error = $state<string>('')
  
  async function handleScan() {
    scanning = true
    error = ''
    result = ''
    
    try {
      const response = await scanFiles()
      result = `扫描完成！处理了 ${response.files_processed} 个文件`
    } catch (err) {
      error = err instanceof Error ? err.message : '扫描失败'
    } finally {
      scanning = false
    }
  }
</script>

<div class="documents-page">
  <div class="content">
    <div class="header">
      <span class="icon">📚</span>
      <h1>文档管理</h1>
      <p class="subtitle">扫描并上传文件到知识库</p>
    </div>
    
    <div class="actions">
      <button 
        class="scan-btn" 
        onclick={handleScan}
        disabled={scanning}
      >
        {#if scanning}
          <span class="spinner">⏳</span>
          扫描中...
        {:else}
          <span class="btn-icon">🔍</span>
          开始扫描
        {/if}
      </button>
    </div>
    
    {#if result}
      <div class="result success">
        <span class="result-icon">✅</span>
        {result}
      </div>
    {/if}
    
    {#if error}
      <div class="result error">
        <span class="result-icon">❌</span>
        {error}
      </div>
    {/if}
    
    <div class="info-card">
      <h3>使用说明</h3>
      <ul>
        <li>将待扫描的文件放入 <code>backend/data</code> 目录</li>
        <li>确保已配置环境变量 <code>DIFY_BASE_URL</code> 和 <code>DIFY_API_KEY</code></li>
        <li>点击"开始扫描"按钮触发文件上传</li>
        <li>系统会自动将所有文件上传到 Dify 知识库</li>
      </ul>
    </div>
  </div>
</div>

<style>
  .documents-page {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    overflow: auto;
  }
  
  .content {
    max-width: 600px;
    width: 100%;
    padding: 2rem;
  }
  
  .header {
    text-align: center;
    margin-bottom: 2rem;
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
  }
  
  .actions {
    display: flex;
    justify-content: center;
    margin-bottom: 2rem;
  }
  
  .scan-btn {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 2rem;
    font-size: 1.1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }
  
  .scan-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  }
  
  .scan-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .btn-icon, .spinner {
    font-size: 1.3rem;
  }
  
  .spinner {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  
  .result {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-size: 1rem;
  }
  
  .result.success {
    background: rgba(76, 175, 80, 0.2);
    border: 1px solid rgba(76, 175, 80, 0.4);
    color: #4caf50;
  }
  
  .result.error {
    background: rgba(244, 67, 54, 0.2);
    border: 1px solid rgba(244, 67, 54, 0.4);
    color: #f44336;
  }
  
  .result-icon {
    font-size: 1.5rem;
  }
  
  .info-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    color: rgba(255, 255, 255, 0.9);
  }
  
  .info-card h3 {
    font-size: 1.3rem;
    margin-bottom: 1rem;
    color: #4ecdc4;
  }
  
  .info-card ul {
    list-style: none;
    padding: 0;
  }
  
  .info-card li {
    padding: 0.5rem 0;
    padding-left: 1.5rem;
    position: relative;
  }
  
  .info-card li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: #667eea;
  }
  
  .info-card code {
    background: rgba(0, 0, 0, 0.3);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    color: #4ecdc4;
  }
</style>

