<template>
    <div class="col-12">
      <q-card>
        <q-table :rows="cache" row-key="fid" :rows-per-page-options="[10, 20, 50, 100, 200, 500, 0]" dense :columns="cols">
          <template v-slot:top>
            <div class="col-2 q-table__title">索引缓存</div>
            <q-btn flat @click="loadCache" color="primary" class="float-right q-ma-sm" label="刷新" icon="refresh">
            </q-btn>
            <q-btn flat @click="empty" color="warning" class="float-right q-ma-sm" v-show="cache.length != 0"
              label="清空" icon="delete">
            </q-btn>
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

const cols = [
  { name: 'fid', label: 'FID', field: 'fid', },
  { name: 'path', label: '文件', field: 'path' }
]

const cache = ref<Array<wm.FileEntry>>([])

watch(() => props.refresh, () => {
  loadCache()
})

function loadCache() {
  wm.ir_get_cache(props.repoName)
    .then(c => { cache.value = c })
}

onMounted(loadCache)

function empty() {
  wm.ir_empty_cache(props.repoName)
    .then(() => {
      pushNoti({
        level: 'success',
        msg: '清空了 ' + props.repoName + ' 的索引缓存'
      })
      loadCache()
    })
}
</script>
