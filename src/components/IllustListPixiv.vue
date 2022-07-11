<template>

  <CheckboxGroup v-model="selected">
    <template v-slot:default="{ toggle, getState }">

      <div class="row q-col-gutter-sm q-ma-md">
        <transition-group appear enter-active-class="animated zoomIn" leave-active-class="animated zoomOut">
          <div class="col-md-3 col-sm-6 col-xs-12 col-lg-2" v-for="ilst, i in illusts" :key="ilst.iid">
            <IllustCardPixiv @update:select="toggle(ilst.iid, $event)" :detail="ilst" :selected="getState(ilst.iid)"
              height="300px"
              :score="scores === undefined ? undefined : (scores[i] == -1 ? undefined : scores[i].toFixed(2))">
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
import CheckboxGroup from 'src/components/CheckboxGroup.vue';
import { ref } from 'vue';
import IllustCardPixiv from 'src/components/IllustCardPixiv.vue';
import { IllustDetail } from 'src/plugins/wahuBridge/methods';
import GotoTop from 'src/components/GotoTop.vue';
import PixivIllustToolbar from 'src/components/PixivIllustToolbar.vue';

const props = defineProps<{
  illusts: Array<IllustDetail>,
  scores?: Array<number>
}>()


const selected = ref<Array<number>>([])

</script>
