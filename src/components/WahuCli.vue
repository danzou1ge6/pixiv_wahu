<template>
  <div class="q-pa-sm">
    <div>
      <pre>{{ text }}</pre>
    </div>
    <q-input v-model="cmdInp" @keyup.enter="enter" dense :prefix="generator === undefined ? '$' : '>'" autofocus
      :dark="dark" class="q-mr-sm q-mb-sm">
    </q-input>
    <div ref="inputBoxAnchor" style="q-my-md">
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';

import { wahu_exec } from 'src/plugins/wahuBridge/methods';

const props = defineProps<{
  dark: boolean
}>()

const text = ref<string>('WahuCli\n输入 --help 来获得命令列表')
const cmdInp = ref<string>('')

const inputBoxAnchor = ref<HTMLTemplateElement | null>(null)

let generator = ref<AsyncGenerator<string, undefined, string | undefined>>()

function enter() {
  if (generator.value === undefined) {
    if(cmdInp.value != '') {
      wahu_exec(cmdInp.value)
        .then(gen => {
          text.value += '$ ' + cmdInp.value + '\n'
          cmdInp.value = ''
          generator.value = gen
          listenGenerator()
        })
    }
  } else {
    listenGenerator(cmdInp.value)
    text.value += cmdInp.value + '\n'
    cmdInp.value = ''
  }


}

watch(text, () => {
  if(inputBoxAnchor.value !== null) {
    inputBoxAnchor.value.scrollIntoView()
  }
})


async function listenGenerator(initalSendVal?: string) {
  while (generator.value !== undefined) {
    const ret = await generator.value.next(initalSendVal)
    initalSendVal = undefined

    if (ret.done) {
      generator.value = undefined
      text.value += '\n'
      return
    }
    if (ret.value == '[:input]') {
      return
    }
    processRetVal(ret.value)
  }
}

function processRetVal(ret: string | undefined) {
  if (ret !== undefined) {
    text.value += ret
  }
}
</script>

<style scoped>
pre {
  white-space: break-spaces;
}
</style>
