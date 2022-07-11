<template>
  <div class="bg-blue text-white text-center q-pa-md flex flex-center" style="width: 100%; height: 90vh">
    <div>
      <div style="font-size: 30vh">
        404
      </div>

      <div class="text-h2" style="opacity:.4">
        Oops. Nothing here...
      </div>

    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted } from 'vue';

const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

onMounted(() => {
  emits('updateTitle', '404')
})
</script>
