<script setup lang="ts">
defineProps<{
	samples: AudioSample[];
	playAudio: (audio: Float32Array, sampleRate: number) => void;
}>();
</script>
<template>
<section class="grid4 gap-4 p-8">
      <div v-for="sample in samples">
        <button
          class="rounded-3xl bg-#F1F3F4 col center  p-2 sh hover:brightness-120 scale"
          @click="playAudio(sample.audio, sample.sample_rate)"
        >
          <Icon icon="mdi-music" class="x4 text-gray-500" />
          <audio :src="sample.url" controls></audio>
        </button>
      </div>
    </section>
</template>