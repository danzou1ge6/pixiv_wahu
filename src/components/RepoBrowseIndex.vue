<template>
  <div class="col-12">
    <q-card>
      <q-table :rows="indexed" row-key="fid" :rows-per-page-options="[10, 20, 50, 100, 200, 500, 0]" dense
        :columns="indexedColDef">
        <template v-slot:top>
          <div class="col-4 q-table__title">已索引的文件</div>
          <q-btn flat @click="loadIndex" color="primary" class="float-right q-ma-sm" label="刷新" icon="refresh">
          </q-btn>
          <q-btn flat @click="updateIndex" color="primary" class="float-right q-ma-sm" :loading="updating"
            icon="update" label="更新">
            <q-tooltip>
              将索引缓存中下载完成的项移入索引
            </q-tooltip>
          </q-btn>
          <q-btn flat @click="validate" color="primary" class="float-right q-ma-sm" :loading="validating"
            label="校验" icon="verified">
            <q-tooltip>
              检查是否存在未索引的文件和失效的索引
            </q-tooltip>
          </q-btn>
        </template>
      </q-table>
    </q-card>
  </div>

  <div class="col-md-6 col-lg-6 col-sm-12 col-xs-12">
    <q-card>
      <q-table :rows="invalidFiles" row-key="path" :rows-per-page-options="[10, 20, 50, 100, 200, 500, 0]" dense
        :columns="invalidFileColDef" selection="multiple" v-model:selected="selectedDelFile">
        <template v-slot:top>
          <div class="col-2 q-table__title">无效文件</div>
          <q-btn flat @click="submitDelFile" color="warning" class="float-right q-ma-sm"
            v-show="selectedDelFile.length != 0">删除</q-btn>
        </template>
      </q-table>
    </q-card>
  </div>

  <div class="col-md-6 col-lg-6 col-sm-12 col-xs-12">
    <q-card>
      <q-table :rows="invalidIndex" row-key="fid" :rows-per-page-options="[10, 20, 50, 100, 200, 500, 0]" dense
        :columns="indexedColDef" selection="multiple" v-model:selected="selectedDelIndex">
        <template v-slot:top>
          <div class="col-2 q-table__title">无效索引</div>
          <q-btn flat @click="submitDelIndex" color="warning" class="float-right q-ma-sm"
            v-show="selectedDelIndex.length != 0">删除</q-btn>
        </template>
      </q-table>
    </q-card>
  </div>

</template>


<script setup lang="ts">
import { pushNoti } from 'src/plugins/notifications';
import { onMounted, ref, watch } from 'vue';
import * as wm from '../plugins/wahuBridge/methods'

const props = defineProps<{
  repoName: string,
  refresh: boolean
}>()
const emits = defineEmits<{
  (e: 'refreshCache'): void
}>()

const updating = ref<boolean>(false)
const validating = ref<boolean>(false)

watch(() => props.refresh, () => {
  loadIndex()
})

const indexedColDef = [
  { name: 'fid', label: 'FID', field: 'fid', },
  { name: 'path', label: '文件', field: 'path' }
]
const invalidFileColDef = [indexedColDef[1]]

const indexed = ref<Array<wm.FileEntry>>([])

function loadIndex() {
  wm.ir_get_index(props.repoName)
    .then(c => { indexed.value = c })
}

function updateIndex() {
  updating.value = true
  wm.ir_update_index(props.repoName)
    .then(newEntries => {
      pushNoti({
        level: 'info',
        msg: `${props.repoName} 新增了 ${newEntries.length} 条索引`
      })
      updating.value = false

      loadIndex()
      emits('refreshCache')
    })
}

onMounted(loadIndex)

interface FileWithPath {
  path: string
}

const invalidFiles = ref<Array<FileWithPath>>([])
const invalidIndex = ref<Array<wm.FileEntry>>([])

const selectedDelFile = ref<Array<FileWithPath>>([])
const selectedDelIndex = ref<Array<wm.FileEntry>>([])

function validate() {
  validating.value = true
  wm.ir_validate(props.repoName)
    .then(([entries, files]) => {
      invalidFiles.value = files.map(item => {
        return { path: item }
      })
      validating.value = false
      invalidIndex.value = entries

      if (files.length == 0 && entries.length == 0) {
        pushNoti({
          level: 'success',
          msg: '校验无异常'
        })
      }
    })
}

function submitDelFile() {
  const files = selectedDelFile.value.map(item => item.path)
  wm.ir_remove_file(props.repoName, files)
    .then(() => {
      pushNoti({
        level: 'success',
        msg: `从储存库 ${props.repoName} 删除了 ${selectedDelFile.value.length} 个无效文件`
      })
      selectedDelFile.value = []
      validate()
    })
}

function submitDelIndex() {
  const fids = selectedDelIndex.value.map(item => item.fid)
  wm.ir_rm_index(props.repoName, fids)
    .then(() => {
      pushNoti({
        level: 'success',
        msg: `从储存库 ${props.repoName} 删除了 ${selectedDelFile.value.length} 条无效索引`
      })
      selectedDelIndex.value = []
      loadIndex()
      validate()
    })
}

</script>
