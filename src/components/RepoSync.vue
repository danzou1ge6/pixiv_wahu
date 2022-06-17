<template>
  <div class="col-12">
    <q-card>
      <q-card-section>

        <div class="row items-center">
          <div class="col-1">
            <div class="text-h5" style="display: inline-block">同步</div>
          </div>
          <div class="col-9">
            <q-select underlined :options="allDbNames" label="连接数据库" @update:model-value="updateLinkedDb"
              :model-value="selectedDbName" multiple></q-select>
          </div>
          <div class="col">
            <q-btn class="float-right" color="primary" @click="calcSync" label="计算差集" icon="data_object">
              <q-tooltip>
                新增 = 数据库 \ 储存库；删除 = 储存库 \ 数据库
              </q-tooltip>
            </q-btn>
          </div>
        </div>
      </q-card-section>

      <q-linear-progress :indeterminate="calcingSync"></q-linear-progress>
    </q-card>
  </div>

  <div class="col-md-7 col-sm-12 col-xs-12 col-lg-7">
    <q-card>

      <q-table :rows="syncAddTableRows" row-key="fid" selection="multiple" v-model:selected="selectedAdd"
        :rows-per-page-options="[10, 20, 50, 100, 200, 500, 0]" dense :columns="syncAddTableColDef"
        :visible-columns="addTableVisibleCols">

        <template v-slot:top>
          <div class="col-2 q-table__title">新增</div>
          <q-btn flat @click="submitAdd" color="primary" class="float-right q-ma-sm" v-show="selectedAdd.length != 0">
            确认新增
            <q-tooltip>
              加入选中的条目到储存库索引的缓存区
            </q-tooltip>
          </q-btn>
          <q-btn flat @click="submitDownload" color="primary" class="float-right q-ma-sm"
            v-show="selectedAdd.length != 0">
            加入下载
            <q-tooltip>
              下载选中的条目到储存库的目录中
            </q-tooltip>
          </q-btn>
        </template>
      </q-table>
    </q-card>
  </div>

  <div class="col-md-5 col-sm-12 col-xs-12 col-lg-5">
    <q-card>
      <q-table :rows="delList" row-key="fid" selection="multiple" v-model:selected="selectedDel"
        :rows-per-page-options="[10, 20, 50, 100, 200, 500, 0]" dense :columns="syncDelTableCofDef">
        <template v-slot:top>
          <div class="col-2 q-table__title">
            删除
            <q-tooltip>
              从储存库索引删除选中的条目
            </q-tooltip>
          </div>
          <q-btn @click="submitDel" color="warning" class="float-right q-ma-sm" v-if="selectedDel.length != 0">确认删除
          </q-btn>
        </template>
      </q-table>
    </q-card>
  </div>

</template>

<script setup lang="ts">
import { computed } from '@vue/reactivity';
import { pushNoti } from 'src/plugins/notifications';
import { onMounted, ref } from 'vue';
import * as wm from '../plugins/wahuBridge/methods'

const props = defineProps<{
  repoName: string
}>()
const emits = defineEmits<{
  (e: 'refreshCache'): void,
  (e: 'refreshIndex'): void,
}>()

const selectedDbName = ref<Array<string>>([])
const allDbNames = ref<Array<string>>()

function updateLinkedDb(dbs: Array<string>): void {
  selectedDbName.value = dbs
  wm.ir_set_linked_db(props.repoName, dbs)
}

onMounted(() => {
  wm.ir_linked_db(props.repoName)
    .then(ls => {
      selectedDbName.value = ls
      wm.ibd_list()
        .then(dls => {
          allDbNames.value = Array.from(new Set(dls.concat(selectedDbName.value)))
        })
    })
})

interface FileEntryWithDbURL extends wm.FileEntry {
  dbName: string,
  url: string
}

const delList = ref<Array<wm.FileEntry>>([])
const addList = ref<Array<wm.RepoSyncAddReport>>([])

const selectedAdd = ref<Array<FileEntryWithDbURL>>([])
const selectedDel = ref<Array<wm.FileEntry>>([])


const syncAddTableColDef = [
  { name: 'dbName', label: '来自数据库', field: 'dbName', },
  { name: 'fid', label: 'FID', field: 'fid', },
  { name: 'path', label: '文件', field: 'path' },
]
const addTableVisibleCols = ['dbName', 'fid', 'path']

const syncAddTableRows = computed(() => {
  let ret: Array<FileEntryWithDbURL> = []
  for (let { db_name, entries } of addList.value) {
    for (let entry of entries) {
      ret.push({
        dbName: db_name,
        fid: entry.fid,
        path: entry.path,
        url: entry.url
      })
    }
  }
  return ret
})

const syncDelTableCofDef = [syncAddTableColDef[1], syncAddTableColDef[2]]

const calcingSync = ref<boolean>(false)

function calcSync() {
  calcingSync.value = true
  wm.ir_calc_sync(props.repoName)
    .then((ret => {
      let [del, add] = ret
      selectedAdd.value = []
      selectedDel.value = []
      delList.value = del
      addList.value = add
      calcingSync.value = false
    }))
}

function submitAdd() {
  const entries = selectedAdd.value.map(item => {
    return {
      fid: item.fid,
      path: item.path
    }
  })
  wm.ir_add_cache(props.repoName, entries)
    .then(() => {
      pushNoti({
        level: 'success', msg: `添加了 ${entries.length} 项到 ${props.repoName} 的缓存`
      })
      emits('refreshCache')
    })
}

function submitDel() {
  const fids = selectedDel.value.map(
    item => item.fid
  )
  wm.ir_rm_index(props.repoName, fids)
    .then(() => {
      pushNoti({
        level: 'success', msg: `从 ${props.repoName} 的索引删除了 ${fids.length} 项`
      })
      selectedDel.value = []
      emits('refreshIndex')
    })
}

function submitDownload() {
  const entries = selectedAdd.value.map(item => {
    return {
      fid: item.fid,
      path: item.path,
      url: item.url
    }
  })
  wm.ir_download(props.repoName, entries)
    .then(() => {
      pushNoti({
        level: 'success',
        msg: `添加了 ${entries.length} 项下载到 ${props.repoName}`
      })
    })
}

</script>
