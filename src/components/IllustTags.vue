<template>
  <q-card class="q-ma-sm">
    <q-card-section>标签</q-card-section>
    <q-card-section>
      <div v-for="tag in detail.tags" :key="tag.name">
        <div class="text-body-2 cursor-pointer" @click="queryTag(tag.name)">
          {{ tag.name }}
          <q-tooltip>
            在 {{ dbName === undefined ? 'Pixiv' : dbName }} 搜索标签 {{ tag.name }}
          </q-tooltip>
        </div>
        <div class="text-body-2 text-grey-8">{{ tag.translated }}</div>
      </div>
    </q-card-section>
  </q-card>
</template>


<script setup lang="ts">
import type { IllustDetail } from 'src/plugins/wahuBridge/methods';
import { pushWindow } from 'src/plugins/windowManager';

const props = defineProps<{ detail: IllustDetail, dbName?: string }>()

function queryTag(tagName: string) {
  if (props.dbName === undefined) {
    pushWindow({
      component: 'PixivSearchIllust',
      props: { initialQueryString: '-s etag "' + tagName + '"'}
    })

  } else {
    pushWindow({
      component: 'IllustQueryLocal',
      title: props.dbName,
      props: { dbName: props.dbName, initialQueryString: '-t "' + tagName + '"'}
    }, true)
  }
}

</script>
