<template>
  <div class="q-pa-sm">
    <div>
      <pre>{{ text }}</pre>
    </div>
    <q-input v-model="cmdInp" @keyup.enter="enter" dense :prefix="generator === undefined ? '$' : '>'" autofocus
      :dark="dark" class="q-mr-sm q-mb-sm" @keyup.up="previousHistory" @keyup.down="nextHistory">
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

const text = ref<string>('WahuCli\n输入 man 来获得帮助\n')
const cmdInp = ref<string>('')

const history = ref<Array<string>>([])
const historyPointer = ref<number>(0)

const inputBoxAnchor = ref<HTMLTemplateElement | null>(null)

let generator = ref<AsyncGenerator<string, undefined, string | undefined>>()

function enter() {
  if (generator.value === undefined) {
    if(cmdInp.value != '') {

      text.value += '\n$ ' + cmdInp.value + '\n'
      history.value.push(cmdInp.value)
      historyPointer.value = history.value.length

      if(handleSpecialCmd(cmdInp.value)) {
        cmdInp.value = ''
        return
      }

      wahu_exec(cmdInp.value)
        .then(gen => {
          cmdInp.value = ''
          generator.value = gen
          listenGenerator()
        })
    }
  } else {
    listenGenerator(cmdInp.value)
    text.value += '> ' + cmdInp.value + '\n'
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

function nextHistory() {
  if(historyPointer.value < history.value.length) {
    historyPointer.value += 1

    if(historyPointer.value == history.value.length) {
      cmdInp.value = ''
    }else{
      cmdInp.value = history.value[historyPointer.value]
    }
  }
}

function previousHistory() {
  if(historyPointer.value > 0) {
    historyPointer.value -= 1

    cmdInp.value = history.value[historyPointer.value]
  }
}

const manText = `
输入 --help 来获得命令列表
指示符：
  当指示符为 $ ，表明命令行终端处于待机状态，可以执行命令
  当指示符为 > ，表明命令行终端正在执行命令，此时输入的字符会被存入缓冲区，下次命令行脚本请求输入的时候从缓冲区读取
历史：
  可以使用上下箭头键回溯命令行执行历史；历史存储在前端，页面刷新后会丢失
清屏：
  执行 clear 清屏
每个命令行终端之间相互独立，并发执行，也就是说可以打开多个 Home 页面分别执行命令
在任何一个页面，可以使用快捷加 Ctrl+\` 呼出快捷命令行终端
`.trim()

function handleSpecialCmd(cmd: string) : boolean {
  if(cmd == 'clear') {
    text.value = ''
  }else if(cmd == 'man') {
    text.value += manText
  }else{
    return false
  }
  return true
}

</script>

<style scoped>
pre {
  white-space: break-spaces;
}
</style>
