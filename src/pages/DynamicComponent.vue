<template>
  <div class="page-container">
    <transition-group appear enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutRight">
      <div v-for="(win, i) in openedWindows" :key="win.key" v-show="i == displayedWindowN" style="height: 100%;">
        <q-scroll-area style="height: 100%">
          <div class="component-container">
            <component :is="getComponent(win.component)" v-bind="win.props" @update-props="updateProps(i, $event)"
              @update-title="updateTitle(i, $event)">
            </component>
          </div>
        </q-scroll-area>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { openedWindows, displayedWindowN } from '../plugins/windowManager'
import { useQuasar } from 'quasar'


/** 自动生成 Import Begin */
import CliScriptView from './CliScriptView.vue'
import ErrorNotFound from './ErrorNotFound.vue'
import GetToken from './GetToken.vue'
import Home from './Home.vue'
import IllustDetailLocal from './IllustDetailLocal.vue'
import IllustDetailPixiv from './IllustDetailPixiv.vue'
import IllustQueryLocal from './IllustQueryLocal.vue'
import PixivSearchIllust from './PixivSearchIllust.vue'
import PixivSearchUser from './PixivSearchUser.vue'
import PixivUserDetail from './PixivUserDetail.vue'
import RepoView from './RepoView.vue'
import TagRegression from './TagRegression.vue'
import TrendingTags from './TrendingTags.vue'
interface componentIndex {[index: string] : any}
const components: componentIndex = {
  CliScriptView: CliScriptView,
  ErrorNotFound: ErrorNotFound,
  GetToken: GetToken,
  Home: Home,
  IllustDetailLocal: IllustDetailLocal,
  IllustDetailPixiv: IllustDetailPixiv,
  IllustQueryLocal: IllustQueryLocal,
  PixivSearchIllust: PixivSearchIllust,
  PixivSearchUser: PixivSearchUser,
  PixivUserDetail: PixivUserDetail,
  RepoView: RepoView,
  TagRegression: TagRegression,
  TrendingTags: TrendingTags,
}
/** 自动生成 Import End */

const $q = useQuasar()

function getComponent(name: string) {
  const comp = components[name]
  if (comp === undefined) {
    return ErrorNotFound
  } else {
    return comp
  }
}

function updateProps(i: number, props: object) {
  openedWindows.value[i].props = props
}

function updateTitle(i: number, title: string) {
  openedWindows.value[i].title = title
}


</script>
<style lang="scss" scoped>
.page-container {
  position: absolute;
  top: 0px;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
.component-container {
  position: relative;
  width: 100%;
  top: $header-height
}
</style>
