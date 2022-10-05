<template>
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
import { ref, watch } from 'vue'
import { notificationTime } from '../constants'
import { wahu_logger_client } from '../plugins/wahuBridge/methods'
import { onSocketOpen } from '../plugins/wahuBridge/client'
import { useQuasar } from 'quasar'
import { Console } from 'console'


interface Props {
  modelValue: boolean,
  maxDisp: number
}
const { modelValue, maxDisp = 5 } = defineProps<Props>()

const emits = defineEmits<{
  (e: 'update:modelValue', id: boolean): void
}>()


const displayedNotifications = ref<Array<AppNotification>>([])

const $q = useQuasar()

watch(appAllNoti.value, (n: Array<AppNotification>) => {
  const noti = n[n.length - 1]
  $q.notify({
    type: notifyType(noti.level),
    message: noti.msg,
    position: 'bottom-right',
    closeBtn: true,
    progress: true,
    timeout: notificationTime
  })
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

function notifyType(level: 'error' | 'warning' | 'info' | 'success'): string {
  if (level == 'error') return 'negative'
  if (level == 'success') return 'positive'
  else return level
}


</script>

<style scoped lang="scss">
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

</style>
