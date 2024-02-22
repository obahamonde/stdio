import { defineStore, acceptHMRUpdate } from "pinia";
import { User } from "firebase/auth";

export const useStore = defineStore("state", () => {
  const state = reactive({
    user: null as User | null,
  });
  return {
    state,
  };
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useStore, import.meta.hot));
}
