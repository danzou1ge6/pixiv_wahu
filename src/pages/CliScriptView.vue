<template>
  <div class="q-ma-md">
    <span class="text-h6">命令行脚本列表</span>
    <q-btn class="float-right q-mr-sm" @click="reload" :loading="reloading" color="primary" icon="refresh" label="重新加载"></q-btn>
  </div>

  <q-card style="min-width: 500px; width: 80vw; margin: auto;">
    <q-list>
      <div v-for="info in cliScriptInfo" :key="info.name">
        <q-item clickable @click="openCodeDisplay(info)">
          <q-item-section>
            <q-item-label>{{ info.name }}</q-item-label>
            <q-item-label caption>文件：{{ info.path }}</q-item-label>
            <q-item-label caption>描述：{{ info.descrip }}</q-item-label>
          </q-item-section>
        </q-item>
      </div>
    </q-list>
  </q-card>

  <q-dialog v-model="showCode" full-width full-height transition-show="slide-up" transition-hide="slide-down">
    <q-card style="height: 90vh" v-if="displayed !== undefined">
      <q-bar>
        <span>{{ displayed.name }}</span>
        <q-space></q-space>
        <q-btn icon="edit" @click="openEditor(displayed)" flat color="primary" class="q-mx-none">
          <q-tooltip>在默认编辑器中打开</q-tooltip>
        </q-btn>
        <q-btn icon="close" @click="showCode = false" flat color="primary" class="q-mx-none">
        </q-btn>
      </q-bar>
      <q-scroll-area style="height: 90%">
        <pre class="q-ma-sm">{{ displayed.code }}</pre>
      </q-scroll-area>
    </q-card>
  </q-dialog>

</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { CliScriptInfo } from "src/plugins/wahuBridge/methods";
import { cli_list, cli_reload, cli_open_editor } from "src/plugins/wahuBridge/methods";

const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()
onMounted(() => {
  emits('updateTitle', '命令行脚本')
})

const cliScriptInfo = ref<Array<CliScriptInfo>>([])

const showCode = ref<boolean>(false)
const displayed = ref<CliScriptInfo>()

const reloading = ref<boolean>(false)

function refresh() {
  cli_list().then(ls => {
    cliScriptInfo.value = ls
  })
}

onMounted(refresh)

function openCodeDisplay(csi: CliScriptInfo) {
  displayed.value = csi
  showCode.value = true
}

function reload() {
  reloading.value = true
  cli_reload().then(() => {
    reloading.value = false
    refresh()
  })
}

function openEditor(csi: CliScriptInfo | undefined) {
  if (csi !== undefined) {
    showCode.value = false
    cli_open_editor(csi.name)
  }
}

</script>
