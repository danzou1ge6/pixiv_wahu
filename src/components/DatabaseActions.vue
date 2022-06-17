<template>
  <div class="float-right">

    <q-btn-dropdown color="primary" icon="menu" class="q-ma-md">
      <q-list>
        <q-item clickable @click="update">
          <q-item-section avatar><q-icon name="update"></q-icon></q-item-section>
          <q-item-section>更新详情</q-item-section>
        </q-item>
        <q-item clickable @click="exportJson">
          <q-item-section avatar><q-icon name="file_upload"></q-icon></q-item-section>
          <q-item-section>导出 JSON</q-item-section>
          <q-menu auto-close anchor="top right">
            <q-btn :href="objURLForExport" target="_blank" :loading="objURLForExport === undefined"
              @click="objURLForExport = undefined" label="下载"></q-btn>
          </q-menu>
        </q-item>
        <q-item clickable>
          <q-item-section avatar><q-icon name="file_download"></q-icon></q-item-section>
          <q-item-section>导入 JSON</q-item-section>
          <q-menu anchor="top right">
            <q-file :model-value="jsonUpload" @update:model-value="handleJsonUpload" label="上传 JSON 文件"></q-file>
          </q-menu>
        </q-item>

      </q-list>
    </q-btn-dropdown>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import * as wm from '../plugins/wahuBridge/methods'
import { pushNoti } from '../plugins/notifications';

const props = defineProps<{
  dbName: string,
}>()


const jsonUpload = ref<File>()

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

function update() {
  wm.ibd_update(props.dbName)
    .then(num => {
      pushNoti({
        level: 'success',
        msg: `更新了 ${props.dbName} 的 ${num} 条详情`
      })
    })
}

</script>
