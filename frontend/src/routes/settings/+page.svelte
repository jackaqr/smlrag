<script lang="ts">
  import { onMount } from 'svelte'
  import * as configApi from '$lib/api/config'
  import type { AppConfig, ConfigModel, ConfigUI } from '$lib/api/config'
  import { log, logError } from '$lib/logger'

  type ConfigCategory = 'model' | 'ui'
  type ModelItem = { modality: string; id: string; label: string }

  const CONFIG_CATEGORIES: { id: ConfigCategory; label: string; icon: string }[] = [
    { id: 'model', label: '模型', icon: '🤖' },
    { id: 'ui', label: '界面', icon: '🎨' }
  ]

  const MODEL_PARAMS_PLACEHOLDER = '{"aspect_ratio":"16:9","seconds":5}'
  const MODALITIES = ['text', 'image', 'video'] as const
  const MODALITY_LABELS: Record<string, string> = { text: '文本', image: '图片', video: '视频' }

  /** 从 config.model 生成模型列表（按模态分组） */
  function buildModelListFromConfig(cfg: AppConfig | null): ModelItem[] {
    if (!cfg?.model) return []
    const list: ModelItem[] = []
    for (const mod of MODALITIES) {
      const m = cfg.model[mod as keyof ConfigModel]
      const models = m?.models ?? {}
      for (const id of Object.keys(models)) {
        list.push({ modality: mod, id, label: id })
      }
    }
    return list
  }

  /** 按模态分组的模型列表，用于弹层展示 */
  function buildModelListGrouped(cfg: AppConfig | null): { modality: string; label: string; items: ModelItem[] }[] {
    if (!cfg?.model) return []
    return MODALITIES.map((mod) => {
      const m = cfg.model[mod as keyof ConfigModel]
      const models = m?.models ?? {}
      const items: ModelItem[] = Object.keys(models).map((id) => ({ modality: mod, id, label: id }))
      return { modality: mod, label: MODALITY_LABELS[mod] ?? mod, items }
    }).filter((g) => g.items.length > 0)
  }

  let config = $state<AppConfig | null>(null)
  let loading = $state(true)
  let saving = $state(false)
  let message = $state<{ type: 'success' | 'error'; text: string } | null>(null)
  let activeCategory = $state<ConfigCategory>('model')
  let showModelListCard = $state(false)
  let selectedModel = $state<ModelItem | null>(null)
  let modelParamsJson = $state('')
  let modelParamsJsonError = $state('')
  let ui = $state<ConfigUI>({ theme: 'dark', sidebar_collapsed: false })

  /** 添加新模型 */
  let showAddModelForm = $state(false)
  let addModelModality = $state<'text' | 'image' | 'video'>('text')
  let addModelId = $state('')
  let addModelParamsJson = $state('{}')
  let addModelSetDefault = $state(false)
  let addModelError = $state('')

  /** 删除模型 */
  let showDeleteConfirm = $state(false)
  let deleting = $state(false)

  onMount(async () => {
    loading = true
    message = null
    try {
      config = await configApi.getConfig()
      ui = { theme: config.ui?.theme ?? 'dark', sidebar_collapsed: config.ui?.sidebar_collapsed ?? false }
      syncModelParamsJson()
    } catch (err) {
      logError('加载配置失败', err)
      message = { type: 'error', text: err instanceof Error ? err.message : '加载配置失败' }
    } finally {
      loading = false
    }
  })

  function syncModelParamsJson() {
    if (!selectedModel || !config?.model) return
    const m = config.model[selectedModel.modality as keyof ConfigModel]
    const models = m?.models ?? {}
    const entry = models[selectedModel.id]
    const params = entry?.params ?? m?.params ?? {}
    modelParamsJson = JSON.stringify(params, null, 2)
    modelParamsJsonError = ''
  }

  $effect(() => {
    if (config && selectedModel) syncModelParamsJson()
  })

  function openModelList() {
    showModelListCard = true
    showAddModelForm = false
  }

  function selectModel(item: ModelItem) {
    selectedModel = item
    showModelListCard = false
    syncModelParamsJson()
  }

  function closeModelListCard(e: MouseEvent) {
    if ((e.target as HTMLElement)?.classList?.contains('model-list-backdrop')) showModelListCard = false
  }

  async function saveModelParams() {
    if (!selectedModel || !config?.model) return
    modelParamsJsonError = ''
    let params: Record<string, unknown>
    try {
      const raw = modelParamsJson.trim() || '{}'
      const parsed = JSON.parse(raw)
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error('应为 JSON 对象')
      params = parsed as Record<string, unknown>
    } catch {
      modelParamsJsonError = '参数 JSON 格式错误'
      return
    }
    saving = true
    message = null
    try {
      const modality = selectedModel.modality as keyof ConfigModel
      const current = config.model[modality] ?? {}
      const models = { ...current.models, [selectedModel.id]: { params } }
      const newModel: ConfigModel = {
        ...config.model,
        [modality]: { ...current, models }
      }
      const updated = await configApi.updateConfig({ model: newModel })
      config = updated
      message = { type: 'success', text: '已保存当前模型参数' }
      log('模型参数已保存', { modality, id: selectedModel.id })
    } catch (err) {
      logError('保存模型参数失败', err)
      message = { type: 'error', text: err instanceof Error ? err.message : '保存失败' }
    } finally {
      saving = false
    }
  }

  async function saveUi() {
    saving = true
    message = null
    try {
      const updated = await configApi.updateConfig({ ui })
      config = updated
      ui = { theme: updated.ui?.theme ?? 'dark', sidebar_collapsed: updated.ui?.sidebar_collapsed ?? false }
      message = { type: 'success', text: '界面配置已保存' }
    } catch (err) {
      logError('保存界面配置失败', err)
      message = { type: 'error', text: err instanceof Error ? err.message : '保存失败' }
    } finally {
      saving = false
    }
  }

  async function submitAddModel() {
    addModelError = ''
    const id = addModelId.trim()
    if (!id) {
      addModelError = '请输入模型 ID'
      return
    }
    if (!config?.model) return
    let params: Record<string, unknown> = {}
    try {
      const raw = addModelParamsJson.trim() || '{}'
      const parsed = JSON.parse(raw)
      if (parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed)) {
        params = parsed as Record<string, unknown>
      }
    } catch {
      addModelError = '参数 JSON 格式错误'
      return
    }
    const modality = addModelModality as keyof ConfigModel
    const current = config.model[modality] ?? {}
    const models = { ...(current.models ?? {}), [id]: { params } }
    if (models[id] === undefined) models[id] = { params }
    const newModel: ConfigModel = {
      ...config.model,
      [modality]: {
        ...current,
        models,
        ...(addModelSetDefault ? { default_model: id } : {})
      }
    }
    saving = true
    message = null
    try {
      const updated = await configApi.updateConfig({ model: newModel })
      config = updated
      showAddModelForm = false
      addModelId = ''
      addModelParamsJson = '{}'
      addModelSetDefault = false
      message = { type: 'success', text: '已添加模型' }
      log('已添加模型', { modality, id })
    } catch (err) {
      logError('添加模型失败', err)
      addModelError = err instanceof Error ? err.message : '添加失败'
    } finally {
      saving = false
    }
  }

  function openDeleteConfirm() {
    showDeleteConfirm = true
  }

  function closeDeleteConfirm() {
    showDeleteConfirm = false
  }

  async function confirmDeleteModel() {
    if (!selectedModel || !config?.model) return
    const modality = selectedModel.modality as keyof ConfigModel
    const idToDelete = selectedModel.id
    const current = config.model[modality] ?? {}
    const models = { ...(current.models ?? {}) }
    delete models[idToDelete]
    const defaultModel = current.default_model === idToDelete ? undefined : current.default_model
    const remainingIds = Object.keys(models)
    const newDefault =
      defaultModel !== undefined && remainingIds.includes(defaultModel)
        ? defaultModel
        : remainingIds[0]
    const newModel: ConfigModel = {
      ...config.model,
      [modality]: {
        ...current,
        models,
        default_model: newDefault
      }
    }
    deleting = true
    message = null
    try {
      const updated = await configApi.updateConfig({ model: newModel })
      config = updated
      selectedModel = null
      showDeleteConfirm = false
      message = { type: 'success', text: '已删除该模型' }
      log('已删除模型', { modality, id: idToDelete })
    } catch (err) {
      logError('删除模型失败', err)
      message = { type: 'error', text: err instanceof Error ? err.message : '删除失败' }
    } finally {
      deleting = false
    }
  }
</script>

<div class="settings-page">
  <aside class="settings-sidebar">
    <div class="sidebar-header">
      <span class="icon">⚙️</span>
      <span class="title">设置</span>
    </div>
    <nav class="sidebar-nav">
      {#each CONFIG_CATEGORIES as cat}
        <button
          type="button"
          class="nav-item"
          class:active={activeCategory === cat.id}
          onclick={() => (activeCategory = cat.id)}
        >
          <span class="nav-icon">{cat.icon}</span>
          <span class="nav-label">{cat.label}</span>
        </button>
      {/each}
    </nav>
  </aside>

  <main class="settings-main">
    {#if loading}
      <div class="loading">加载配置中…</div>
    {:else if activeCategory === 'model'}
      <div class="model-config">
        <div class="model-config-header">
          <button type="button" class="btn model-list-btn" onclick={openModelList}>
            选择模型
          </button>
          <button type="button" class="btn model-list-btn" onclick={() => { showAddModelForm = !showAddModelForm; addModelError = ''; showModelListCard = false; }}>
            添加模型
          </button>
          {#if selectedModel}
            <span class="selected-model-name">当前：{selectedModel.label}</span>
          {:else}
            <span class="selected-model-hint">请先选择要配置的模型</span>
          {/if}
        </div>

        {#if showAddModelForm}
          <div class="add-model-form">
            <div class="params-label">添加新模型</div>
            <div class="block">
              <label for="add-modality">模态</label>
              <select id="add-modality" bind:value={addModelModality}>
                <option value="text">文本 (text)</option>
                <option value="image">图片 (image)</option>
                <option value="video">视频 (video)</option>
              </select>
            </div>
            <div class="block">
              <label for="add-model-id">模型 ID（必填）</label>
              <input id="add-model-id" type="text" class="params-json" bind:value={addModelId} placeholder="例如：My-Model-1" />
            </div>
            <div class="block">
              <label for="add-model-params">初始参数（JSON，可选）</label>
              <textarea id="add-model-params" class="params-json" bind:value={addModelParamsJson} rows="4" placeholder={'{}'}></textarea>
            </div>
            <div class="block checkbox-row">
              <input type="checkbox" id="add-set-default" bind:checked={addModelSetDefault} />
              <label for="add-set-default">设为该模态的默认模型</label>
            </div>
            {#if addModelError}
              <span class="params-error">{addModelError}</span>
            {/if}
            <div class="params-actions">
              <button type="button" class="btn primary" disabled={saving} onclick={submitAddModel}>添加</button>
              <button type="button" class="btn" disabled={saving} onclick={() => { showAddModelForm = false; addModelError = ''; }}>取消</button>
            </div>
          </div>
        {/if}

        {#if showModelListCard}
          <div
            class="model-list-backdrop"
            role="dialog"
            aria-modal="true"
            aria-label="选择模型"
            tabindex="-1"
            onclick={closeModelListCard}
            onkeydown={(e) => { if (e.key === 'Escape') showModelListCard = false; }}
          >
            <div class="model-list-card">
              <div class="model-list-title">模型列表</div>
              {#each buildModelListGrouped(config) as group}
                <div class="model-list-group">
                  <div class="model-modality">{group.label}</div>
                  <ul class="model-list">
                    {#each group.items as item}
                      <li>
                        <button
                          type="button"
                          class="model-list-item"
                          class:selected={selectedModel?.id === item.id && selectedModel?.modality === item.modality}
                          onclick={() => selectModel(item)}
                        >
                          <span class="model-label">{item.label}</span>
                        </button>
                      </li>
                    {/each}
                  </ul>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        {#if selectedModel && !showAddModelForm}
          <div class="params-section">
            <label for="model-params-json" class="params-label">参数（JSON，平铺）</label>
            <textarea
              id="model-params-json"
              class="params-json"
              bind:value={modelParamsJson}
              placeholder={MODEL_PARAMS_PLACEHOLDER}
              rows="12"
              disabled={saving}
            ></textarea>
            {#if modelParamsJsonError}
              <span class="params-error">{modelParamsJsonError}</span>
            {/if}
            <div class="params-actions">
              <button type="button" class="btn primary" disabled={saving} onclick={saveModelParams}>
                {saving ? '保存中…' : '保存当前模型参数'}
              </button>
              <button type="button" class="btn btn-danger" disabled={saving} onclick={openDeleteConfirm}>
                删除该模型
              </button>
            </div>
          </div>
        {/if}

        {#if showDeleteConfirm}
          <div
            class="model-list-backdrop"
            role="dialog"
            aria-modal="true"
            aria-label="确认删除模型"
            tabindex="-1"
            onclick={(e) => { if ((e.target as HTMLElement)?.classList?.contains('model-list-backdrop')) closeDeleteConfirm(); }}
            onkeydown={(e) => { if (e.key === 'Escape') closeDeleteConfirm(); }}
          >
            <div class="model-list-card delete-confirm-card">
              <div class="model-list-title">确认删除</div>
              <p class="delete-confirm-text">
                确定要删除模型「{selectedModel?.label}」吗？该模态下若无其他模型，将恢复默认配置。
              </p>
              <div class="params-actions delete-confirm-actions">
                <button type="button" class="btn btn-danger" disabled={deleting} onclick={confirmDeleteModel}>
                  {deleting ? '删除中…' : '确认删除'}
                </button>
                <button type="button" class="btn" disabled={deleting} onclick={closeDeleteConfirm}>取消</button>
              </div>
            </div>
          </div>
        {/if}
      </div>
    {:else if activeCategory === 'ui'}
      <div class="ui-config">
        <h2 class="panel-title">界面设置</h2>
        <form
          class="ui-form"
          onsubmit={(e) => {
            e.preventDefault()
            saveUi()
          }}
        >
          <div class="block">
            <label for="cfg-theme">主题</label>
            <select id="cfg-theme" bind:value={ui.theme}>
              <option value="dark">深色</option>
              <option value="light">浅色</option>
            </select>
          </div>
          <div class="block checkbox-row">
            <input type="checkbox" id="sidebar_collapsed" bind:checked={ui.sidebar_collapsed} />
            <label for="sidebar_collapsed">侧边栏默认收起</label>
          </div>
          <button type="submit" class="btn primary" disabled={saving}>
            {saving ? '保存中…' : '保存界面配置'}
          </button>
        </form>
      </div>
    {/if}

    {#if message}
      <div class="message" class:success={message.type === 'success'} class:error={message.type === 'error'}>
        {message.text}
      </div>
    {/if}
  </main>
</div>

<style>
  .settings-page {
    flex: 1;
    display: flex;
    overflow: hidden;
    background: var(--bg-surface);
  }

  .settings-sidebar {
    width: 200px;
    flex-shrink: 0;
    background: var(--bg-base);
    border-right: 1px solid var(--border-subtle);
    display: flex;
    flex-direction: column;
  }

  .sidebar-header {
    padding: 1rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    border-bottom: 1px solid var(--border-subtle);
  }

  .sidebar-header .icon {
    font-size: 1.5rem;
  }

  .sidebar-header .title {
    font-weight: 600;
    color: var(--text-primary);
  }

  .sidebar-nav {
    padding: 0.75rem 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.65rem 1.25rem;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 0.95rem;
    text-align: left;
    width: 100%;
    transition: background 0.2s;
  }

  .nav-item:hover {
    background: var(--color-primary-muted);
    color: var(--text-primary);
  }

  .nav-item.active {
    background: var(--color-primary-muted);
    color: var(--text-primary);
    border-left: 3px solid var(--color-primary);
  }

  .nav-icon {
    font-size: 1.2rem;
  }

  .settings-main {
    flex: 1;
    overflow: auto;
    padding: 1.5rem 2rem;
    color: var(--text-primary);
  }

  .loading {
    padding: 3rem;
    color: var(--text-secondary);
  }

  .model-config {
    position: relative;
    max-width: 720px;
  }

  .model-config-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .model-list-btn {
    padding: 0.5rem 1rem;
    border-radius: var(--radius-md);
    border: none;
    background: var(--gradient-primary);
    color: var(--color-brand);
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 600;
    transition: filter 0.2s, box-shadow 0.2s;
  }

  .model-list-btn:hover {
    filter: brightness(1.08);
    box-shadow: 0 2px 10px rgba(142, 164, 202, 0.35);
  }

  .selected-model-name {
    color: var(--text-primary);
    font-size: 1rem;
  }

  .selected-model-hint {
    color: var(--text-muted);
    font-size: 0.95rem;
  }

  .model-list-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    padding: 80px 0 0 220px;
  }

  .model-list-card {
    background: var(--bg-elevated);
    border: 2px solid var(--color-primary);
    border-radius: var(--radius-lg);
    padding: 1rem;
    min-width: 280px;
    box-shadow: var(--shadow-lg);
  }

  .model-list-title {
    font-weight: 600;
    font-size: 1rem;
    color: var(--color-primary);
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-default);
  }

  .model-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .model-list li {
    margin: 0;
  }

  .model-list-item {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
    width: 100%;
    padding: 0.65rem 0.75rem;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: var(--text-primary);
    cursor: pointer;
    font-size: 0.95rem;
    text-align: left;
    transition: background 0.2s;
  }

  .model-list-item:hover {
    background: var(--color-primary-muted);
  }

  .model-list-item.selected {
    background: var(--color-primary-muted);
    color: var(--color-primary);
  }

  .model-modality {
    font-size: 0.8rem;
    color: var(--text-muted);
  }

  .params-section {
    margin-top: 1rem;
  }

  .params-label {
    display: block;
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
  }

  .params-json {
    width: 100%;
    padding: 0.75rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-default);
    background: #fff;
    color: var(--text-primary);
    font-family: ui-monospace, monospace;
    font-size: 0.9rem;
    resize: vertical;
  }

  .params-json:focus {
    outline: none;
    border-color: var(--color-primary);
  }

  .params-error {
    display: block;
    margin-top: 0.4rem;
    font-size: 0.85rem;
    color: #ff8a80;
  }

  .params-actions {
    margin-top: 1rem;
  }

  .add-model-form {
    margin-bottom: 1.5rem;
    padding: 1.25rem;
    border: 2px solid var(--color-primary);
    border-radius: var(--radius-lg);
    background: var(--bg-elevated);
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    box-shadow: var(--shadow-md);
  }

  .add-model-form .params-label {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-primary);
  }

  .add-model-form .params-actions {
    display: flex;
    gap: 0.5rem;
  }

  .add-model-form input[type='text'] {
    padding: 0.6rem 0.75rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-default);
    background: #fff;
    color: var(--text-primary);
    font-size: 0.95rem;
  }

  .add-model-form input[type='text']:focus {
    outline: none;
    border-color: var(--color-primary);
  }

  .add-model-form textarea.params-json {
    background: #fff;
    color: var(--text-primary);
    border: 1px solid var(--border-default);
  }

  .add-model-form select {
    background: #fff;
    color: var(--text-primary);
    border: 1px solid var(--border-default);
  }

  .model-list-group {
    margin-bottom: 0.5rem;
  }

  .model-list-group .model-modality {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 0.25rem;
  }

  .delete-confirm-card {
    min-width: 320px;
  }

  .delete-confirm-text {
    margin: 0 0 1rem 0;
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  .delete-confirm-actions {
    display: flex;
    gap: 0.5rem;
  }

  .ui-config {
    max-width: 480px;
  }

  .panel-title {
    font-size: 1.25rem;
    margin: 0 0 1rem 0;
    color: var(--text-primary);
  }

  .ui-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .block {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .block label {
    font-size: 0.9rem;
    color: var(--text-secondary);
  }

  .block select {
    padding: 0.6rem 0.75rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-default);
    background: #fff;
    color: var(--text-primary);
    font-size: 0.95rem;
  }

  .block select:focus {
    outline: none;
    border-color: var(--color-primary);
  }

  .checkbox-row {
    flex-direction: row;
    align-items: center;
  }

  .checkbox-row input[type='checkbox'] {
    width: 1.1rem;
    height: 1.1rem;
    accent-color: var(--color-primary);
  }

  .checkbox-row label {
    margin: 0;
    cursor: pointer;
  }

  .message {
    margin-top: 1.5rem;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
  }

  .message.success {
    background: var(--color-accent-muted);
    border: 1px solid rgba(20, 184, 166, 0.4);
    color: #5eead4;
  }

  .message.error {
    background: var(--color-primary-muted);
    border: 1px solid var(--color-primary);
    color: #fdba74;
  }

  .btn {
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
  }

  .btn.primary {
    background: var(--gradient-primary);
    color: var(--color-brand);
  }

  .btn.primary:hover:not(:disabled) {
    filter: brightness(1.08);
    transform: translateY(-1px);
  }

  .btn.btn-danger {
    background: var(--bg-elevated);
    color: #ff8a80;
    border: 1px solid rgba(255, 138, 128, 0.5);
  }

  .btn.btn-danger:hover:not(:disabled) {
    background: rgba(255, 138, 128, 0.15);
  }

  .btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
</style>
