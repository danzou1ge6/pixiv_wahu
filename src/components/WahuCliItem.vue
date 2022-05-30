<template>
  <div v-if="text !== undefined && src === undefined">
    <pre>{{ text }}</pre>
  </div>
  <div v-if="text === undefined && src !== undefined">
    <q-img :src="src" max-width="100%" height="300px" fit="contain"></q-img>
  </div>
  <div v-if="text !== undefined && src !== undefined">
    <div class="row justify-center no-wrap q-gutter-md items-center">
      <div class="col">
        <q-img :src="src" max-width="60%" height="300px" fit="contain"></q-img>
      </div>
      <div class="col">
        <pre>{{ text }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  text?: string,
  src?: string
}>()

</script>

<style>
pre {
  white-space: break-spaces;
}
</style>
