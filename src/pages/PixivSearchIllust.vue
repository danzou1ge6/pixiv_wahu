<template>

  <q-card class="q-ma-md">

    <div class="text-h5 q-ma-md" style="display: inline-block">Pixiv 插画</div>

    <div class="float-right q-ma-md">
      <q-btn icon="help" size="sm" flat @click="getHelpText(); showHelp = !showHelp">
        <q-tooltip>帮助</q-tooltip>
      </q-btn>
    </div>
    <q-dialog v-model="showHelp" full-width>
      <q-card>
        <pre class="q-ma-md">{{ helpText }}</pre>
        <q-btn flat class="float-right q-ma-md" color="primary" @click="showHelp = false">关闭</q-btn>
      </q-card>
    </q-dialog>

    <q-input class="q-ma-md" autofocus v-model="queryString" label="查询" :error="queryStringError"
      @keyup.enter="executeQuery" @input="queryStringError = false" hide-hint hint="回车发起查询">
    </q-input>

    <q-linear-progress :indeterminate="queryLoading"></q-linear-progress>
  </q-card>


  <IllustListPixiv :illusts="illusts" :scores="scores"></IllustListPixiv>

  <div class="row q-ma-lg" v-show="generator !== undefined">
    <div class="col-12">
      <q-btn @click="invokeGenerator" color="primary float-right" stretch :loading="loading">下一页</q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import IllustListPixiv from "src/components/IllustListPixiv.vue";
import { onMounted, onUnmounted, ref } from "vue";
import * as wm from '../plugins/wahuBridge/methods'
import { WahuStopIteration } from "src/plugins/wahuBridge/client";
import { pushNoti } from "src/plugins/notifications";

const props = defineProps<{
  initialQueryString?: string
}>()

const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

const showHelp = ref<boolean>(false)

const queryString = ref<string>('')
const queryStringError = ref<boolean>(false)
const queryLoading = ref<boolean>(false)

const loading = ref<boolean>(false)
const illusts = ref<Array<wm.IllustDetail>>([])
const scores = ref<Array<number>>([])

let generator = ref<AsyncGenerator<Array<[wm.IllustDetail, number]>>>()

function asignGenerator(gen: typeof generator.value) {
  if (generator.value !== undefined && generator.value.throw !== undefined) {
    generator.value.throw(new WahuStopIteration())
  }
  generator.value = gen
}

function invokeGenerator() {
  if (generator.value !== undefined) {

    loading.value = true
    generator.value.next().then(ret => {
      if (ret.done) {
        generator.value = undefined
        pushNoti({
          level: 'info',
          msg: '已加载所有插画'
        })
        return
      }

      illusts.value = illusts.value.concat(ret.value.map(item => item[0]))
      scores.value = scores.value.concat(ret.value.map(item => item[1]))
      loading.value = false
      pushNoti({
        level: 'success',
        msg: '获取了 ' + ret.value.length + ' 张插画'
      })
    })
  }
}

function asignAndInvokeGenerator(gen: typeof generator.value) {
  asignGenerator(gen)
  invokeGenerator()
}

onUnmounted(() => {
  if (generator.value !== undefined && generator.value.throw !== undefined) {
    generator.value.throw(new WahuStopIteration())
  }
})


function executeQuery() {
  queryStringError.value = false

  emits('updateProps', { initialQueryString: queryString.value })
  emits('updateTitle', '插画:' + queryString.value)

  queryLoading.value = true
  wm.p_query(queryString.value)
    .then(gen => {
      illusts.value = []
      scores.value = []
      asignAndInvokeGenerator(gen)
      queryLoading.value = false
    })
    .catch(e => {
      queryStringError.value = true
      queryLoading.value = false
      console.log(e)
    })

}

onMounted(() => {
  if (props.initialQueryString !== undefined) {
    queryString.value = props.initialQueryString
    executeQuery()
  }
  emits('updateTitle', '插画:' + queryString.value)
})

const helpText = ref<string>('')

function getHelpText() {
  wm.p_query_help().then(t => { helpText.value = t })
}


</script>

<style scoped>
pre {
  white-space: pre-wrap;
}
</style>
