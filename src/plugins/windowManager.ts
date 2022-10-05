import { watch, ref } from 'vue'
import { Router, useRouter } from 'vue-router'

/** 自动生成 Interface Begin */
interface AppWindow {
    title?: string;
    component: 'CliScriptView' | 'ErrorNotFound' | 'GetToken' | 'Home' | 'IllustDetailLocal' | 'IllustDetailPixiv' | 'IllustQueryLocal' | 'PixivSearchIllust' | 'PixivSearchUser' | 'PixivUserDetail' | 'RepoView' | 'TagRegression' | 'TrendingTags';
    props?: object;
}
/** 自动生成 Interface End */

interface KeyedAppWindow extends AppWindow {
  key: number;
}

const openedWindows = ref<Array<KeyedAppWindow>>([{
  component: 'Home',
  title: 'Home',
  key: randomId(),
}])
let displayedWindowN = ref<number>(0)

function randomId() {
  return Math.floor(Math.random() * 1e8)
}

function gotoWindow(n: number): void {
  if(n < openedWindows.value.length) {
    displayedWindowN.value = n
  }
}

function pushWindow(win: AppWindow, goto?: boolean): void {

  let keyedWin = { ...win, key: randomId(), scrollY: 0 }
  openedWindows.value.push(keyedWin)
  if (goto || goto === undefined) { gotoWindow(openedWindows.value.length - 1) }
}

let router: Router

function initWindowRouter(r: Router) {
  router = r
}

watch(displayedWindowN, () => {
  router.push(String(displayedWindowN.value))
})

function refreshCurrentWindow() {
  openedWindows.value[displayedWindowN.value].key = randomId()
}

function removeWindow(i: number) {

  if (openedWindows.value.length <= 1) {
    openedWindows.value.splice(i, 1, {
      component: 'Home',
      title: 'home',
      key: randomId()
    })
    return
  }

  openedWindows.value.splice(i, 1)
  if (openedWindows.value.length == displayedWindowN.value) {
    displayedWindowN.value = displayedWindowN.value - 1
  }
}

function replaceCurrentWindow(win: AppWindow): void {
  let keyedWin = { ...win, key: randomId(), scrollY: 0 }
  openedWindows.value[displayedWindowN.value] = keyedWin
}

export {
  gotoWindow, pushWindow, openedWindows, displayedWindowN,
  refreshCurrentWindow, removeWindow, replaceCurrentWindow,
  initWindowRouter
}
export type { AppWindow }
