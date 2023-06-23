<template>
  <q-card class="q-ma-md">
    <div class="text-h5 q-ma-md" style="display: inline-block">{{ dbName }}</div>

    <DatabaseActions :db-name="dbName" @update-subscrip="executeQuery"></DatabaseActions>

    <div class="absolute-bottom-right">
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

  <q-pagination class="q-ma-md" v-model="page" v-if="queryResult.length > numPerPage"
    :max="queryResult.length / numPerPage + 1">
  </q-pagination>

  <CheckboxGroup v-model="selected">
    <template v-slot:default="{ toggle, getState }">

      <div class="row q-col-gutter-sm q-ma-md">
        <transition-group appear enter-active-class="animated zoomIn" leave-active-class="animated zoomOut">
          <div class="col-md-3 col-sm-6 col-xs-12 col-lg-2" v-for="[iid, score] in displayed" :key="iid">
            <IllustCardLocal :iid="iid" :db-name="props.dbName" @update:select="toggle(iid, $event)"
              :selected="getState(iid)" :score="score === -1 ? undefined : score"
              height="300px">
            </IllustCardLocal>
          </div>
        </transition-group>
      </div>

    </template>
  </CheckboxGroup>

  <DatabaseToolbar v-model="selected" :db-name="dbName" :all="queryResult.map(v => v[0])" @delete="handleDelete">
  </DatabaseToolbar>

  <GotoTop></GotoTop>

</template>


<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import IllustCardLocal from '../components/IllustCardLocal.vue'
import * as wm from '../plugins/wahuBridge/methods'
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

const queryResult = ref<Array<[number, number]>>([])

const queryLoading = ref<boolean>(false)

const page = ref<number>(1)

const selected = ref<Array<number>>([])


function executeQuery() {
  queryStringError.value = false

  emits('updateTitle', props.dbName + ':' + queryString.value)
  emits('updateProps', { ...props, initialQueryString: queryString.value })

  queryLoading.value = true
  wm.ibd_query(props.dbName, queryString.value)
    .then(ret => {
      queryResult.value = ret
      queryLoading.value = false
    })
    .catch(e => {
      queryStringError.value = true
      queryLoading.value = false
      console.log(e)
    })

}

onMounted(() => {
  emits('updateTitle', props.dbName)

  if (props.initialQueryString !== undefined) {
    queryString.value = props.initialQueryString
    executeQuery()
  }
})


const displayed = computed(() => {
  return queryResult.value.slice(
    numPerPage * (page.value - 1), numPerPage * page.value)
})


function handleDelete() {
  queryResult.value = queryResult.value.filter(v => !selected.value.includes(v[0]))
  selected.value = []
}

const helpText = ref<string>('')

function getHelpText() {
  wm.ibd_query_help().then(s => helpText.value = s)
}

</script>

<style scoped>
pre {
  white-space: pre-wrap;
}
</style>
