<script setup lang="ts">
const text = ref('')
const {
    state,
		generateMusic,
    playAudio,
    playAllSequentially,
    drawFrequencyData,
    canvas: canvasRef
	} = useSequencer()

async function createSample() {
  if (!text.value) return
  if (state.loading) return
  if (state.samples.length) {
   await generateMusic({text: text.value, audio:  state.samples[state.samples.length - 1].audio})
  }
  else {
  await generateMusic({text: text.value})
}
}

onMounted(() => {
if (!canvasRef.value) {
  canvasRef.value = document.querySelector('canvas')
}  
drawFrequencyData()
})
</script>

<template>
  <div class="col center gap-4">
    <p class="text-title">
      Studio
   </p>
    <p class="text-subtitle">
      Create Music with a prompt
    </p>
    <div>
    <button class="btn-icon bg-gray-500 col center">
      <span class="text-caption rf">  {{  state.loading ? state.loading : state.samples.length ? state.samples[state.samples.length - 1].time.toFixed(0) : '0' }}s   </span>
    </button>
    </div>
    <div class="col center gap-4">
      <p class="text-subtitle">
        {{ state.samples.length }} samples generated.
      </p>
      <p class="row center gap-4">
      <button
        class="btn-icon bg-success text-accent col center"
        :disabled="state.loading"
        @click="playAllSequentially"
      >
        <Icon icon="mdi-play-circle" class="x2" /> 
      </button>

    <button
      class="btn-icon bg-warning col center"
      :disabled="state.loading"
      @click="state.samples = []"
    >
      <Icon icon="mdi-delete" class="x2" />
    </button>
  </p>
    </div>
  
<canvas ref="canvasRef" width="640" height="360"></canvas>
      <section  class="row center gap-4">
       <div v-for="sample in state.samples">
         <button
          class="rounded-lg bg-gray-500 col center p-2 sh hover:brightness-120 scale"
          @click="playAudio(sample.audio,sample.sample_rate)"
        >
          <Icon icon="mdi-music" class=" x4"/>
        </button>
</div>
    </section>

    <TheInput
      v-model="text"
      placeholder="Make a music sample..."
      autocomplete="true"
      @keydown.enter="createSample"
    />


      <button
        class="btn-icon bg-gray-500 col center"
        :disabled="!text"
        @click="createSample"
      >
        <Icon icon="mdi-send"/>
      </button>
     </div>
</template>
