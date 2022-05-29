<template>
  <div class="q-ma-md">
    <span class="text-h6">命令行脚本列表</span>
    <q-btn class="float-right q-mr-sm" @click="reload" :loading="reloading">重新加载</q-btn>
  </div>

  <q-card style="min-width: 500px; width: 80vw; margin: auto;">
    <q-list>
      <div v-for="info in cliScriptInfo" :key="info.name">
        <q-item clickable @click="openCodeDisplay(info.code)">
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
    <q-card style="height: 90vh">
      <q-bar>
        <span>代码</span>
        <q-space></q-space>
        <q-btn icon="close" @click="showCode = false" flat color="primary" class="q-mx-none">
        </q-btn>
      </q-bar>
      <q-scroll-area style="height: 90%">
        <pre class="q-ma-sm">{{ displayedCode }}</pre>
      </q-scroll-area>
    </q-card>
  </q-dialog>

</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { CliScriptInfo } from "src/plugins/wahuBridge/methods";
import { cli_list, cli_reload } from "src/plugins/wahuBridge/methods";

const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()
onMounted(() => {
  emits('updateTitle', '命令行脚本')
})

const cliScriptInfo = ref<Array<CliScriptInfo>>([])

const showCode = ref<boolean>(false)
const displayedCode = ref<string>('')

const reloading = ref<boolean>(false)

onMounted(() => {
  cli_list().then(ls => {
    cliScriptInfo.value = ls
  })
})

function openCodeDisplay(code: string) {
  displayedCode.value = code
  showCode.value = true
}

function reload() {
  reloading.value = true
  cli_reload().then(() => { reloading.value = false })
}

</script>
