<script setup lang="ts">
defineProps<{
	state: any;
	playAllSequentially: ()=>void
}>();

</script>

<template>
<h1 class="row center"> 
<AppLogo /> 
<ControlsTop :state="state" :playAllSequentially="playAllSequentially" />   </h1>
</template>