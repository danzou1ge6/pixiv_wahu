<template>
  <q-card v-if="detail !== undefined" class="q-ma-sm">
    <div class="q-ma-md">
      <span class="text-h4">{{ detail.title }}</span>
      <span class="text-h6 text-medium-emphasis">
        / iid = {{ detail.iid }}
      </span>
      <div class="col-2 q-ma-md absolute-right">
        <q-btn @click="handleBookmarkClick" :loading="bookmarkLoading" color="primary">
        {{ detail.is_bookmarked ? '取消收藏' :'收藏'}}</q-btn>
      </div>
    </div>

    <div class="row justify-center">
      <div class="col-md-8 col-lg-7 col-sm-12 col-xs-12">
        <q-card class="q-ma-sm">
          <div class="row justify-center">
            <div class="col-6">
              <q-select :options="imageQualities" v-model="selectedImageQuality" label="选择图片质量" dense class="q-ma-sm">
              </q-select>
            </div>
            <div class="col-6">
              <q-select class="q-ma-sm" :options="dbList" v-model="selectedDb" label="选择数据库" dense>
              </q-select>
            </div>
          </div>
        </q-card>

        <IllustImagePages v-model="selectedPage" :iid="iid" :page-count="detail.page_count"
          :disabled="selectedDb === undefined" :image-src-list="imageURLList"></IllustImagePages>

        <IllustInformation :detail="detail"></IllustInformation>
        <IllustCaption :detail="detail"></IllustCaption>
      </div>

      <div class="col-md-3 col-lg-4 col-sm-12 col-xs-12">
        <IllustTags :detail="detail"></IllustTags>
        <PixivUserPanel :user="detail.user"></PixivUserPanel>
      </div>
    </div>
  </q-card>

  <div v-if="detail === undefined">
    <q-linear-progress indeterminate>
    </q-linear-progress>
    <span class="text-h4 q-ma-md">
      Pixiv / iid = {{ props.iid }}
    </span>
  </div>

  <q-card class="q-ma-sm">
    <div class="q-ma-md text-h6">相关插画</div>

    <IllustListPixiv :illusts="relatedIllusts"></IllustListPixiv>

    <div class="row q-ma-lg" v-show="relatedGenerator !== undefined">
      <div class="col-12 q-mb-md">
        <q-btn @click="invokeRelatedGenerator" color="primary float-right" stretch :loading="relatedLoading">下一页</q-btn>
      </div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import * as wm from '../plugins/wahuBridge/methods'
import { IllustDetail } from '../plugins/wahuBridge/methods';
import { lazyimageURL } from '../constants';
import { computed } from '@vue/reactivity';
import IllustTags from 'src/components/IllustTags.vue';
import IllustInformation from 'src/components/IllustInformation.vue';
import PixivUserPanel from 'src/components/PixivUserPanel.vue';
import IllustImagePages from 'src/components/IllustImagePages.vue';
import IllustCaption from 'src/components/IllustCaption.vue';
import IllustListPixiv from 'src/components/IllustListPixiv.vue';
import { WahuStopIteration } from 'src/plugins/wahuBridge/client';
import { pushNoti } from 'src/plugins/notifications';

const imageQualities = [
  'original', 'large', 'medium', 'square_medium'
]

const props = defineProps<{
  iid: number
}>()
const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

const detail = ref<IllustDetail>()
const selectedPage = ref<Array<number>>([])

const selectedImageQuality = ref<string>()

const selectedDb = ref<string>()
const dbList = ref<Array<string>>([])

onMounted(() => {
  emits('updateTitle', 'Pixiv/' + props.iid)

  wm.get_config('fallback_image_size')
    .then(fis => { selectedImageQuality.value = fis })
  wm.p_ilst_detail(props.iid)
    .then(dtl => {
      detail.value = dtl
      emits('updateTitle', 'Pixiv/' + dtl.title)
    })
  wm.ibd_list()
    .then(ibdls => { dbList.value = ibdls })
})

const imageURLList = computed((): Array<string> => {
  if (selectedImageQuality.value === undefined || detail.value === undefined) {
    return [lazyimageURL]
  }
  if (selectedImageQuality.value == 'original') {
    return detail.value.image_origin
  }
  if (selectedImageQuality.value == 'large') {
    return detail.value.image_large
  }
  if (selectedImageQuality.value == 'medium') {
    return detail.value.image_medium
  }
  if (selectedImageQuality.value == 'square_medium') {
    return detail.value.image_sqmedium
  }
  return [lazyimageURL]
})


watch(selectedDb, (n) => {
  if (n !== undefined) {
    wm.ibd_query_bm(n, props.iid)
      .then(bm => {
        if (bm == null) {
          selectedPage.value = []
        } else {
          selectedPage.value = bm.pages
        }
      })
  }
})

watch(selectedPage, () => {
  if (selectedPage.value === undefined) {
    throw Error('selectedPage 为 undefined')
  }
  if (selectedDb.value !== undefined) {
    wm.ibd_set_bm(selectedDb.value, props.iid, selectedPage.value)
  }
})

const relatedIllusts = ref<Array<wm.IllustDetail>>([])

const relatedGenerator = ref<AsyncGenerator<Array<wm.IllustDetail>>>()

onMounted(() => {
  wm.p_ilst_related(props.iid)
    .then(gen => { relatedGenerator.value = gen })
})

onUnmounted(() => {
  if (relatedGenerator.value !== undefined && relatedGenerator.value.throw !== undefined) {
    relatedGenerator.value.throw(new WahuStopIteration())
  }
})

const relatedLoading = ref<boolean>(false)

function invokeRelatedGenerator() {
  if (relatedGenerator.value !== undefined) {
    relatedLoading.value = true
    relatedGenerator.value.next()
      .then(ret => {
        if (ret.done) {
          relatedGenerator.value = undefined
          pushNoti({
            level: 'info',
            msg: '已加载所有插画'
          })
          return
        }
        relatedIllusts.value = relatedIllusts.value.concat(ret.value)
        relatedLoading.value = false
      })
  }
}

const bookmarkLoading = ref<boolean>(false)

function handleBookmarkClick() {
  if (detail.value !== undefined) {
    if (detail.value.is_bookmarked) {
      bookmarkLoading.value = true
      wm.p_ilstbm_rm([props.iid])
        .then(() => {
          pushNoti({
            level: 'success',
            msg: `从 Pixiv 收藏删除 ${props.iid}`
          })
          bookmarkLoading.value = false
          if(detail.value !== undefined){detail.value.is_bookmarked = false}
        })
        .catch(() => { bookmarkLoading.value = false })

    } else {
      bookmarkLoading.value = true
      wm.p_ilstbm_add([props.iid])
        .then(() => {
          pushNoti({
            level: 'success',
            msg: `添加 ${props.iid} 到 Pixiv 收藏`
          })
          bookmarkLoading.value = false
          if(detail.value !== undefined){detail.value.is_bookmarked = true}
        })
        .catch(() => { bookmarkLoading.value = false })
    }

  }
}

</script>

<style scoped>
.image {
  max-height: 90vh;
}
</style>
