<template>
  <q-card class="q-ma-md">
    <div class="text-h5 q-ma-md" style="display: inline-block">{{ dbName }}</div>

    <DatabaseActions :db-name="dbName" @update-subscrip="executeQuery"></DatabaseActions>

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
            <span>模糊查询: title|tag|username|caption[=&lt;fuzzy_cutoff&gt;] &lt;keyword&gt;</span><br>
            <span>按 IID 查询: iid &lt;iid&gt;,...</span><br>
            <span>按 UID 查询画师: uid &lt;uid&gt;</span><br>
            <span>列出被删除的插画: restricted</span>
          </div>
          <div class="text-h5">说明</div>
          <div class="q-body-2 text-grey-8">
            <span>「|」: 表示「或」</span><br>
            <span>「[]」: 表示可选</span><br>
            <span>「,...」: 表示可以用「英文逗号」连接多个值</span><br>
          </div>
          <div class="text-h5">举例</div>
          <div class="q-body-2 text-grey-8">
            <span>「title=90 shizuku」: 按 90% 的模糊匹配值在标题中查询 「shizuku」</span><br>
            <span>「iid 0123,2345」: 查询插画 IID 0123 和 2345</span><br>
          </div>
        </div>
        <q-btn flat class="float-right q-ma-md" color="primary" @click="showHelp = false">关闭</q-btn>
      </q-card>
    </q-dialog>

    <q-input class="q-ma-md" underlined autofocus v-model="queryString" label="查询" :error="queryStringError"
      @keyup.enter="executeQuery" @input="queryStringError = false" hide-hint hint="回车发起查询">
    </q-input>

    <q-linear-progress :indeterminate="queryLoading"></q-linear-progress>
  </q-card>

  <q-pagination class="q-ma-md" v-model="page" v-if="queryResultIids.length > numPerPage"
    :max="queryResultIids.length / numPerPage + 1">
  </q-pagination>

  <CheckboxGroup v-model="selected">
    <template v-slot:default="{ toggle, getState }">

      <div class="row q-col-gutter-sm q-ma-md">
        <transition-group appear enter-active-class="animated zoomIn" leave-active-class="animated zoomOut">
          <div class="col-md-3 col-sm-6 col-xs-12 col-lg-2" v-for="(iid, i) in displayedIids" :key="iid">
            <IllustCardLocal :iid="iid" :db-name="props.dbName" @update:select="toggle(iid, $event)"
              :selected="getState(iid)" :score="queryResultScores === undefined ? undefined : queryResultScores[i]"
              height="300px">
            </IllustCardLocal>
          </div>
        </transition-group>
      </div>

    </template>
  </CheckboxGroup>

  <DatabaseToolbar v-model="selected" :db-name="dbName" :all=queryResultIids @delete="handleDelete">
  </DatabaseToolbar>

  <GotoTop></GotoTop>

</template>


<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import IllustCardLocal from '../components/IllustCardLocal.vue'
import * as wm from '../plugins/wahuBridge/methods'
import { pushNoti } from '../plugins/notifications';
import { numPerPage } from '../constants';
import DatabaseToolbar from 'src/components/DatabaseToolbar.vue';
import CheckboxGroup from 'src/components/CheckboxGroup.vue';
import GotoTop from 'src/components/GotoTop.vue';
import DatabaseActions from 'src/components/DatabaseActions.vue';


const props = defineProps<{
  dbName: string,
  initialQueryString?: string
}>()
const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

const showHelp = ref<boolean>(false)

const queryString = ref<string>('')
const queryStringError = ref<boolean>(false)

const queryResultIids = ref<Array<number>>([])
const queryResultScores = ref<Array<number> | undefined>()

const queryLoading = ref<boolean>(false)

const page = ref<number>(1)

const selected = ref<Array<number>>([])


function cutStringWith(str: string, subStr: string): [string, string | null] {
  let at = str.indexOf(subStr)
  if (at == -1) {
    return [str, null]
  }
  return [str.slice(0, at), str.slice(at + 1)]
}

function executeQuery() {
  queryStringError.value = false

  let [cmd, keyword] = cutStringWith(queryString.value, ' ')

  if (keyword == null) {
    if (cmd == 'all') {
      queryLoading.value = true
      wm.ibd_list_bm(props.dbName)
        .then(bms => {
          pushNoti({ level: 'success', msg: `数据库 ${props.dbName} 中共有 ${bms.length} 幅插画` })
          queryResultIids.value = []
          queryResultScores.value = undefined
          for (let bm of bms) { queryResultIids.value.push(bm.iid) }
          queryLoading.value = false

          emits('updateTitle', props.dbName + ':all')
          emits('updateProps', { ...props, initialQueryString: 'all' })
        })
      return
    }else if (cmd == 'restricted') {
      queryLoading.value = true
      wm.ibd_filter_restricted(props.dbName)
        .then(iids => {
          pushNoti({
            level: 'info',
            msg: `数据库 ${props.dbName} 中有 ${iids.length} 张被删除的插画`
          })
          queryResultIids.value = iids
          queryResultScores.value = undefined
          queryLoading.value = false

          emits('updateProps', {...props, initialQueryString: 'restricted'})
          emits('updateTitle', props.dbName + ':restricted')
        })
      return

    } else {
      queryStringError.value = true
      return
    }
  }

  let [target, cutoff] = cutStringWith(cmd, '=')

  if ((cutoff !== null) && (isNaN(Number(cutoff)))) {
    queryStringError.value = true
    return
  }
  let numCutoff
  if (cutoff === null) { numCutoff = null }
  else { numCutoff = Number(cutoff) }

  switch (target) {
    case ('tag'):
    case ('username'):
    case ('caption'):
    case ('title'):
      queryLoading.value = true
      wm.ibd_fuzzy_query(props.dbName, target, keyword, numCutoff)
        .then(ret => {
          pushNoti({
            level: 'success',
            msg: `根据 ${keyword} 在数据库 ${props.dbName} 中模糊查询 ${target} 到 ${ret.length} 幅插画`
          })
          queryResultIids.value = []
          queryResultScores.value = []
          for (let [iid, score] of ret) {
            queryResultIids.value.push(iid)
            queryResultScores.value?.push(score)
          }
          queryLoading.value = false

          emits('updateTitle', props.dbName + ':' + keyword)
          emits('updateProps', { ...props, initialQueryString: queryString.value })
        })
      return

    case ('uid'):
      if (isNaN(Number(keyword))) {
        queryStringError.value = true
        return
      }
      let uid = Number(keyword)
      queryLoading.value = true
      wm.ibd_query_uid(props.dbName, uid)
        .then(ret => {
          pushNoti({
            level: 'success',
            msg: `数据库 ${props.dbName} 中 ${uid} 的插画作品共有 ${ret.length} 幅`
          })
          queryResultScores.value = undefined
          queryResultIids.value = ret
          queryLoading.value = false

          emits('updateTitle', props.dbName + ':user ' + uid)
          emits('updateProps', { ...props, initialQueryString: queryString.value })
        })
      return

    case ('iid'):
      let iids: Array<number> = []
      for (let s of keyword.split(',')) {
        if (isNaN(Number(s))) {
          queryStringError.value = true
          return
        }
        iids.push(Number(s))
      }
      queryResultScores.value = undefined
      queryResultIids.value = iids

      emits('updateTitle', props.dbName + ':iid ')
      emits('updateProps', { ...props, initialQueryString: queryString.value })
      return
    default:
      queryStringError.value = true
      return
  }

}

onMounted(() => {
  emits('updateTitle', props.dbName)

  if (props.initialQueryString !== undefined) {
    queryString.value = props.initialQueryString
    executeQuery()
  }
})


const displayedIids = computed(() => {
  return queryResultIids.value.slice(
    numPerPage * (page.value - 1), numPerPage * page.value)
})


function handleDelete() {
  for (let iid of selected.value) {
    const idx = queryResultIids.value.indexOf(iid)

    if (idx != -1) {
      queryResultIids.value.splice(idx, 1)
      queryResultScores.value?.splice(idx, 1)
    }

    const selectedIdx = selected.value.indexOf(iid)

    if (selectedIdx !== -1) {
      selected.value.splice(selectedIdx, 1)
    }
  }
}

</script>
