<template>
  <div class="text-h6 q-ma-md">趋势标签</div>
  <q-linear-progress :indeterminate="loading"></q-linear-progress>
  <CheckboxGroup v-model="selected">
    <template v-slot:default="{ toggle, getState }">

      <div class="row q-col-gutter-sm q-ma-md">
        <transition-group appear enter-active-class="animated zoomIn" leave-active-class="animated zoomOut">
          <div class="col-md-3 col-sm-6 col-xs-12 col-lg-2 " v-for="tti in ttis" :key="tti.illust.iid">
            <div class="text-subtitle-1">
              <span>{{ tti.tag.name }}</span>
              <span class="text-grey-8">&emsp;{{ tti.tag.translated }}</span>
            </div>
            <IllustCardPixiv @update:select="toggle(tti.illust.iid, $event)"
              :detail="tti.illust" :selected="getState(tti.illust.iid)"
              height="300px">
            </IllustCardPixiv>
          </div>
        </transition-group>
      </div>

    </template>
  </CheckboxGroup>

  <PixivIllustToolbar v-model="selected" :details="illusts"></PixivIllustToolbar>

  <GotoTop></GotoTop>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import type { TrendingTagIllusts } from '../plugins/wahuBridge/methods'
import { p_trending_tags } from '../plugins/wahuBridge/methods'
import IllustCardPixiv from 'src/components/IllustCardPixiv.vue';
import CheckboxGroup from 'src/components/CheckboxGroup.vue';
import GotoTop from 'src/components/GotoTop.vue';
import PixivIllustToolbar from 'src/components/PixivIllustToolbar.vue';

const loading = ref<boolean>(true)
const selected = ref<Array<number>>([])

const illusts = computed(() => {
  let ret = []
  for(const tti of ttis.value) {
    ret.push(tti.illust)
  }
  return ret
})

const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

const ttis = ref<Array<TrendingTagIllusts>>([])

onMounted(() => {
  p_trending_tags()
    .then(ret => {
      ttis.value = ret
      loading.value = false
    })

  emits('updateTitle', '趋势标签')
})
</script>

