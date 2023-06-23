<template>
  <div class="float-right">

    <q-btn-dropdown color="primary" icon="menu" class="q-ma-md">
      <q-list dense>
        <q-item clickable v-close-popup flat @click="showConfig = !showConfig">
          配置
        </q-item>
        <q-item clickable v-close-popup @click="updateSubscribe" :loading="updateSubsLoading">
          更新订阅
        </q-item>
        <q-item clickable @click="exportJson">
          导出 JSON
          <q-menu auto-close anchor="top right">
            <q-btn :href="objURLForExport" target="_blank" :loading="objURLForExport === undefined"
              @click="objURLForExport = undefined">下载</q-btn>
          </q-menu>
        </q-item>
        <q-item clickable>
          导入 JSON
          <q-menu anchor="top right">
            <q-file :model-value="jsonUpload" @update:model-value="handleJsonUpload" label="上传 JSON 文件"></q-file>
          </q-menu>
        </q-item>

      </q-list>
    </q-btn-dropdown>

    <DatabaseConfig v-model="showConfig" :db-name="dbName"></DatabaseConfig>

    <q-dialog v-model="showUpdateSubs" @hide="updateSubSInfo = '更新订阅..\n'">
      <q-card style="width: 50%">
        <q-card-section><q-linear-progress :indeterminate="updateSubsLoading"></q-linear-progress></q-card-section>
        <q-card-section>
          <q-scroll-area style="height: 300px;" ref="infoScroller">
            <pre class="q-ma-md">{{  updateSubSInfo }}</pre>
          </q-scroll-area>
        </q-card-section>
      </q-card>
    </q-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import * as wm from '../plugins/wahuBridge/methods'
import { pushNoti } from '../plugins/notifications';
import DatabaseConfig from 'src/components/DatabaseConfig.vue';
import { QScrollArea } from 'quasar';

const props = defineProps<{
  dbName: string,
}>()
const emits = defineEmits<{
  (e: 'updateSubscrip'): void
}>()

const showConfig = ref<boolean>(false)
const showUpdateSubs = ref<boolean>(false)
const updateSubSInfo = ref<string>('更新订阅..\n')

const infoScroller = ref<QScrollArea|null>(null)

const jsonUpload = ref<File>()

const updateSubsLoading = ref<boolean>(false)

async function consumePipedInfo(pipe: AsyncGenerator<string, undefined, string|null>) {
  while (true) {
    let value = await pipe.next()

    if (value.done) {
      updateSubsLoading.value = false
      updateSubSInfo.value += '完成'
      emits('updateSubscrip')
      return
    }

    updateSubSInfo.value += value.value;
    if (infoScroller.value != null)
      infoScroller.value.setScrollPercentage('vertical', 1, 0.1)
  }
}

function updateSubscribe() {
  showUpdateSubs.value = true

  updateSubsLoading.value = true

  wm.ibd_update_subs(props.dbName, null)
    .then(consumePipedInfo)
}

const objURLForExport = ref<string>()
function exportJson() {
  wm.ibd_export_json(props.dbName)
    .then(json => {
      objURLForExport.value = window.URL.createObjectURL(
        new Blob([json], { type: 'application/json' })
      )
    })
}

function handleJsonUpload(f: File) {
  jsonUpload.value = f
  const reader = new FileReader()
  reader.readAsText(f, 'utf-8')
  reader.onload = () => {
    if(typeof reader.result == 'string'){
      wm.ibd_import_json(props.dbName, reader.result)
        .then(() => {
          pushNoti({
            level: 'success',
            msg: '导入 JSON 到 ' + props.dbName + ' 成功'
          })
        })
    }else {
      pushNoti({
        level: 'error',
        msg: '读取文件失败'
      })
    }
  }
}

</script>
