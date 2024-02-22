<script setup lang="ts">
const modelValue = defineModel();
</script>

<template>
  <input
    id="input"
    v-model="modelValue"
    type="text"
    v-bind="$attrs"
      class="w-full px-4 py-2 rounded-lg mx-2 bg-black backdrop-blur-md bg-gray-700 text-white"  

  />
</template>
