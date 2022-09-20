<template>
  <q-card class="shadow-3">

    <q-item>
      <q-item-section>
        <q-item-label v-if="score !== undefined">
          <q-badge>
            <q-icon name="check"></q-icon>{{ score }}
          </q-badge>
          <q-tooltip>模糊匹配的分数</q-tooltip>
        </q-item-label>
        <q-item-label @click="clickTitle" class="cursor-pointer">
          {{ detail.title }}
        </q-item-label>
        <q-item-label @click="clickUsername" caption class="cursor-pointer">
          by {{ detail.user.name }}
        </q-item-label>
      </q-item-section>

      <q-item-section side top v-if="!unselectable">
        <q-checkbox :model-value="selected" @update:model-value="$emit('update:select', $event)"></q-checkbox>
      </q-item-section>
    </q-item>

    <q-img loading="lazy" :alt="notfoundimageURL" :src="serverImageURL + detail.image_medium[0]" fit="cover"
      :height="height" :placeholder-src="lazyimageURL">
    </q-img>

    <div class="q-ma-sm">
      <div class="text-body-2 text-grey-6">
        / iid = {{ detail.iid }} / uid = {{ detail.user.uid }}
      </div>
      <div>
        <span v-if="detail.is_bookmarked">
          <q-badge>
            <q-icon name="bookmark"></q-icon>
          </q-badge>
        </span>
        <span v-if="detail.page_count != 1" style="display: inline-block" class="q-mx-sm">
          <q-badge>
            <q-icon name="photo"></q-icon>
            {{ detail.page_count }}
          </q-badge>
        </span>
        <span style="display: inline-block">
          <q-badge>
            <q-icon name="bookmarks"></q-icon>
            {{ detail.total_bookmarks }}
          </q-badge>
        </span>
      </div>
    </div>

  </q-card>
</template>

<script setup lang="ts">

import * as wm from '../plugins/wahuBridge/methods'
import { notfoundimageURL, lazyimageURL, serverImageURL } from '../constants'
import { pushWindow } from 'src/plugins/windowManager';

interface Props {
  detail: wm.IllustDetail,
  height: string,
  selected: boolean,
  unselectable?: boolean,
  score?: number | string
}

const props = defineProps<Props>()


const emits = defineEmits<{
  (e: 'update:select', val: boolean): void
}>()


function clickTitle() {
  pushWindow({
    component: 'IllustDetailPixiv',
    title: `Pixiv/${props.detail.iid}`,
    props: { iid: props.detail.iid }
  }, true)
}

function clickUsername() {
  pushWindow({
    component: 'PixivUserDetail',
    title: 'User:' + props.detail.user.name,
    props: {uid: props.detail.user.uid}
  })
}


</script>
