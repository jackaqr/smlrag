<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <p>
      推荐的 IDE 设置:
      <a href="https://code.visualstudio.com/" target="_blank">VS Code</a>
      +
      <a href="https://github.com/johnsoncodehk/volar" target="_blank">Volar</a>
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  msg: string
}>()
</script>

<style scoped>
.hello {
  text-align: center;
}

h1 {
  color: #42b983;
}

p {
  margin-top: 1rem;
}
</style>

