<template>

  <q-btn @click="pushWindow({ component: 'PixivSearchIllust', props: { initialQueryString: '-u ' + uid } })" flat>
    插画作品
  </q-btn>
  <q-btn @click="pushWindow({ component: 'PixivSearchIllust', props: { initialQueryString: '-b ' + uid } })" flat>
    收藏插画
  </q-btn>
  <q-btn @click="pushWindow({ component: 'PixivSearchUser', props: { initialQueryString: '-F ' + uid } })" flat>
    {{ name }} 关注的用户
  </q-btn>
  <q-btn @click="pushWindow({ component: 'PixivSearchUser', props: { initialQueryString: '-f ' + uid } })" flat>
    关注 {{ name }} 的用户
  </q-btn>
  <q-btn @click="pushWindow({ component: 'PixivSearchUser', props: { initialQueryString: '-r ' + uid } })" flat>
    相关用户
  </q-btn>
</template>

<script setup lang="ts">
import { pushWindow } from 'src/plugins/windowManager';

const props = defineProps<{
  name: string, uid: number
}>()
</script>
