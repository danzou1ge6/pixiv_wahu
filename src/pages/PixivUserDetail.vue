<template>
  <q-card class="q-ma-md" v-if="detail !== undefined">
    <q-img :src="detail.background_image == '' ? notfoundimageURL : serverImageURL + detail.background_image">
      <q-item>
        <q-item-section avatar top>
          <q-avatar rounded size="100px">
            <q-img :src="serverImageURL + detail.profile_image"></q-img>
          </q-avatar>
        </q-item-section>
        <q-item-section caption>
          {{ detail.name }}
          <br>
          <div class="text-body-2">
            / uid = {{ detail.uid }}<br>/ account = {{ detail.account }}
          </div>
        </q-item-section>
      </q-item>
      <div class="absolute-right q-pa-none" style="height: 75px">
        <PixivUserFollow :uid="uid" :name="detail.name" v-model="detail.is_followed"></PixivUserFollow>
      </div>
      <div class="text-body-1 absolute-bottom">{{ detail.comment }}</div>
    </q-img>
    <q-card-section>
      <div class="text-h7">信息</div>
      <div class="text-body-2 text-grey-9 q-mt-sm">
        / total_followers = {{ detail.total_followers }}
        / total_mypixiv_users = {{ detail.total_mypixiv_users }}
        / total_illusts = {{ detail.total_illusts }}
        / total_manga = {{ detail.total_manga }}
        / total_novels = {{ detail.total_novels }}
        / total_bookmarked_illust = {{ detail.total_bookmarked_illust }}
      </div>
    </q-card-section>
    <q-card-section>
      <div class="text-h7 q-pb-sm">导航</div>
      <PixivUserNav :name="detail.name" :uid="uid"></PixivUserNav>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import * as wm from '../plugins/wahuBridge/methods'
import { serverImageURL, notfoundimageURL } from 'src/constants';
import PixivUserNav from 'src/components/PixivUserNav.vue';
import PixivUserFollow from 'src/components/PixivUserFollow.vue';

const props = defineProps<{
  uid: number
}>()
const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

const detail = ref<wm.PixivUserDetail>()

onMounted(() => {
  wm.p_user_detail(props.uid)
    .then(dtl => {
      detail.value = dtl
      emits('updateTitle', 'User:' + detail.value.name)
    })
})

</script>
