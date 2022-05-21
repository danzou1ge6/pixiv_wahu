<template>
  <div class="float-right">

    <q-btn flat @click="showConfig = !showConfig" class="q-ma-sm" color="primary">配置</q-btn>
    <DatabaseConfig v-model="showConfig" :db-name="dbName"></DatabaseConfig>

    <q-btn flat @click="showUpdateSubs = !showUpdateSubs" class="q-ma-sm" color="primary" :loading="updateSubsLoading">
      更新订阅
    </q-btn>

    <q-btn flat @click="exportJson" class="q-ma-sm" color="primary">
      导出 JSON
      <q-menu auto-close>
        <q-btn :href="objURLForExport" target="_blank" :loading="objURLForExport === undefined"
          @click="objURLForExport = undefined">下载</q-btn>
      </q-menu>
    </q-btn>

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
import { ref } from 'vue'
import * as wm from '../plugins/wahuBridge/methods'
import { pushNoti } from '../plugins/notifications';
import DatabaseConfig from 'src/components/DatabaseConfig.vue';

const props = defineProps<{
  dbName: string,
}>()
const emits = defineEmits<{
  (e: 'updateSubscrip'): void
}>()

const showConfig = ref<boolean>(false)
const showUpdateSubs = ref<boolean>(false)
const updateSubsPageCount = ref<number>(-1)

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

</script>
