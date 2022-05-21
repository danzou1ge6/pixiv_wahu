<template>
  <q-card class="q-ma-sm">
    <q-card-section>描述</q-card-section>
    <q-card-section>
      <p class="text-body-2" v-html="detail.caption">
      </p>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import type { IllustDetail } from 'src/plugins/wahuBridge/methods';
const props = defineProps<{ detail: IllustDetail }>()
</script>
