<template>

  <q-card class="q-ma-md">

    <div class="text-h5 q-ma-md" style="display: inline-block">Pixiv 插画</div>

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
            <span>推荐插画： recom</span><br>
            <span>新作： new</span><br>
            <span>关注画师的新作： follow</span><br>
            <span>插画收藏： bookmark</span><br>
            <span>排行： ranking day|week|month|day-male|day-female|week-original|week-rookie</span><br>
            <span>搜索： search ptag|etag|tc|kw[:ddate|adate|dp] &lt;keyword&gt;</span><br>
            <span>画师的作品： uid &lt;uid&gt;</span>
          </div>
          <div class="text-h5">说明</div>
          <div class="q-body-2 text-grey-8">
            <span>「|」: 表示「或」</span><br>
            <span>「[]」: 表示可选</span><br>
            <span>「ptag」: 部分标签(partial tag)</span><br>
            <span>「etag」: 全部标签(exact tag)</span><br>
            <span>「tc」: 标题和描述(title caption)</span><br>
            <span>「ddate」: 日期逆序(descend date)</span><br>
            <span>「adate」: 日期正序(ascend date)</span><br>
            <span>「dp」: 热门度逆序(descend popularity) 似乎需要「 充 V I P 」才能用</span><br>
          </div>
          <div class="text-h5">举例</div>
          <div class="q-body-2 text-grey-8">
            <span>「search ptag:ddate white hair」: 逆序日期，部分标签匹配「 white hair 」</span><br>
            <span>「ranking day」: 今日作品排行</span><br>
          </div>
        </div>
        <q-btn flat class="float-right q-ma-md" color="primary" @click="showHelp = false">关闭</q-btn>
      </q-card>
    </q-dialog>

    <q-input class="q-ma-md" autofocus v-model="queryString" label="查询" :error="queryStringError"
      @keyup.enter="executeQuery" @input="queryStringError = false" hide-hint hint="回车发起查询">
    </q-input>

    <q-linear-progress :indeterminate="queryLoading"></q-linear-progress>
  </q-card>


  <IllustListPixiv :illusts="illusts"></IllustListPixiv>

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

let generator = ref<AsyncGenerator<Array<wm.IllustDetail>>>()

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

      illusts.value = illusts.value.concat(ret.value)
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
  illusts.value = []
  invokeGenerator()
}

onUnmounted(() => {
  if (generator.value !== undefined && generator.value.throw !== undefined) {
    generator.value.throw(new WahuStopIteration())
  }
})


function cutStringWith(str: string, subStr: string): [string, string | null] {
  let at = str.indexOf(subStr)
  if (at == -1) {
    return [str, null]
  }
  return [str.slice(0, at), str.slice(at + 1)]
}

interface StrMapping {
  [index: string]: string
}

const targetMap: StrMapping = {
  'ptag': "partial_match_for_tags",
  'etag': "exact_match_for_tags",
  'tc': "title_and_caption",
  'kw': "keyword"
}

const sortMap: StrMapping = {
  'adate': 'date_asc',
  'ddate': 'date_desc',
  'dp': 'popular_desc'
}

function searchIllust(qs: string) {

  let [cmd, keyword] = cutStringWith(qs, ' ')

  if (keyword === null) {
    queryStringError.value = true; return
  }

  let [target, sort] = cutStringWith(cmd, ':')

  let pTarget = targetMap[target]
  if (pTarget === undefined) {
    queryStringError.value = true; return
  }
  let pSort = null
  if (sort !== null) {
    let pSort = sortMap[sort]
    if (pSort === undefined) {
      queryStringError.value = true; return
    }
  }

  queryLoading.value = true
  wm.p_ilst_search(keyword, pTarget as wm.PixivSearchTarget,
    pSort as wm.PixivSort | null)
    .then(gen => {
      asignAndInvokeGenerator(gen)
      queryLoading.value = false
      illusts.value = []
      emits('updateTitle', 'Pixiv:' + keyword as string)
      emits('updateProps', { initialQueryString: 'search ' + qs })
    })

}

const recomModes = [
  "day",
  "week",
  "month",
  "day_male",
  "day_female",
  "week_original",
  "week_rookie"
]

function executeQuery() {
  queryStringError.value = false

  let [cmd, other] = cutStringWith(queryString.value, ' ')

  if (other === null) {
    if (cmd == 'recom') {
      queryLoading.value = true
      wm.p_ilst_recom()
        .then(gen => {
          asignAndInvokeGenerator(gen)
          queryLoading.value = false
          illusts.value = []
          emits('updateProps', { initialQueryString: 'recom' })
          emits('updateTitle', '推荐插画')
        })
      return

    } else if (cmd == 'new') {
      queryLoading.value = true
      wm.p_ilst_new()
        .then(gen => {
          asignAndInvokeGenerator(gen)
          queryLoading.value = false
          illusts.value = []
          emits('updateProps', { initialQueryString: 'new' })
          emits('updateTitle', '新作')
        })
      return

    } else if (cmd == 'follow') {
      queryLoading.value = true
      wm.p_ilst_folow()
        .then(gen => {
          asignAndInvokeGenerator(gen)
          queryLoading.value = false
          illusts.value = []
          emits('updateProps', { initialQueryString: 'follow' })
          emits('updateTitle', '关注新作')
        })
      return

    } else if (cmd == 'bookmark') {
      wm.p_account_session()
        .then(ac => {
          if (ac === null) {
            wm.p_attempt_login().then(() => { executeQuery() })
            return
          }
          queryString.value += ' ' + ac.user_id
          executeQuery()
        })
      return

    } else {
      queryStringError.value = true; return
    }
  }

  if (cmd == 'search') {
    searchIllust(other); return

  } else if (cmd == 'ranking') {
    let rankMode = other.replace('-', '_')
    if (recomModes.indexOf(rankMode) == -1) {
      queryStringError.value = true; return
    }
    queryLoading.value = true
    wm.p_ilst_ranking(rankMode as wm.PixivRecomMode)
      .then(gen => {
        asignAndInvokeGenerator(gen)
        queryLoading.value = false
        emits('updateProps', { initialQueryString: queryString.value })
        emits('updateTitle', '作品排行')
      })
    return

  } else if (cmd == 'bookmark') {
    let uid = Number(other)
    if (isNaN(uid)) {
      queryStringError.value = true; return
    }
    queryLoading.value = true
    wm.p_user_bmilsts(uid)
      .then(gen => {
        asignAndInvokeGenerator(gen)
        queryLoading.value = false
        emits('updateProps', { initialQueryString: queryString.value })
        emits('updateTitle', `${uid} 的收藏`)
      })
    return

  } else if (cmd == 'iid') {
    let iids: Array<number> = []
    for (let s of other.split(',')) {
      if (isNaN(Number(s))) {
        queryStringError.value = true
        return
      }
      iids.push(Number(s))
    }
    illusts.value = []
    for (let iid of iids) {
      wm.p_ilst_detail(iid)
        .then(dtl => {
          illusts.value.push(dtl)
        })
    }
    emits('updateProps', { initialQueryString: queryString.value })
    emits('updateTitle', `iids`)
    return
  } else if (cmd == 'uid') {
    if (isNaN(Number(other))) {
      queryStringError.value = true
      return
    }
    wm.p_user_ilsts(Number(other))
      .then(gen => {
        asignAndInvokeGenerator(gen)
        queryLoading.value = false
        emits('updateProps', { initialQueryString: queryString.value })
        emits('updateTitle', `${other} 的作品`)
        return
      })
  } else {
    queryStringError.value = true; return
  }
}

onMounted(() => {
  if (props.initialQueryString !== undefined) {
    queryString.value = props.initialQueryString
    executeQuery()
  }
  emits('updateTitle', 'Pixiv 插画')
})

</script>
