<template>
  <transition appear enter-active-class="animated fadeInDown" leave-active-class="animated fadeOutUp">
    <q-card class="dl-card" v-show="modelValue">
      <q-checkbox v-model="showFinished" label="显示已完成"></q-checkbox>
      <q-markup-table>
        <thead>
          <tr>
            <th>描述</th>
            <th>进度</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dl in dlProgList" :key="dl.gid" v-show="dl.status == 'inprogress' || showFinished">
            <td>{{ dl.descript }}</td>
            <td>
              <q-linear-progress
                :value="dl.total_size === null ? (dl.status == 'inprogress'?undefined:1):dl.downloaded_size / dl.total_size"
                :color="getColor(dl.status)"
                :indeterminate="dl.total_size === null && dl.status == 'inprogress'"
              >
              </q-linear-progress>
              <div class="text-body-2">
                {{
                `${(dl.downloaded_size / 1024).toFixed(0)} / ${dl.total_size === null ? '':(dl.total_size / 1024).toFixed(0)} kb`
                }}
              </div>
            </td>
            <td>
              {{ statusStringFor(dl.status) }}
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </q-card>
  </transition>
</template>

<script setup lang="ts">
import * as wm from '../plugins/wahuBridge/methods'
import { regDlProgressReportCbk } from '../plugins/wahuBridge/client'
import { computed, onMounted, ref } from 'vue';

const props = defineProps<{ modelValue: boolean }>()
const emits = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()

const dlProgList = ref<Array<wm.DownloadProgress>>([])

const showFinished = ref<boolean>(false)

function updateDlProg(val: Array<wm.DownloadProgress>) {
  dlProgList.value = val
}


onMounted(() => {
  regDlProgressReportCbk(updateDlProg)
})

function statusStringFor(val: string) {
  switch (val) {
    case 'inprogress':
      return '下载中'
    case 'finished':
      return '完成'
    case 'error':
      return '失败'
    case 'pending':
      return '等待中'
  }
}

function getColor(status: string) {
  switch(status) {
    case 'inprogress':
      return 'primary'
    case 'error':
      return 'red'
    case 'finished':
      return 'green'
    case 'pending':
      return 'primary'
  }
}

</script>

<style scoped>
.dl-card {
  position: fixed;
  width: 60vw;
  min-width: 400px;
  right: 10px;
  top: 55px;
  z-index: 999;
  max-height: 80vh;
  overflow-y: auto;
}
</style>
