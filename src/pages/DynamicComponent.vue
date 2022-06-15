<template>
  <div>
    <transition-group appear enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutRight"
      @enter="scroll">
      <div v-for="(win, i) in openedWindows" :key="win.key" v-show="i == displayedWindowN"
        style="position: absolute; width: 100%">
        <q-scroll-observer @scroll="scrollHandler"></q-scroll-observer>
        <component :is="getComponent(win.component)" v-bind="win.props" @update-props="updateProps(i, $event)"
          @update-title="updateTitle(i, $event)">
        </component>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { openedWindows, displayedWindowN } from '../plugins/windowManager'
import { useQuasar } from 'quasar'


/** 自动生成 Import Begin */
import CliScriptView from './CliScriptView.vue'
import ErrorNotFound from './ErrorNotFound.vue'
import Home from './Home.vue'
import IllustDetailLocal from './IllustDetailLocal.vue'
import IllustDetailPixiv from './IllustDetailPixiv.vue'
import IllustQueryLocal from './IllustQueryLocal.vue'
import PixivSearchIllust from './PixivSearchIllust.vue'
import PixivSearchUser from './PixivSearchUser.vue'
import PixivUserDetail from './PixivUserDetail.vue'
import RepoView from './RepoView.vue'
import TrendingTags from './TrendingTags.vue'
interface componentIndex {[index: string] : any}
const components: componentIndex = {
  CliScriptView: CliScriptView,
  ErrorNotFound: ErrorNotFound,
  Home: Home,
  IllustDetailLocal: IllustDetailLocal,
  IllustDetailPixiv: IllustDetailPixiv,
  IllustQueryLocal: IllustQueryLocal,
  PixivSearchIllust: PixivSearchIllust,
  PixivSearchUser: PixivSearchUser,
  PixivUserDetail: PixivUserDetail,
  RepoView: RepoView,
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

function scrollHandler(e: any) {
  openedWindows.value[displayedWindowN.value].scrollY = e.position.top
}


function scroll() {
  setTimeout(
    () => {
      window.scrollTo(0, openedWindows.value[displayedWindowN.value].scrollY)
    },
    $q.platform.is.mobile ? 200 : 100
  )
}


</script>
