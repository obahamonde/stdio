<script setup lang="ts">
const text = ref("");
defineProps<{
	createSample: ()=>void
}>();
</script>

<template>
<footer class="row center m-4 px-4 py-2">
    <TextInput
      v-model="text"
      placeholder="Create a sample..."
      autocomplete="true"
      @keydown.enter="createSample"
    />

    <button
      class="btn-icon bg-gray-500 col center"
      :disabled="!text"
      @click="createSample"
    >
      <Icon icon="mdi-send" />
    </button>
</footer></template>