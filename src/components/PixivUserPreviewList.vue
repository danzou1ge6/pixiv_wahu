<template>
  <q-card class="q-ma-md">
    <q-list bordered>
      <div v-for="up in userPreviews" :key="up.user_summery.uid">
        <q-expansion-item style="display: block">
          <template v-slot:header>
            <q-item>
              <q-item-section top avatar>
                <q-avatar rounded size="60px">
                  <img :src="`${serverImageURL}/${up.user_summery.profile_image}`">
                </q-avatar>
              </q-item-section>
              <q-item-section>
                {{ up.user_summery.name }}
                <br>
                <div class="text-body-2 text-grey-8">
                  / uid = {{ up.user_summery.uid }}
                </div>
                <q-badge v-if="up.user_summery.is_followed" style="width: 25px;">
                  <q-icon name="bookmark"></q-icon>
                </q-badge>
              </q-item-section>
            </q-item>
          </template>

          <div class="row q-col-gutter-sm q-ma-sm">
            <div class="col-md-3 col-sm-6 col-xs-12 col-lg-2" v-for="ilst in up.illusts" :key="ilst.iid">
              <IllustCardPixiv :detail="ilst" :unselectable="true" :selected="false" height="300px">
              </IllustCardPixiv>
            </div>

          </div>
          <div class="row q-ma-sm">
            <q-btn @click="pushWindow({ component: 'PixivUserDetail', props: { uid: up.user_summery.uid } })" flat
              color="primary">
              详情
            </q-btn>
            <PixivUserNav :name="up.user_summery.name" :uid="up.user_summery.uid"></PixivUserNav>
            <PixivUserFollow :name="up.user_summery.name" :uid="up.user_summery.uid"
              v-model="up.user_summery.is_followed"></PixivUserFollow>
          </div>
          <q-separator></q-separator>
        </q-expansion-item>
        <q-separator></q-separator>
      </div>
    </q-list>
  </q-card>

  <GotoTop></GotoTop>

</template>


<script setup lang="ts">
import { PixivUserPreview } from 'src/plugins/wahuBridge/methods';
import IllustCardPixiv from './IllustCardPixiv.vue';
import { pushWindow } from 'src/plugins/windowManager';
import { serverImageURL } from 'src/constants';
import PixivUserNav from './PixivUserNav.vue';
import PixivUserFollow from './PixivUserFollow.vue';
import GotoTop from './GotoTop.vue';

const props = defineProps<{
  userPreviews: Array<PixivUserPreview>
}>()


</script>
