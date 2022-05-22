<template>
  <div class="float-right">

    <q-btn-dropdown color="primary" label="操作" class="q-ma-md">
      <q-list dense>
        <q-item clickable v-close-popup flat @click="showConfig = !showConfig">
          配置
        </q-item>
        <q-item clickable v-close-popup @click="showUpdateSubs = !showUpdateSubs" :loading="updateSubsLoading">
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

    <q-dialog v-model="showUpdateSubs">
      <q-card>
        <q-card-section>
          <q-input v-model="updateSubsPageCount" @keyup.enter="updateSubscribe" underlined autofocus label="每个订阅更新的页数"
            :rules="[n => !isNaN(Number(n))]" type="number" hint="输入-1来更新全部"></q-input>
        </q-card-section>
      </q-card>
    </q-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import * as wm from '../plugins/wahuBridge/methods'
import { pushNoti } from '../plugins/notifications';
import DatabaseConfig from 'src/components/DatabaseConfig.vue';
import { json } from 'body-parser';

const props = defineProps<{
  dbName: string,
}>()
const emits = defineEmits<{
  (e: 'updateSubscrip'): void
}>()

const showConfig = ref<boolean>(false)
const showUpdateSubs = ref<boolean>(false)
const updateSubsPageCount = ref<number>(-1)

const jsonUpload = ref<File>()

const updateSubsLoading = ref<boolean>(false)

function updateSubscribe() {
  showUpdateSubs.value = false

  let pc: number
  if (updateSubsPageCount.value == -1) { pc = -1 }
  else { pc = updateSubsPageCount.value }

  updateSubsLoading.value = true

  wm.ibd_update_subs(props.dbName, pc)
    .then(num => {
      pushNoti({
        level: 'success',
        msg: `${props.dbName} 更新了 ${num} 幅插画`
      })
      updateSubsLoading.value = false
      emits('updateSubscrip')
    })
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
