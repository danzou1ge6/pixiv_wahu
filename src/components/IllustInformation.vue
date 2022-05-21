<template>
  <q-card class="q-ma-sm">
    <q-card-section class="pb-0 mb-0">信息</q-card-section>
    <q-card-section class="my-2">
      <span class="text-body-2 text-grey-8">
        / bookmarks = {{ detail.total_bookmarks }}
        / views = {{ detail.total_view }}
        / restrict = {{ detail.restrict }}
        / sanity_level = {{ detail.sanity_level }}
        / visible = {{ detail.visible }}
        / x_restrict = {{ detail.x_restrict }}
      </span>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import type { IllustDetail } from 'src/plugins/wahuBridge/methods';
const props = defineProps<{ detail: IllustDetail }>()
</script>
