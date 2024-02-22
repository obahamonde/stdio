<script setup lang="ts">
const text = ref("");
const {
  state,
  generateMusic,
  playAudio,
  playAllSequentially,
  drawFrequencyData,
  canvas: canvasRef,
} = useContext();
async function createSample() {
  if (!text.value) return;
  if (state.loading) return;
  if (state.samples.length) {
    await generateMusic({
      text: text.value,
      audio: state.samples[state.samples.length - 1].audio,
    });
  } else {
    await generateMusic({ text: text.value });
  }
}

onMounted(() => {
  if (!canvasRef.value) {
    canvasRef.value = document.querySelector("canvas");
  }
  drawFrequencyData();
});
</script>

<template>
<AppTitle :state="state" :playAllSequentially="playAllSequentially" />
<canvas ref="canvasRef" width="960" height="480" class="mx-auto"></canvas>
<AppInput :createSample="createSample" v-model:text="text" />  
<AppFooter :samples="state.samples" :playAudio="playAudio" />
</template>
