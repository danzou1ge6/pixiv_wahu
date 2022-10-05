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
          {{ title }}
        </q-item-label>
        <q-item-label @click="clickUsername" caption class="cursor-pointer">
          by {{ userName }}
          <q-tooltip>在 {{ dbName }} 中检索 {{ userName }} 的作品</q-tooltip>
        </q-item-label>
      </q-item-section>

      <q-item-section side top>
        <q-checkbox :model-value="selected" @update:model-value="handleUpdate"></q-checkbox>
      </q-item-section>
    </q-item>

    <q-img loading="lazy" :alt="notfoundimageURL" :src="imageSrc" fit="cover" :height="height"
      :placeholder-src="lazyimageURL">
    </q-img>

    <div class="q-ma-sm">
      <div class="text-body-2 text-grey-6">
        / iid = {{ iid }} / uid = {{ uid }}
      </div>
      <div v-if="pageCount != 1" style="display: inline-block">
        <q-badge>
          <q-icon name="photo"></q-icon>
          {{ pageCount }}
        </q-badge>
      </div>
    </div>

  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';

import * as wm from '../plugins/wahuBridge/methods'
import { notfoundimageURL, lazyimageURL } from '../constants'
import { pushWindow } from 'src/plugins/windowManager';

interface Props {
  dbName: string,
  iid: number,
  selected: boolean,
  height: string,
  displayedPage?: number,
  score?: number
}

const props = defineProps<Props>()


const emits = defineEmits<{
  (e: 'update:select', val: boolean): void
}>()


const show = ref<boolean>(false)

const title = ref<string>('')
const userName = ref<string>('')
const uid = ref<number>(-1)
const pageCount = ref<number>(1)
const imageSrc = ref<string>('')

function loadDetail(): void {
  if (!show.value) {
    show.value = true
    wm.ibd_ilst_detail(props.dbName, props.iid)
      .then(ilst => {
        if (ilst === null) {
          title.value = 'Unknown'
          userName.value = 'Unknown'
          uid.value = -1
          imageSrc.value = notfoundimageURL
          return
        }

        title.value = ilst.title
        userName.value = ilst.user.name
        uid.value = ilst.user.uid
        pageCount.value = ilst.page_count

        if (props.displayedPage === undefined) {
          imageSrc.value = `/ilstdbimage/${props.dbName}/${props.iid}/0`
        } else {
          imageSrc.value = `/ilstdbimage/${props.dbName}/${props.iid}/${props.displayedPage}`
        }

      })
  }
}
onMounted(loadDetail)

function clickTitle() {
  pushWindow({
    component: 'IllustDetailLocal',
    title: `${props.dbName}/${props.iid}`,
    props: { dbName: props.dbName, iid: props.iid }
  }, true)
}

function clickUsername() {
  pushWindow({
    component: 'IllustQueryLocal',
    title: props.dbName,
    props: { dbName: props.dbName, initialQueryString: '-U ' + uid.value }
  }, true)
}

function handleUpdate(val: boolean) {
  emits('update:select', val)
}

</script>
