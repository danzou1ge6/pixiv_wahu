<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-bar v-if="showNotConnectedBar" class="bg-negative">
        <q-icon name="error"></q-icon>
        <div class="text-subtitle-2">未连接后端</div>
      </q-bar>

      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="leftDrawerOpen = !leftDrawerOpen" />

        <q-toolbar-title>
          PixivWahu
        </q-toolbar-title>

        <q-space></q-space>

        <TaskBar></TaskBar>

        <q-btn @click="windowRefresh" flat>
          <q-icon name="refresh"></q-icon>
          <q-tooltip>刷新页面</q-tooltip>
        </q-btn>

        <q-btn @click="showLoginCtl = !showLoginCtl" flat>
          <q-icon name="person"></q-icon>
          <q-tooltip>Access Token 状态</q-tooltip>
        </q-btn>

        <q-btn @click="showDlProgress = !showDlProgress" flat>
          <q-icon name="download"></q-icon>
          <q-tooltip>下载状态</q-tooltip>
        </q-btn>

        <q-btn @click="showNotification = !showNotification" flat>
          <q-icon name="notifications"></q-icon>
          <q-tooltip>通知</q-tooltip>
        </q-btn>

      </q-toolbar>
    </q-header>

    <NavDrawerContent v-model="leftDrawerOpen"></NavDrawerContent>

    <q-page-container>
      <NotificationArea v-model="showNotification" :max-disp="5"></NotificationArea>
      <LoginControl v-model="showLoginCtl"></LoginControl>
      <DownloadProgress v-model="showDlProgress"></DownloadProgress>
      <DynamicComponent></DynamicComponent>
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import NotificationArea from '../components/NotificationArea.vue';
import TaskBar from 'src/components/TaskBar.vue';
import DynamicComponent from '../pages/DynamicComponent.vue';

import { pushWindow, refreshCurrentWindow, AppWindow } from 'src/plugins/windowManager';
import LoginControl from 'src/components/LoginControl.vue';
import NavDrawerContent from 'src/components/NavDrawerContent.vue';
import DownloadProgress from 'src/components/DownloadProgress.vue';
import { soecketStatusReact } from 'src/plugins/wahuBridge/client';

export default defineComponent({
  name: 'MainLayout',

  components: {
    NotificationArea,
    TaskBar,
    DynamicComponent,
    LoginControl,
    NavDrawerContent,
    DownloadProgress
  },

  setup() {
    const leftDrawerOpen = ref(false)

    const showNotification = ref(false)
    const showLoginCtl = ref(false)
    const showDlProgress = ref(false)

    const route = useRoute()
    const router = useRouter()

    function pushWindowFromRouter() {
      if (route.params.page !== undefined) {

        pushWindow({
          component: route.params.page,
          title: route.params.page,
          props: route.query
        } as AppWindow, true)
      } else {
        pushWindow({
          component: 'Home',
          title: 'Home'
        }, true)
      }
    }

    onMounted(() => {
      window.addEventListener('hashchange', () => {
        const currentPath = window.location.hash.slice(1)
        router.push(currentPath)
        pushWindowFromRouter()
      }, false)
    })


    onMounted(() => {
      pushWindowFromRouter()
    })

    function windowRefresh() {
      refreshCurrentWindow()
    }

    const showNotConnectedBar = computed(() => {
      return soecketStatusReact.value == WebSocket.OPEN ? false : true
    })

    return {
      leftDrawerOpen,
      showNotification,
      showLoginCtl,
      showDlProgress,
      windowRefresh,
      showNotConnectedBar
    }
  }
});
</script>
