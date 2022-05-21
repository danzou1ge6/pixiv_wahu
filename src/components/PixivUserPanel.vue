<template>

  <q-card class="q-ma-sm">
    <q-item>
      <q-item-section top avatar>
        <q-avatar>
          <img :src="`${serverImageURL}/${user.profile_image}`">
        </q-avatar>
      </q-item-section>
      <q-item-section>
        <span class="cursor-pointer" @click="pushWindow({ component: 'PixivUserDetail', props: { uid: user.uid } })">
          {{ user.name }}
          <q-tooltip>
            查看 {{ user.name }} 的详情
          </q-tooltip>
        </span>
        <br>
        <div class="text-body-2 text-grey-8">
          / uid = {{ user.uid }}
        </div>
        <q-badge v-if="user.is_followed" style="width: 25px;">
          <q-icon name="bookmark"></q-icon>
        </q-badge>
      </q-item-section>
    </q-item>
  </q-card>
</template>


<script setup lang="ts">
import type { PixivUserSummery } from 'src/plugins/wahuBridge/methods';
import { serverImageURL } from 'src/constants';
import { pushWindow } from 'src/plugins/windowManager';

const props = defineProps<{ user: PixivUserSummery }>()
</script>

