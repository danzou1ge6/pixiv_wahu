<template>
  <q-card v-if="detail !== undefined" class="q-ma-sm">
    <div class="q-ma-md">
      <span class="text-h4">{{ detail.title }}</span>
      <span class="text-h6 text-grey-8">
        / iid = {{ detail.iid }} / dbName = {{ dbName }}
      </span>
    </div>
    <div class="q-mx-lg q-my-none text-subtitle-2 text-grey-8" v-if="addTimestamp !== undefined">
      添加于 {{ new Date(addTimestamp*1000)}}  <!--Python 时间戳单位为秒，js 为毫秒-->
    </div>

    <div class="row justify-center">
      <div class="col-md-8 col-lg-7 col-sm-12 col-xs-12">

        <IllustImagePages v-model="selectedPage" :db-name="dbName" :page-count="detail.page_count" :iid="iid"
          :disabled="false">
        </IllustImagePages>
        <IllustInformation :detail="detail"></IllustInformation>
        <illust-caption :detail="detail"></illust-caption>

      </div>
      <div class="col-md-3 col-lg-4 col-sm-12 col-xs-12">

        <IllustTags :detail="detail" :db-name="dbName"></IllustTags>
        <PixivUserPanel :user="detail.user"></PixivUserPanel>

        <q-card class="q-ma-sm">
          <q-card-section>Pximg 服务器图片链接</q-card-section>
          <div v-for="imgURLPg in detail.image_large.length" :key="imgURLPg">
            <div class="text-body-1 text-grey-8 q-mx-md">页 {{ imgURLPg }}</div>
            <q-card-section>
              <div class="text-body-2">
                <q-btn flat :href="serverImageURL + detail.image_origin[imgURLPg - 1]" target="_blank">
                  original
                </q-btn>
                <q-btn flat :href="serverImageURL + detail.image_large[imgURLPg - 1]" target="_blank">
                  large
                </q-btn>
                <q-btn flat :href="serverImageURL + detail.image_medium[imgURLPg - 1]" target="_blank">
                  medium
                </q-btn>
                <q-btn flat :href="serverImageURL + detail.image_sqmedium[imgURLPg - 1]" target="_blank">
                  square_medium
                </q-btn>
              </div>
            </q-card-section>
          </div>
        </q-card>

        <q-btn @click="openPixivDetail" stretch class="q-ma-sm" icon="launch" label="查看 Pixiv 详情页面"></q-btn>
      </div>
    </div>
  </q-card>

  <div v-if="detail === undefined">
    <q-linear-progress indeterminate>
    </q-linear-progress>
    <span class="text-h4 q-ma-md">
      / db_name = {{ props.dbName }} / iid = {{ props.iid }}
    </span>
  </div>

  <q-card v-if="detailNotFound && selectedPage !== undefined" class="q-ma-md">
    <q-card-section>
      <div class="text-h2">插画详情 Not Found ㄟ( ▔, ▔ )ㄏ</div>
    </q-card-section>
    <q-card-section>
      <q-input label="设置收藏页" underlined hint="用英文逗号分割整数 e.g. 0,1,2 ；输入 -1 来清除收藏" :placeholder="selectedPage.join(',')"
        v-model="manualBmPages" :error="manualBmPagesError">
      </q-input>
    </q-card-section>
  </q-card>

  <q-card v-if="bookmarkedPagesNotFound" class="q-ma-md">
    <q-card-section>
      <div class="text-h2">收藏页 Not Found ㄟ( ▔, ▔ )ㄏ</div>
    </q-card-section>
  </q-card>
</template>


<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import * as wm from '../plugins/wahuBridge/methods'
import { serverImageURL } from '../constants';
import { pushWindow } from '../plugins/windowManager';
import IllustInformation from '../components/IllustInformation.vue';
import IllustCaption from 'src/components/IllustCaption.vue';
import IllustTags from 'src/components/IllustTags.vue';
import PixivUserPanel from 'src/components/PixivUserPanel.vue';
import IllustImagePages from 'src/components/IllustImagePages.vue';

const props = defineProps<{
  dbName: string,
  iid: number,
}>()
const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

const detail = ref<wm.IllustDetail>()
const selectedPage = ref<Array<number>>([])
const addTimestamp = ref<number>()

const manualBmPages = ref<string>('')
const manualBmPagesError = ref<boolean>(false)

const detailNotFound = ref<boolean>(false)
const bookmarkedPagesNotFound = ref<boolean>(false)

onMounted(() => {
  emits('updateTitle', props.dbName + '/' + props.iid)

  wm.ibd_ilst_detail(props.dbName, props.iid)
    .then(ilstdtl => {
      if (ilstdtl === null) {
        detailNotFound.value = true
      } else {
        detail.value = ilstdtl

        emits('updateTitle', props.dbName + '/' + detail.value.title)
      }
    })

  wm.ibd_query_bm(props.dbName, props.iid)
    .then(bm => {
      if (bm === null) {
        bookmarkedPagesNotFound.value = true
        selectedPage.value = []
      } else {
        selectedPage.value = bm.pages
        addTimestamp.value = bm.add_timestamp
      }
    })
    .then(() => {
      watch(selectedPage, () => {
        if (selectedPage.value === undefined) {
          throw Error('selectedPage 为 undefined')
        }
        wm.ibd_set_bm(props.dbName, props.iid, selectedPage.value)
      })
    })
})

watch(manualBmPages, () => {
  manualBmPagesError.value = false
  let strPages = manualBmPages.value.split(',')
  let pages: Array<number> = []
  for (let p of strPages) {
    // 跳过空字符串
    if (p == '') {
      continue
    }

    let np = Number(p)
    // 不允许出现整数外的内容
    if (isNaN(np) || Math.round(np) != np) {
      manualBmPagesError.value = true
      return
    } else {
      // 传入 -1 来清除收藏
      if (np == -1) {
        bookmarkedPagesNotFound.value = true
        wm.ibd_set_bm(props.dbName, props.iid, [])
        return
      }
      // 压入整数数组
      pages.push(np)
    }
  }

  // 什么都不输入不执行操作
  if (pages.length >= 1) {
    bookmarkedPagesNotFound.value = false
    wm.ibd_set_bm(props.dbName, props.iid, pages)
  }
})

function openPixivDetail() {
  pushWindow({
    component: 'IllustDetailPixiv',
    props: { iid: props.iid },
    title: `Pixiv/${props.iid}`
  }, true)
}

</script>

