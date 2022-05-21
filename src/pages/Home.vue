<template>
  <Transition appear enter-active-class="animated fadeInDown">
    <q-img :src="homeImageURL" v-show="showKud">
      <Transition appear enter-active-class="animated zoomIn">
        <div class="text-h1 absolute-top-right" v-show="showWahu">Wahu！</div>
      </Transition>
      <Transition appear enter-active-class="animated fadeInUp">
        <div class="text-subtitle-2 absolute-bottom-right" v-show="showWahu">クドリャフカ - 73072668 by クー </div>
      </Transition>
    </q-img>
  </Transition>
</template>

<script setup lang="ts">
import { homeImageURL } from 'src/constants';
import { onMounted, ref } from 'vue';

const showWahu = ref<boolean>(false)
const showKud = ref<boolean>(false)

onMounted(() => {
  setTimeout(() => {
    showWahu.value = true
  }, 500)
  setTimeout(() => {
    showKud.value = true
  }, 250)
})
</script>

<style scoped>
img {
  max-width: 100%;
  max-height: 95vh;
}
</style>
