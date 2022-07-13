<template>
  <div v-show="!modelValue" class="noti-box px-1">
    <transition-group enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutRight">
      <div v-for="(noti, i) in displayedNotifications" :key="i" class="pa-1">
        <q-banner :class="bannerClass(noti.level)" class="q-ma-sm semi-transparent">
          <template v-slot:avatar>
            <q-icon :name="iconName(noti.level)"></q-icon>
          </template>
          <pre>{{ noti.msg }}</pre>
        </q-banner>
      </div>
    </transition-group>
  </div>

  <transition appear enter-active-class="animated fadeInDown" leave-active-class="animated fadeOutUp">
    <div v-show="modelValue" class="noti-box-opened">
      <q-card class="noti-card">
        <q-scroll-area style="height: 100%">
          <div class="text-subtitle-2 q-ma-md">通知</div>
          <transition-group enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutRight">
            <div v-for="(noti, i) in appAllNoti" :key="i" class="py-1 px-0">
              <q-banner :class="bannerClass(noti.level)" class="q-ma-sm">
                <template v-slot:avatar>
                  <q-icon :name="iconName(noti.level)"></q-icon>
                </template>
                <pre>{{ noti.msg }}</pre>
              </q-banner>
            </div>
          </transition-group>
        </q-scroll-area>
      </q-card>
    </div>
  </transition>
</template>


<script setup lang="ts">
import { AppNotification, appAllNoti, pushNoti } from '../plugins/notifications'
import { onMounted, ref, watch } from 'vue'
import { notificationTime } from '../constants'
import { wahu_logger_client } from '../plugins/wahuBridge/methods'
import { onSocketOpen } from '../plugins/wahuBridge/client'


interface Props {
  modelValue: boolean,
  maxDisp: number
}
const { modelValue, maxDisp = 5 } = defineProps<Props>()

const emits = defineEmits<{
  (e: 'update:modelValue', id: boolean): void
}>()

async function listenLogGen(gen: AsyncGenerator<[number, string], undefined, null>) {
  while(true) {
    const ret = await gen.next()

    if(ret.value === undefined) {
      throw(new Error('logGen returned undefined'))
    }

    const [level, msg] = ret.value
    if(level == 30) { // warning
      pushNoti({level: 'warning', msg})
    }else if(level >= 40) {  // error, fatal
      pushNoti({level: 'error', msg})
    }
  }
}

onSocketOpen(() => {
  wahu_logger_client()
    .then(logGen => {
      listenLogGen(logGen)
    })
})


const displayedNotifications = ref<Array<AppNotification>>([])

watch(appAllNoti.value, (n: Array<AppNotification>) => {

  displayedNotifications.value.push(n.slice(-1)[0])

  if (displayedNotifications.value.length > maxDisp) {
    displayedNotifications.value.splice(
      0, displayedNotifications.value.length - maxDisp)
  }

  setTimeout(() => {
    displayedNotifications.value.splice(0, 1)
  }, notificationTime)
})

function bannerClass(level: 'error' | 'warning' | 'info' | 'success'): string {
  switch (level) {
    case 'error':
      return 'bg-negative text-white'
    case 'info':
      return 'bg-info text-white'
    case 'success':
      return 'bg-positive text-white'
    case 'warning':
      return 'bg-warning text-white'
  }
}

function iconName(level: 'error' | 'warning' | 'info' | 'success'): string {
  switch (level) {
    case 'error':
      return 'error'
    case 'info':
      return 'info'
    case 'success':
      return 'check'
    case 'warning':
      return 'warning'
  }
}


</script>

<style scoped lang="scss">
.noti-box {
  position: fixed;
  width: 500px;
  max-width: 95vw;
  max-height: 90vh;
  right: 10px;
  top: 55px;
  z-index: 999;
}

.noti-box-opened {
  position: fixed;
  @media (min-width: $breakpoint-md-min) {
    width: 75vw;
  }
  @media (max-width: $breakpoint-sm-max) {
    width: 95vw;
  }
  min-width: 300px;
  right: 10px;
  height: 80vh;
  top: 55px;
  z-index: 999;
}

.noti-card {
  height: 80vh;
  overflow-y: auto;
}

pre {
  white-space: break-spaces;
}

.semi-transparent {
  opacity: 0.8;
  backdrop-filter: blur(5px);
}
</style>
