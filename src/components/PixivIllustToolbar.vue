<template>
  <transition appear enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutLeft">
    <q-fab color="primary" icon="keyboard_arrow_down" direction="down" v-if="modelValue.length > 0"
      :label="`选中 ${modelValue.length} 项`" class="db-toolbar" square vertical-actions-align="left"
      persistent v-model="open">

      <q-fab-action color="primary" square @click="cancelSelect">
        取消选择
      </q-fab-action>

      <q-fab-action color="primary" label="添加到" square @click="updateDbList(); open = true">
        <q-menu>
          <q-list>
            <q-item v-for="dbName in dbNameList" :key="dbName" clickable v-close-popup @click="addTo(dbName)">
              <q-item-section>
                {{ dbName }}
              </q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-fab-action>

      <q-fab-action color="primary" square @click="$emit('update:modelValue', details.map(item => item.iid)); open = true">
        全选
      </q-fab-action>
      <q-fab-action color="primary" square @click="reverseSelect(); open = true">
        反选
      </q-fab-action>
      <q-fab-action color="primary" square @click="addBookmark(); open = true">
        收藏
      </q-fab-action>
      <q-fab-action color="primary" square @click="delBookmark(); open = true" :loading="addBmLoading">
        取消收藏
      </q-fab-action>
      <q-fab-action color="primary" square @click="download(); open = true" :loading="delBmLoading">
        下载
      </q-fab-action>


    </q-fab>
  </transition>
</template>


<script setup lang="ts">
import { ref, watch } from 'vue';
import * as wm from '../plugins/wahuBridge/methods'
import { pushNoti } from 'src/plugins/notifications';

const props = defineProps<{
  modelValue: Array<number>,
  details: Array<wm.IllustDetail>
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', val: Array<number>): void,
}>()

const dbNameList = ref<Array<string>>([])

const open = ref<boolean>(false)

function updateDbList() {
  wm.ibd_list()
    .then(ls => {
      dbNameList.value = ls
    })
}

interface Iid2Ilst {
  [index: number]: wm.IllustDetail
}

let iid2ilst: Iid2Ilst = {}

watch(() => props.details, () => {

  iid2ilst = {}
  for (let dtl of props.details) {
    iid2ilst[dtl.iid] = dtl
  }
})

function addTo(targetDbName: string) {
  let promiseList = []
  for (let iid of props.modelValue) {
    const pc = iid2ilst[iid].page_count
    if (pc !== undefined) {
      let pages = []
      for (let i = 0; i < pc; i++) {
        pages.push(i)
      }
      promiseList.push(wm.ibd_set_bm(targetDbName, iid, pages))
    }
  }
  Promise.all(promiseList).then(() => {
    pushNoti({
      level: 'success',
      msg: '添加了 ' + promiseList.length + ' 条收藏到 ' + targetDbName
    })
  })
}


function cancelSelect() {
  emits('update:modelValue', [])
}

function reverseSelect() {
  let newValue: Array<number> = []
  for (let iid of props.details.map(item => item.iid)) {
    if (props.modelValue.indexOf(iid) == -1) {
      newValue.push(iid)
    }
  }
  emits('update:modelValue', newValue)
}

function download() {
  wm.wahu_download(props.modelValue)
    .then(() => {
      pushNoti({
        level: 'info',
        msg: '添加了 ' + props.modelValue.length + ' 条下载到临时下载目录'
      })
    })
}

const addBmLoading = ref<boolean>(false)
const delBmLoading = ref<boolean>(false)

function addBookmark() {
  addBmLoading.value = true
  let toAdd = []
  for (let iid of props.modelValue) {
    if (iid2ilst[iid] !== undefined) {

      if (iid2ilst[iid].is_bookmarked == false) {
        toAdd.push(iid)
      } else {
        pushNoti({
          level: 'warning',
          msg: `${iid} - ${iid2ilst[iid].title} 已被收藏`
        })
      }
    }
  }
  wm.p_ilstbm_add(toAdd)
    .then(() => {
      addBmLoading.value = false
      pushNoti({
        level: 'success',
        msg: `收藏了 ${toAdd.length} 张插画`
      })
    })
}

function delBookmark() {
  delBmLoading.value = true
  let toDel = []
  for (let iid of props.modelValue) {
    if (iid2ilst[iid] !== undefined) {

      if (iid2ilst[iid].is_bookmarked == true) {
        toDel.push(iid)
      } else {
        pushNoti({
          level: 'warning',
          msg: `${iid} - ${iid2ilst[iid].title} 未被收藏`
        })
      }
    }
  }
  wm.p_ilstbm_rm(toDel)
    .then(() => {
      delBmLoading.value = false
      pushNoti({
        level: 'success',
        msg: `取消收藏了 ${toDel.length} 张插画`
      })
    })
}

</script>

<style scoped lang="scss">
.db-toolbar {
  position: fixed;
  left: 10px;
  top: 60px;
}
</style>
