<template>

  <q-btn @click="pushWindow({ component: 'PixivSearchIllust', props: { initialQueryString: 'uid ' + uid } })" flat>
    插画作品
  </q-btn>
  <q-btn @click="pushWindow({ component: 'PixivSearchIllust', props: { initialQueryString: 'bookmark ' + uid } })" flat>
    收藏插画
  </q-btn>
  <q-btn @click="pushWindow({ component: 'PixivSearchUser', props: { initialQueryString: 'following ' + uid } })" flat>
    {{ name }} 关注的用户
  </q-btn>
  <q-btn @click="pushWindow({ component: 'PixivSearchUser', props: { initialQueryString: 'follower ' + uid } })" flat>
    关注 {{ name }} 的用户
  </q-btn>
  <q-btn @click="pushWindow({ component: 'PixivSearchUser', props: { initialQueryString: 'related ' + uid } })" flat>
    相关用户
  </q-btn>
</template>

<script setup lang="ts">
import { pushWindow } from 'src/plugins/windowManager';

const props = defineProps<{
  name: string, uid: number
}>()
</script>
