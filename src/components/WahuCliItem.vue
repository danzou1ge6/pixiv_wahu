<template>
  <div v-if="text !== undefined && src === undefined">
    <pre class="normal-pre">{{ text }}</pre>
  </div>
  <div v-if="text === undefined && src !== undefined">
    <q-img :src="src" width="100%" height="300px" fit="contain"></q-img>
  </div>
  <div v-if="text !== undefined && src !== undefined">
    <div class="row justify-right no-wrap q-gutter-md items-center">
      <div class="col-6">
        <q-img :src="src" width="100%" height="300px" fit="contain"></q-img>
      </div>
      <div class="col-6">
        <pre class="inline-pre">{{ text }}</pre>
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

<style scoped>
.inline-pre {
  white-space: pre;
}
.normal-pre {
  white-space: pre-wrap;
}
pre {
  margin-top: 0px;
  margin-bottom: 0px;
}
</style>
