<template>
  <div class="top-anchor" ref="topAnchor"></div>

  <q-scroll-observer @scroll="scrollHandler"></q-scroll-observer>

  <Transition appear enter-active-class="animated zoomIn" leave-active-class="animated zoomOut">
    <q-btn v-show="showGotoTop" @click="gotoTop"
      style="position: fixed; right: 10px; bottom: 75px; z-index: 5;"
      color="primary">
      <q-icon name="arrow_upward"></q-icon>
    </q-btn>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const topAnchor = ref<HTMLTemplateElement | null>(null)

const showGotoTop = ref<boolean>(false)

function scrollHandler(e: any): void {
  if (e.position.top > 100) { showGotoTop.value = true }
  else { showGotoTop.value = false }
}

function gotoTop(): void {
  if (topAnchor.value !== null) {
    topAnchor.value.scrollIntoView({
      block: 'start',
      behavior: 'smooth'
    })
  }
}

</script>

<style scoped>
.top-anchor {
  position: absolute;
  top: 0;
  left: 0;
}
</style>
