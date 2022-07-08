<template>
  <transition appear enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutLeft">

    <q-fab color="primary" icon="keyboard_arrow_down" direction="down" v-if="modelValue.length > 0"
      :label="`选中 ${modelValue.length} 项`" class="db-toolbar" square vertical-actions-align="left"
      style="backdrop-filter: blur(7px);"
      persistent v-model="open">

      <q-fab-action color="primary" square @click="cancelSelect" label="取消选择" external-label icon="cancel">
      </q-fab-action>
      <q-fab-action color="primary" label="复制到" external-label icon="copy_all" @click="updateDbList(); open = true" square>
        <q-menu>
          <q-list>
            <q-item v-for="dbName in dbNameList" :key="dbName" clickable v-close-popup @click="copyTo(dbName)">
              <q-item-section>
                {{ dbName }}
              </q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-fab-action>

      <q-fab-action color="primary" square @click="$emit('update:modelValue', all); open = true"
        label="全选" external-label icon="select_all">
      </q-fab-action>

      <q-fab-action color="primary" square @click="reverseSelect(); open = true"
        label="反选" external-label icon="tab_unselected">
      </q-fab-action>

      <q-fab-action color="primary" label="删除" external-label icon="delete" square
        @click="confirmDel = !confirmDel; open = true">
      </q-fab-action>

      <q-fab-action color="primary" label="收藏" external-label icon="bookmark_add"
        square @click="addPBookmark(); open = true" :loading="addPBmLoading">
      </q-fab-action>

      <q-fab-action color="primary" label="删除收藏" external-label icon="bookmark_remove"
        square @click="delPBookmark(); open = true" :loading="delPBmLoading">
      </q-fab-action>

    </q-fab>
  </transition>

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

const open = ref<boolean>(false)

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
    .catch(() => {
      addPBmLoading.value = false
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
    .catch(() => {
      delPBmLoading.value = false
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
