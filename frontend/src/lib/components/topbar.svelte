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
    height: 56px;
    background: var(--gradient-bar);
    border-bottom: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: 1000;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
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
    gap: 0.6rem;
    font-weight: 700;
    font-size: 1.2rem;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    user-select: none;
  }

  .logo-icon {
    font-size: 1.4rem;
    filter: drop-shadow(0 0 8px rgba(142, 164, 202, 0.4));
  }

  .logo-text {
    color: var(--color-brand);
  }

  .nav-buttons {
    display: flex;
    gap: 0.4rem;
    flex: 1;
    justify-content: center;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-md);
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 1rem;
    font-weight: 500;
    text-decoration: none;
  }

  .nav-btn:hover {
    background: var(--color-primary-muted);
    border-color: var(--border-default);
    color: var(--color-brand);
  }

  .nav-btn.active {
    background: var(--color-brand);
    border-color: transparent;
    color: #fff;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    box-shadow: 0 2px 12px rgba(61, 80, 112, 0.4);
  }

  .nav-icon {
    font-size: 1.2rem;
    line-height: 1;
    opacity: 0.9;
  }

  .nav-label {
    font-family: inherit;
  }

  .user-section {
    display: flex;
    align-items: center;
  }

  .user-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
  }

  .user-btn:hover {
    background: var(--color-primary-muted);
    border-color: var(--color-primary);
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
      padding: 0.5rem;
      min-width: 40px;
      justify-content: center;
    }

    .nav-buttons {
      gap: 0.25rem;
    }
  }
</style>

