<script setup lang="ts">

defineProps<{
	state: any;
	playAllSequentially: () => void;
}>();


</script>

<template>
 <div class="col center gap-4">
      <p class="row center gap-4">
        <button
          class="btn-icon bg-success text-accent col center"
          @click="playAllSequentially"
        >
          <Icon icon="mdi-play-circle" class="x2" />
        </button>
        <button class="btn-icon bg-gray-500 col center animated-border-box">
        <span class="text-caption rf">
          {{
            state.loading
              ? state.loading
              : state.samples.length
                ? state.samples[state.samples.length - 1].time.toFixed(0)
                : "0"
          }}s
        </span>
      </button>
        <button
          class="btn-icon bg-warning col center"
          @click="state.samples = []"
        >
          <Icon icon="mdi-delete" class="x2" />
        </button>
      </p>
    </div></template>