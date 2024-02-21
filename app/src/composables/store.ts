import { defineStore, acceptHMRUpdate } from 'pinia'


export const useStore = defineStore('state', () => {
	const state = reactive({
		generated: Array<Array<number>>(),
	})
	return {
		state
	}

})

if (import.meta.hot) {
	import.meta.hot.accept(acceptHMRUpdate(useStore, import.meta.hot))
}