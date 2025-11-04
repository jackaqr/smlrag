<script lang="ts">
  import { scanFiles, type ScanResult } from '$lib/api/dataset'
  
  let scanning = $state(false)
  let scanResult = $state<ScanResult | null>(null)
  let error = $state<string>('')
  
  async function handleScan() {
    scanning = true
    error = ''
    scanResult = null
    
    try {
      scanResult = await scanFiles()
    } catch (err) {
      error = err instanceof Error ? err.message : '扫描失败'
    } finally {
      scanning = false
    }
  }
  
  function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
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
    
    {#if scanResult}
      <div class="result success">
        <span class="result-icon">✅</span>
        扫描完成！找到 {scanResult.total_files} 个文件，总大小 {formatFileSize(scanResult.total_size)}
      </div>
      
      {#if scanResult.files.length > 0}
        <div class="files-list">
          <h3>📄 文件列表</h3>
          <div class="files-grid">
            {#each scanResult.files as file}
              <div class="file-item">
                <span class="file-icon">📄</span>
                <div class="file-info">
                  <div class="file-name">{file.name}</div>
                  <div class="file-size">{formatFileSize(file.size)}</div>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
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
  
  .files-list {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .files-list h3 {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    color: #4ecdc4;
  }
  
  .files-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .file-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(0, 0, 0, 0.3);
    padding: 0.75rem;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
  }
  
  .file-item:hover {
    background: rgba(0, 0, 0, 0.4);
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }
  
  .file-icon {
    font-size: 1.5rem;
  }
  
  .file-info {
    flex: 1;
    min-width: 0;
  }
  
  .file-name {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.9);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .file-size {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 0.25rem;
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

