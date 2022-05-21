<template>
  <q-card>
    <q-expansion-item>
      <template v-slot:header>
        <PixivUserPanel :user="userPreview.user_summery"></PixivUserPanel>
      </template>

      <IllustListPixiv :illusts="userPreview.illusts"></IllustListPixiv>

    </q-expansion-item>
  </q-card>
</template>

<script setup lang="ts">
import * as wm from '../plugins/wahuBridge/methods'
import PixivUserPanel from './PixivUserPanel.vue';
import IllustListPixiv from './IllustListPixiv.vue';

const props = defineProps<{
  userPreview: wm.PixivUserPreview
}>()

</script>
