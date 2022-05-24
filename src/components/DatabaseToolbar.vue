<template>
  <transition appear enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutLeft">
    <q-banner class="bg-primary db-toolbar" v-if="modelValue.length > 0">

      <div class="text-h6 text-white">选中 {{ modelValue.length }} 项</div>

      <template v-slot:action>
        <q-btn color="white" flat @click="cancelSelect">
          取消选择
        </q-btn>
        <q-btn color="white" label="复制到" flat @click="updateDbList">
          <q-menu>
            <q-list>
              <q-item v-for="dbName in dbNameList" :key="dbName" clickable v-close-popup @click="copyTo(dbName)">
                <q-item-section>
                  {{ dbName }}
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>

        <q-btn color="white" flat @click="$emit('update:modelValue', all)">
          全选
        </q-btn>

        <q-btn color="white" flat @click="reverseSelect">
          反选
        </q-btn>

        <q-btn color="white" label="删除" flat @click="confirmDel = !confirmDel">
        </q-btn>
        <q-dialog v-model="confirmDel">
          <q-card>
            <q-card-section>
              <div class="text-h5">确认删除？所有详情和收藏信息都将被删除</div>
            </q-card-section>
            <q-card-section>
              <div class="text-body-1">iid: </div>
            </q-card-section>
            <q-card-section>
              <div class="text-body-1">{{ modelValue }}</div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat color="primary" @click="deleteSelected" v-close-popup>确认</q-btn>
              <q-btn flat color="primary" v-close-popup>取消</q-btn>
            </q-card-actions>
          </q-card>
        </q-dialog>

        <q-btn color="white" label="收藏" flat @click="addPBookmark" :loading="addPBmLoading">
        </q-btn>

        <q-btn color="white" label="删除收藏" flat @click="delPBookmark" :loading="delPBmLoading">
        </q-btn>

      </template>

    </q-banner>
  </transition>
</template>


<script setup lang="ts">
import { onMounted, ref } from 'vue';
import * as wm from '../plugins/wahuBridge/methods'
import { pushNoti } from 'src/plugins/notifications';

const props = defineProps<{
  modelValue: Array<number>,
  all: Array<number>,
  dbName: string
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', val: Array<number>): void,
  (e: 'delete'): void
}>()

const dbNameList = ref<Array<string>>([])

const confirmDel = ref<boolean>(false)

function updateDbList() {
  wm.ibd_list()
    .then(ls => {
      const idxOfThis = ls.indexOf(props.dbName)
      ls.splice(idxOfThis, 1)
      dbNameList.value = ls
    })
}

function copyTo(targetDbName: string) {
  wm.ibd_copy(props.dbName, targetDbName, props.modelValue)
    .then(() => {
      pushNoti({
        level: 'success',
        msg: `从 ${props.dbName} 复制了 ${props.modelValue.length} 项到 ${targetDbName}`
      })
    })
}

function deleteSelected() {
  for (let iid of props.modelValue) {
    wm.ibd_set_bm(props.dbName, iid, [])
      .then(() => {
        pushNoti({
          level: 'info',
          msg: '删除 ' + props.dbName + '/' + iid
        })
        emits('delete')
      })
  }
}

function cancelSelect() {
  emits('update:modelValue', [])
}

function reverseSelect() {
  let newValue: Array<number> = []
  for (let iid of props.all) {
    if (props.modelValue.indexOf(iid) == -1) {
      newValue.push(iid)
    }
  }
  emits('update:modelValue', newValue)
}

const addPBmLoading = ref<boolean>(false)
const delPBmLoading = ref<boolean>(false)

function addPBookmark() {
  addPBmLoading.value = true
  wm.p_ilstbm_add(props.modelValue)
    .then(() => {
      addPBmLoading.value = false
      pushNoti({
        level: 'success',
        msg: `添加了 ${props.modelValue.length} 条收藏`
      })
    })
}

function delPBookmark() {
  delPBmLoading.value = true
  wm.p_ilstbm_rm(props.modelValue)
    .then(() => {
      delPBmLoading.value = false
      pushNoti({
        level: 'success',
        msg: `删除了 ${props.modelValue.length} 条收藏`
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
