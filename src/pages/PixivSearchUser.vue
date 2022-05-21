<template>

  <q-card class="q-ma-md">

    <div class="text-h5 q-ma-md" style="display: inline-block">Pixiv 用户</div>

    <div class="float-right q-ma-md">
      <q-btn icon="help" size="sm" flat @click="showHelp = !showHelp">
        <q-tooltip>帮助</q-tooltip>
      </q-btn>
    </div>
    <q-dialog v-model="showHelp">
      <q-card>
        <div class="q-ma-md">
          <div class="text-h5">命令列表</div>
          <div class="q-body-2 text-grey-8">
            <span>按名称搜索: name &lt;name&gt;</span><br>
            <span>跳转到 UID 为 &lt;uid&gt; 的用户的详情页面: uid &lt;uid&gt;</span><br>
            <span>关注了 &lt;uid&gt; 的用户: follower &lt;uid&gt;</span><br>
            <span>&lt;uid&gt; 关注的用户: following &lt;uid&gt;</span><br>
            <span>&lt;uid&gt; 的相关用户: related &lt;uid&gt;</span><br>
            <span>上述的 follower following related 命令，若缺省 &lt;uid&gt; 则使用自己的</span><br>
          </div>
        </div>
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

const generator = ref<AsyncIterator<Array<wm.PixivUserPreview>>>()

const loading = ref<boolean>(false)

onMounted(() => {
  emits('updateTitle', 'Pixiv 用户')
})

function cutStringWith(str: string, subStr: string): [string, string | null] {
  let at = str.indexOf(subStr)
  if (at == -1) {
    return [str, null]
  }
  return [str.slice(0, at), str.slice(at + 1)]
}


function executeQuery() {

  let [cmd, keyword] = cutStringWith(queryString.value, ' ')

  if (keyword !== null) {

    if (cmd == 'name') {
      queryLoading.value = true
      wm.p_user_search(keyword)
        .then(gen => {
          queryLoading.value = false
          asignAndInvokeGenerator(gen)
          emits('updateTitle', `Name:${keyword}`)
          emits('updateProps', { initialQueryString: queryString.value })
        })
      return
    }
    else if (cmd == 'uid') {

      if (isNaN(Number(keyword))) {
        queryError.value = true
        return
      }
      queryLoading.value = true
      replaceCurrentWindow({
        component: 'PixivUserDetail',
        props: { uid: Number(keyword) },
        title: 'User:' + keyword
      })
      return

    } else if (cmd == 'follower') {
      if (isNaN(Number(keyword))) {
        queryError.value = true
        return
      }
      queryLoading.value = true
      wm.p_user_follower(Number(keyword))
        .then(gen => {
          queryLoading.value = false
          asignAndInvokeGenerator(gen)
          emits('updateTitle', `Follower:${keyword}`)
          emits('updateProps', { initialQueryString: queryString.value })
        })
      return

    } else if (cmd == 'following') {
      if (isNaN(Number(keyword))) {
        queryError.value = true
        return
      }
      queryLoading.value = true
      wm.p_user_following(Number(keyword))
        .then(gen => {
          queryLoading.value = false
          asignAndInvokeGenerator(gen)
          emits('updateTitle', `Following:${keyword}`)
          emits('updateProps', { initialQueryString: queryString.value })
        })
      return

    } else if (cmd == 'related') {
      if (isNaN(Number(keyword))) {
        queryError.value = true
        return
      }
      queryLoading.value = true
      wm.p_user_related(Number(keyword))
        .then(gen => {
          queryLoading.value = false
          asignAndInvokeGenerator(gen)
          emits('updateTitle', `Related:${keyword}`)
          emits('updateProps', { initialQueryString: queryString.value })
        })
      return

    } else {
      queryError.value = true
      return
    }
  } else {
    if (cmd == 'following' || cmd == 'follower' || cmd == 'related') {
      appendMyUidAndQuery()
    }
  }

}

function appendMyUidAndQuery() {

  wm.p_account_session()
    .then(ac => {
      if (ac === null) {
        wm.p_attempt_login().then(() => { executeQuery() })
        return
      }
      queryString.value += ' ' + ac.user_id
      executeQuery()
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


</script>
