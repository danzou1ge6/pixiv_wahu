<template>
  <q-scroll-area ref="scrollArea" :style="`width: ${width}; height: ${height}; padding-left: 0px; padding-right: 0px;`">
    <div :style="`width: ${width}; height: ${height};`" class="q-mx-sm">
      <div>
        <div v-for="(item, i) in content" :key="i">
          <WahuCliItem v-bind="item"></WahuCliItem>
        </div>
      </div>
      <q-input v-model="cmdInp" @keyup.enter="enter" dense :prefix="inpPrefix" autofocus
        :dark="dark" class="cli-input" @keyup.up="previousHistory" @keyup.down="nextHistory"
        :loading="loading" :disabled="loading" ref="inputBox">
      </q-input>
      <div ref="inputBoxAnchor"></div>
    </div>
  </q-scroll-area>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';

import { wahu_exec } from 'src/plugins/wahuBridge/methods';
import WahuCliItem from './WahuCliItem.vue';

const props = defineProps<{
  dark: boolean,
  width: string,
  height: string
}>()


const content = ref<Array<{
  text?: string,
  src?: string
}>>([{ text: 'WahuCli\n输入 man 来获得帮助\n' }])
const cmdInp = ref<string>('')
const inpPrefix = ref<string>('$')
const loading = ref<boolean>(false)

const history = ref<Array<string>>([])
const historyPointer = ref<number>(0)

const scrollArea = ref<HTMLTemplateElement | null>(null)
const inputBox = ref<HTMLTemplateElement | null>(null)
const inputBoxAnchor = ref<HTMLTemplateElement | null>(null)

let generator = ref<AsyncGenerator<string, undefined, string | undefined>>()

function enter() {
  const cmd = cmdInp.value
  cmdInp.value = ''

  history.value.push(cmd)
  historyPointer.value = history.value.length

  if (generator.value === undefined) {
    if (cmd != '') {

      content.value.push({ text: '$ ' + cmd + '\n' })
      autoScroll()

      if (handleSpecialCmd(cmd)) {
        return
      }

      loading.value = true

      wahu_exec(cmd)
        .then(gen => {
          loading.value = false
          generator.value = gen
          listenGenerator()
        })
    }
  } else {
    listenGenerator(cmd)
    processRetVal(inpPrefix.value + ' ' + cmd + '\n')
  }


}

function autoScroll() {
  if(scrollArea.value !== null && inputBoxAnchor.value !== null) {
    setTimeout(() => {
      // @ts-ignore
      scrollArea.value.setScrollPosition('vertical', inputBoxAnchor.value.offsetTop, 300)
    }, 50)
  }
}


onMounted(() => {
  wahu_exec('wahu')
    .then(gen => {
      generator.value = gen
      listenGenerator()
    })
})


async function listenGenerator(initalSendVal?: string) {
  while (generator.value !== undefined) {
    const ret = await generator.value.next(initalSendVal)
    initalSendVal = undefined

    inpPrefix.value = '>'

    if (ret.done) {
      generator.value = undefined
      inpPrefix.value = '$'
      return
    }
    const inputMatch = ret.value.match(/\[:input=.+\]/)
    if (inputMatch !== null) {
      inpPrefix.value = inputMatch[0].slice(8, -1)
      return
    }
    processRetVal(ret.value)
  }
}

function processRetVal(ret: string | undefined) {
  if (ret !== undefined) {
    const imgMatch = ret.match(/\[:img=.+\]/)
    if (imgMatch !== null) {
      if(ret.match(/\[:img=.+\].+/) !== null) {
        content.value.push({
          src: imgMatch[0].slice(6, -1),
          text: ret.slice(imgMatch[0].length)
        })
      }else {
        content.value.push({
          src: imgMatch[0].slice(6, -1)
        })
      }
    } else {
      if(content.value[content.value.length - 1].src === undefined) {
        content.value[content.value.length - 1].text += ret
      }else{
        content.value.push({text: ret})
      }
    }
    autoScroll()
  }
}

function nextHistory() {
  if (historyPointer.value < history.value.length) {
    historyPointer.value += 1

    if (historyPointer.value == history.value.length) {
      cmdInp.value = ''
    } else {
      cmdInp.value = history.value[historyPointer.value]
    }
  }
}

function previousHistory() {
  if (historyPointer.value > 0) {
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

function handleSpecialCmd(cmd: string): boolean {
  if (cmd == 'clear') {
    content.value = []
  } else if (cmd == 'man') {
    content.value.push({ text: manText })
  } else if (cmd == 'history') {
    content.value.push({
      text: history.value.slice(undefined, history.value.length - 1).join('\n')
    })
  } else {
    return false
  }
  autoScroll()
  return true
}


</script>

<style scoped>
.cli-input {
  font-family: monospace;
}
</style>
