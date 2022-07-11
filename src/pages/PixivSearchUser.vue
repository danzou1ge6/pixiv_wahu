<template>

  <q-card class="q-ma-md">

    <div class="text-h5 q-ma-md" style="display: inline-block">Pixiv 用户</div>

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

    <q-input class="q-ma-md" underlined autofocus v-model="queryString" label="查询" @keyup.enter="executeQuery" hide-hint
      hint="回车发起查询" :error="queryError" @input="queryError = false">
    </q-input>

    <q-linear-progress :indeterminate="queryLoading"></q-linear-progress>
  </q-card>

  <PixivUserPreviewList :user-previews="userPreviews"></PixivUserPreviewList>

  <div class="row q-ma-lg" v-show="generator !== undefined">
    <div class="col-12">
      <q-btn @click="invokeGenerator" color="primary float-right" stretch :loading="loading">下一页</q-btn>
    </div>
  </div>

</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import * as wm from '../plugins/wahuBridge/methods'
import { WahuStopIteration } from 'src/plugins/wahuBridge/client';
import { pushNoti } from 'src/plugins/notifications';
import PixivUserPreviewList from 'src/components/PixivUserPreviewList.vue';
import { replaceCurrentWindow } from 'src/plugins/windowManager';


const props = defineProps<{
  initialQueryString?: string
}>()


const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

const showHelp = ref<boolean>(false)

const queryString = ref<string>('')
const queryLoading = ref<boolean>(false)
const queryError = ref<boolean>(false)

const userPreviews = ref<Array<wm.PixivUserPreview>>([])

const generator = ref<AsyncIterator<Array<wm.PixivUserPreview>, undefined, null>>()

const loading = ref<boolean>(false)

onMounted(() => {
  emits('updateTitle', '用户:' + queryString.value)
})

function cutStringWith(str: string, subStr: string): [string, string | null] {
  let at = str.indexOf(subStr)
  if (at == -1) {
    return [str, null]
  }
  return [str.slice(0, at), str.slice(at + 1)]
}


function executeQuery() {
  queryError.value = false

  emits('updateTitle', '用户:' + queryString.value)
  emits('updateProps', { initialQueryString: queryString.value })

  queryLoading.value = true
  wm.p_query_user(queryString.value)
    .then(ret => {
      if(typeof(ret) == 'number') {
        replaceCurrentWindow({
          component: 'PixivUserDetail',
          props: { uid: ret },
          title: 'User:' + ret
        })
      }else {
        queryLoading.value = false
        asignAndInvokeGenerator(ret)
      }
    })
    .catch(e => {
      queryError.value = true
      queryLoading.value = false
      console.log(e)
    })

}


onMounted(() => {
  if (props.initialQueryString !== undefined) {
    queryString.value = props.initialQueryString
    executeQuery()
  }
})

onUnmounted(() => {
  if (generator.value !== undefined) {
    if (generator.value.throw !== undefined) {
      generator.value.throw(new WahuStopIteration())
    }
  }
})

function asignGenerator(gen: typeof generator.value) {

  if (generator.value !== undefined) {
    if (generator.value.throw !== undefined) {
      generator.value.throw(new WahuStopIteration())
    }
    userPreviews.value = []
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
          msg: '已加载所有用户预览'
        })
        return
      }

      userPreviews.value = userPreviews.value.concat(ret.value)
      loading.value = false
      pushNoti({
        level: 'success',
        msg: '获取了 ' + ret.value.length + ' 个用户预览'
      })
    })
  }
}

function asignAndInvokeGenerator(gen: typeof generator.value) {
  asignGenerator(gen)
  invokeGenerator()
}

const helpText = ref<string>('')
function getHelpText() {
  wm.p_query_user_help().then(s => { helpText.value = s })
}


</script>

<style scoped>
pre {
  white-space: pre-wrap;
}
</style>
