<template>
  <q-scroll-area ref="scrollArea" :style="`padding-left: 0px; padding-right: 0px;`">
    <div style="width: 100%; height: 100%;" class="q-mx-sm">
      <div>
        <div v-for="(item, i) in content" :key="i">
          <WahuCliItem v-bind="item"></WahuCliItem>
        </div>
      </div>
      <q-input :model-value="cmdInp" @keyup.enter="enter" dense :prefix="inpPrefix" autofocus
        class="cli-input" @keyup.up="previousHistory" @keyup.down="nextHistory"
        :loading="loading" ref="inputBox" @update:model-value="handleInput">
      </q-input>
      <pre v-show="cmdInp != '' && generator === undefined" class="text-grey-5">{{ ' ' + completions.join(' ') }}</pre>
      <div v-for="(his, i) in displayedHistory[0]" :key="i" v-show="historyPointer != -1">
        <pre class="text-grey-5">{{ i == displayedHistory[1] ? '-> ' + his : '   ' + his }}</pre>
      </div>
      <div ref="inputBoxAnchor"></div>
    </div>
  </q-scroll-area>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';

import { wahu_exec, wahu_cli_complete } from 'src/plugins/wahuBridge/methods';
import WahuCliItem from './WahuCliItem.vue';


const displayedHistoryNum = 5

const content = ref<Array<{
  text?: string,
  src?: string
}>>([{ text: 'WahuCli\n输入 man 来获得帮助\n' }])
const cmdInp = ref<string>('')
const inpPrefix = ref<string>('$')
const loading = ref<boolean>(false)

const matchedHistory = ref<Array<string>>([])
const history = ref<Array<string>>([])
const historyPointer = ref<number>(0)
const completions = ref<Array<string>>([])

const scrollArea = ref<HTMLTemplateElement | null>(null)
const inputBox = ref<HTMLTemplateElement | null>(null)
const inputBoxAnchor = ref<HTMLTemplateElement | null>(null)

let generator = ref<AsyncGenerator<string, undefined, string | null>>()

function enter() {
  const cmd = cmdInp.value

  history.value.push(cmd)
  historyPointer.value = -1
  cmdInp.value = ''
  matchedHistory.value = Array.from(new Set(history.value))

  if (generator.value === undefined) {
    if (cmd != '') {

      print('\n\n$ ' + cmd)
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
    inpPrefix.value = '>'
    listenGenerator(cmd)
    print('\n' + inpPrefix.value + ' ' + cmd)
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
    const ret = await generator.value.next(
      initalSendVal === undefined ? null : initalSendVal
    )
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
    print(ret.value)
  }
}

function lastOf<T>(arr: Array<T>) : T{
  return arr[arr.length - 1]
}

function print(val: string | undefined) {
  if (val !== undefined) {
    const imgMatch = val.match(/\[:img=.+\]/)
    const rewriteMatch = val.match(/\[:rewrite\].+/)
    const eraseMatch = val.match(/\[:erase\]/)
    if (imgMatch !== null) {
      if(val.match(/\[:img=.+\].+/) !== null) {
        content.value.push({
          src: imgMatch[0].slice(6, -1),
          text: val.slice(imgMatch[0].length)
        })
      }else {
        content.value.push({
          src: imgMatch[0].slice(6, -1)
        })
      }
    } else if(rewriteMatch !== null) {
      const txt = val.slice(10)
      if(lastOf(content.value).text !== null){
        lastOf(content.value).text = txt
      }else{
        content.value.push({text: txt})
      }
    } else if(eraseMatch !== null) {
      content.value.splice(content.value.length - 1, 1)
    } else {
      if(val.startsWith('\n')) {
        content.value.push({text: val.slice(1)})
      }else{
        if(lastOf(content.value).text !== undefined) {
          lastOf(content.value).text += val
        }else{
          content.value.push({text: val})
        }
      }
    }
    autoScroll()
  }
}

function nextHistory() {
  if (historyPointer.value < matchedHistory.value.length) {
    historyPointer.value += 1

    if (historyPointer.value == matchedHistory.value.length) {
      historyPointer.value = -1
      cmdInp.value = ''
      matchedHistory.value = Array.from(new Set(history.value))
    } else {
      cmdInp.value = matchedHistory.value[historyPointer.value]
    }
    autoScroll()
  }
}

function previousHistory() {
  if (historyPointer.value > 0) {
    historyPointer.value -= 1
  }else if(historyPointer.value = -1) {
    historyPointer.value = matchedHistory.value.length - 1
  }
  cmdInp.value = matchedHistory.value[historyPointer.value]
  autoScroll()
}

function handleInput(val: string | number | null) {
  cmdInp.value = val as string
  matchedHistory.value = Array.from(
    new Set(history.value.filter(val => val.startsWith(cmdInp.value)))
  )
  if(historyPointer.value == -1) {
    wahu_cli_complete(cmdInp.value)
      .then(ret => {
        completions.value = ret
      })
    autoScroll()
  }else{
    historyPointer.value = -1
  }
}

const displayedHistory = computed(() => {
  const half = (displayedHistoryNum - 1) / 2
  if(historyPointer.value <= half) {
    return [matchedHistory.value.slice(0, displayedHistoryNum), historyPointer.value]
  }else if(historyPointer.value >= matchedHistory.value.length - half) {
    return [matchedHistory.value.slice(
      matchedHistory.value.length - displayedHistoryNum
    ), historyPointer.value - matchedHistory.value.length + displayedHistoryNum
    ]
  }else {
    return [matchedHistory.value.slice(
      historyPointer.value - half,
      historyPointer.value + half + 1
    ), half]
  }
})

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
`.trim()

function handleSpecialCmd(cmd: string): boolean {
  if (cmd == 'clear') {
    content.value = []
  } else if (cmd == 'man') {
    content.value.push({ text: manText })
  } else if (cmd == 'history') {
    content.value.push({
      text: matchedHistory.value.slice(undefined, matchedHistory.value.length - 1).join('\n')
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
pre {
  margin-top: 0px;
  margin-bottom: 0px;
}
</style>
