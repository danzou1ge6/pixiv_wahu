<template>
  <div class="bg-blue text-white text-center q-pa-md flex flex-center" style="width: 100%; height: 90vh">
    <div>
      <div style="font-size: 30vh">
        404
      </div>

      <div class="text-h2" style="opacity:.4">
        Oops. Nothing here...
      </div>

      <q-btn class="q-mt-xl" color="white" text-color="blue" unelevated to="/" label="Go Home" no-caps />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ErrorNotFound'
});
</script>
