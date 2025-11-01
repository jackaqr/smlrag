<script lang="ts">
  // 使用 Svelte 5 的 runes API
  let count = $state(0)
  
  function increment() {
    count++
  }
  
  function decrement() {
    count--
  }
  
  function reset() {
    count = 0
  }
</script>

<div class="counter">
  <div class="count-display">
    <span class="count">{count}</span>
  </div>
  
  <div class="button-group">
    <button onclick={decrement}>-</button>
    <button onclick={reset}>重置</button>
    <button onclick={increment}>+</button>
  </div>
</div>

<style>
  .counter {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
  }

  .count-display {
    font-size: 4rem;
    font-weight: bold;
    color: #ff3e00;
    min-width: 150px;
    text-align: center;
  }

  .count {
    display: inline-block;
    transition: transform 0.2s;
  }

  .count:active {
    transform: scale(1.1);
  }

  .button-group {
    display: flex;
    gap: 1rem;
  }

  button {
    min-width: 80px;
    padding: 0.8rem 1.5rem;
    font-size: 1.1rem;
    border-radius: 8px;
    border: 2px solid #ff3e00;
    background: rgba(255, 62, 0, 0.1);
    color: #ff3e00;
    cursor: pointer;
    transition: all 0.3s;
  }

  button:hover {
    background: #ff3e00;
    color: white;
    transform: translateY(-2px);
  }

  button:active {
    transform: translateY(0);
  }
</style>

