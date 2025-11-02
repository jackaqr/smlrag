<script lang="ts">
  // 使用 Svelte 5 的 runes API
  let inputText = $state('')
  let responseText = $state('')
  
  function handleSend() {
    if (inputText.trim()) {
      responseText = inputText
      inputText = ''
    }
  }
  
  function handleKeypress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleSend()
    }
  }
</script>

<div class="dialog-box">
  <h2>Smlrag</h2>
  
  <div class="input-group">
    <label for="text-input">请输入内容：</label>
    <div class="input-row">
      <input 
        id="text-input"
        type="text" 
        bind:value={inputText}
        placeholder="在这里输入..."
        onkeypress={handleKeypress}
      />
      {#if inputText}
        <button class="send-btn" onclick={handleSend}>发送</button>
      {/if}
    </div>
  </div>
  
  {#if responseText}
    <div class="response">
      <p class="response-label">回复：</p>
      <p class="response-text">{responseText}</p>
    </div>
  {/if}
</div>

<style>
  .dialog-box {
    width: 100%;
    max-width: 600px;
    padding: 2.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  h2 {
    margin: 0 0 2rem 0;
    color: #ff3e00;
    text-align: center;
    font-size: 1.8rem;
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    margin-bottom: 1.5rem;
  }

  label {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
  }

  .input-row {
    position: relative;
    width: 100%;
  }

  input {
    width: 100%;
    padding: 1rem 6rem 1rem 1.2rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 2px solid rgba(255, 62, 0, 0.3);
    background: rgba(255, 255, 255, 0.05);
    color: inherit;
    transition: border-color 0.3s, box-shadow 0.3s;
  }

  input:focus {
    outline: none;
    border-color: #ff3e00;
    box-shadow: 0 0 0 3px rgba(255, 62, 0, 0.1);
  }

  input::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }

  .send-btn {
    position: absolute;
    right: 0.4rem;
    top: 50%;
    transform: translateY(-50%);
    padding: 0.6rem 1.5rem;
    font-size: 0.95rem;
    border-radius: 6px;
    border: none;
    background: #ff3e00;
    color: white;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .send-btn:hover {
    background: #e63900;
    box-shadow: 0 2px 6px rgba(255, 62, 0, 0.4);
  }

  .send-btn:active {
    transform: translateY(-50%) scale(0.95);
  }

  .response {
    padding: 1.5rem;
    background: rgba(255, 62, 0, 0.08);
    border-radius: 8px;
    border-left: 4px solid #ff3e00;
  }

  .response-label {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #ff3e00;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .response-text {
    margin: 0;
    font-size: 1.1rem;
    line-height: 1.6;
  }
</style>

