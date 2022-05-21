<template>
  <transition appear enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutLeft">
    <q-banner class="bg-primary db-toolbar" v-if="modelValue.length > 0">

      <div class="text-h6 text-white">选中 {{ modelValue.length }} 项</div>

      <template v-slot:action>
        <q-btn color="white" flat @click="cancelSelect">
          取消选择
        </q-btn>

        <q-btn color="white" label="添加到" flat @click="updateDbList">
          <q-menu>
            <q-list>
              <q-item v-for="dbName in dbNameList" :key="dbName" clickable v-close-popup @click="addTo(dbName)">
                <q-item-section>
                  {{ dbName }}
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>

        <q-btn color="white" flat @click="$emit('update:modelValue', details.map(item => item.iid))">
          全选
        </q-btn>
        <q-btn color="white" flat @click="reverseSelect">
          反选
        </q-btn>
        <q-btn color="white" flat @click="addBookmark">
          收藏
        </q-btn>
        <q-btn color="white" flat @click="delBookmark">
          取消收藏
        </q-btn>
        <q-btn color="white" flat @click="download">
          下载
        </q-btn>

      </template>

    </q-banner>
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

function addBookmark() {
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
      pushNoti({
        level: 'success',
        msg: `收藏了 ${toAdd.length} 张插画`
      })
    })
}

function delBookmark() {
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
  width: 300px;
  background: $primary;
}
</style>
