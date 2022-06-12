<template>

  <div class="row q-col-gutter-sm q-ma-sm">
    <RepoSync :repo-name="repoName" @refresh-cache="refreshCache = !refreshCache"
      @refresh-index="refreshIndex = !refreshIndex"></RepoSync>
    <RepoBrowseCache :repo-name="repoName" :refresh="refreshCache"></RepoBrowseCache>
    <RepoBrowseIndex :repo-name="repoName" :refresh="refreshIndex"
      @refresh-cache="refreshCache = !refreshCache"></RepoBrowseIndex>
  </div>

</template>

<script setup lang="ts">
import RepoSync from '../components/RepoSync.vue'
import RepoBrowseCache from 'src/components/RepoBrowseCache.vue';
import RepoBrowseIndex from 'src/components/RepoBrowseIndex.vue';
import { onMounted, ref } from 'vue';

const props = defineProps<{
  repoName: string
}>()
const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

onMounted(() => {
  emits('updateTitle', props.repoName)
})

const refreshCache = ref<boolean>(false)
const refreshIndex = ref<boolean>(false)

</script>
