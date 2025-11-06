<script lang="ts">
  import { page } from '$app/stores';
  
  const navItems = [
    { href: '/chat', label: '对话', icon: '💬' },
    { href: '/documents', label: '文档', icon: '📚' },
    { href: '/analytics', label: '分析', icon: '📊' },
    { href: '/settings', label: '设置', icon: '⚙️' }
  ];
  
  // 判断当前路由是否激活
  function isActive(href: string): boolean {
    return $page.url.pathname === href;
  }
</script>

<div class="topbar">
  <div class="topbar-content">
    <div class="logo">
      <span class="logo-icon">🤖</span>
      <span class="logo-text">SMLRAG</span>
    </div>
    
    <nav class="nav-buttons">
      {#each navItems as item}
        <a
          href={item.href}
          class="nav-btn"
          class:active={isActive(item.href)}
        >
          <span class="nav-icon">{item.icon}</span>
          <span class="nav-label">{item.label}</span>
        </a>
      {/each}
    </nav>
    
    <div class="user-section">
      <button class="user-btn" title="用户菜单">
        <span>👤</span>
      </button>
    </div>
  </div>
</div>

<style>
  .topbar {
    width: 100%;
    height: 60px;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    position: sticky;
    top: 0;
    z-index: 1000;
  }
  
  .topbar-content {
    max-width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1.5rem;
  }
  
  .logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 700;
    font-size: 1.25rem;
    color: #fff;
    user-select: none;
  }
  
  .logo-icon {
    font-size: 1.5rem;
    animation: pulse 2s ease-in-out infinite;
  }
  
  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.1);
    }
  }
  
  .logo-text {
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .nav-buttons {
    display: flex;
    gap: 0.5rem;
    flex: 1;
    justify-content: center;
  }
  
  .nav-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.2rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.95rem;
    font-weight: 500;
    text-decoration: none;
  }
  
  .nav-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
    transform: translateY(-2px);
  }
  
  .nav-btn.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: transparent;
    color: #fff;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }
  
  .nav-icon {
    font-size: 1.2rem;
    line-height: 1;
  }
  
  .nav-label {
    font-family: inherit;
  }
  
  .user-section {
    display: flex;
    align-items: center;
  }
  
  .user-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.2);
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
  }
  
  .user-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
    transform: scale(1.05);
  }
  
  @media (max-width: 768px) {
    .topbar-content {
      padding: 0 1rem;
    }
    
    .logo-text {
      display: none;
    }
    
    .nav-label {
      display: none;
    }
    
    .nav-btn {
      padding: 0.6rem;
      min-width: 40px;
      justify-content: center;
    }
    
    .nav-buttons {
      gap: 0.3rem;
    }
  }
</style>

