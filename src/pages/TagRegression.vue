<template>
  <q-card class="q-ma-sm">
    <div class="text-h5 q-ma-md">选择样本</div>
    <div class="row q-col-gutter-sm q-ma-sm">
      <div class="col-xs-12 col-sm-12 col-md-5 q-mb-sm">
        <q-select underlined :options="allDbNames" label="正样本数据库"
          v-model="selectedPosDb" multiple></q-select>
      </div>
      <div class="col-xs-12 col-sm-12 col-md-5 q-mb-sm">
        <q-select underlined :options="allDbNames" label="负样本数据库"
          v-model="selectedNegDb" multiple></q-select>
      </div>
      <div class="col q-mt-sm">
        <q-btn @click="countTags" class="float-right q-mr-sm" color="primary" label="确认"
          icon="check"></q-btn>
      </div>
    </div>
    <div class="absolute-top-right">
      <q-btn icon="help" @click="showHelp = true" flat size="sm"></q-btn>
    </div>
  </q-card>

  <q-dialog full-width v-model="showHelp">
    <q-card>
      <q-card-section>
        <div class="text-body-1">
          <ul>
            <li>第一步，选择正负样本. 可以选择多个数据库中的插画作为正负样本. 重复插画不会被处理，将影响结果.</li>
            <li>第二步，选择要统计的标签. 通过「最小次数」滑动条可以控制选中标签在样本中出现的最少次数. 也可以在表中手动选择</li>
            <li>
              第三步，设定各个超参数求解模型.
              <ul>
                <li>批处理批大小：每次迭代使用的样本数</li>
                <li>学习率：梯度下降法的学习率</li>
                <li>迭代次数：执行梯度下降的次数</li>
                <li>测试集占比：测试集用于评估模型的准确率</li>
              </ul>
            </li>
            <li>第四步，评估模型. 求解完成后会出现「损失曲线」「测试集准确率」的曲线</li>
            <li>
              第五步，保存模型. 求解完成后会出现模型参数表格. 在表格下方可以给定一个「模型名」保存到配置文件中的 `tag_model_dir` 目录中.
              保存后可以在「搜索 Pixiv 插画」页面使用「-m ;&lt模型名;&gt」选项调用模型
            </li>
          </ul>
        </div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat color="primary" @click="showHelp = false">关闭</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-card class="q-ma-sm">
    <q-table :rows="countedTags" row-key="name" selection="multiple" v-model:selected="selectedTags"
      :rows-per-page-options="[10, 20, 50, 100, 200, 500, 0]" dense :columns="countedTagsTableDef"
      :visible-columns="addTableVisibleCols">

        <template v-slot:top>
          <div class="col-12 q-table__title text-h5">选择要统计的标签</div>
          <div class="col-12">
            <q-badge>最小次数 = {{ minCountForRegression }}</q-badge>
            <q-slider :model-value="minCountForRegression" @update:model-value="updateMinCountForRegression" label
              :min="Math.min(...countedTags.map(item => item.count))" :max="Math.max(...countedTags.map(item => item.count))"
            ></q-slider>
          </div>
        </template>
    </q-table>
  </q-card>

  <q-card class="q-ma-sm">
    <div class="text-h5 q-ma-md">求解模型</div>
    <div class="row q-col-gutter-sm q-ma-sm">
      <div class="col-12">
        <q-badge>样本总数 ( {{ numSamples }} ) 中 批处理批大小 = {{ batchSize }}</q-badge>
        <q-slider v-model="batchSize" label :min="1" :max="numSamples"></q-slider>
      </div>
      <div class="col-12">
        <q-badge>学习率 = {{ Math.pow(10, logLearningRate).toFixed(4) }}</q-badge>
        <q-slider v-model="logLearningRate" label :min="-4" :max="0" :step="0.1"
          :label-value="Math.pow(10, logLearningRate).toFixed(4)"></q-slider>
      </div>
      <div class="col-12">
        <q-badge>迭代次数 = {{ Math.pow(10, logEpoch).toFixed(0) }}</q-badge>
        <q-slider v-model="logEpoch" label :min="0" :max="4" :step="0.1"
          :label-value="Math.pow(10, logEpoch).toFixed(0)"></q-slider>
      </div>
      <div class="col-12">
        <q-badge>测试集占比 = {{ testSetRatio }}</q-badge>
        <q-slider v-model="testSetRatio" label :min="0.01" :max="1" :step="0.01"></q-slider>
      </div>
      <div class="col-6" v-if="selectedTags.length != 0">
        <div class="text-h6 q-ma-md">{{ (trainProgress * 100).toFixed(0) + '%' }}</div>
      </div>
      <div class="col-6" v-if="selectedTags.length != 0">
        <q-btn label="逻辑回归" icon="analytics" class="float-right q-ma-sm" color="primary"
          :loading="regressionLoading" @click="runRegression"></q-btn>
      </div>
    </div>
    <div class="q-ma-md" v-if="lossList.length != 0">
      <Line :chart-data="chartData" :chart-options="chartOptions" :height="80" :width="150"/>
    </div>
  </q-card>

  <q-card v-if="model != undefined" class="q-ma-sm">
    <div class="text-h5 q-ma-md">模型参数</div>

    <q-card-section>
      <div class="text-h6 q-ma-md">标签权重</div>
      <q-scroll-area style="height: 60vh">
        <q-markup-table class="q-ma-sm">
          <thead><tr>
            <th class="text-left">名</th><th class="text-left">译</th><th class="text-left">权重</th>
          </tr></thead>
          <tbody>
            <tr v-for="tag in model.weighed_tags">
              <td>{{ tag.name }}</td><td>{{ tag.translated }}</td><td>{{ tag.weight }}</td>
            </tr>
          </tbody>
        </q-markup-table>
      </q-scroll-area>
    </q-card-section>

    <q-card-section>
      <div class="text-h6 q-ma-md">偏置</div>
      <div class="text-body-1 q-ma-md q-ml-lg">{{ model.bias }}</div>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat color="primary" label="保存" icon="save">
        <q-menu transition-show="slide-left" transition-hide="slide-right" v-model="showSaveInput">
          <q-input label="模型名" underlined class="q-ma-md" @keyup.enter="saveModel"
            v-model="modelName" @input="saveModelError = false" autofocus></q-input>
        </q-menu>
      </q-btn>

    </q-card-actions>
  </q-card>

</template>

<script setup lang="ts">
import { computed } from '@vue/reactivity';
import { ref, onMounted } from 'vue';
import { Line } from 'vue-chartjs'
import * as wm from '../plugins/wahuBridge/methods'

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
} from 'chart.js'
import { pushNoti } from 'src/plugins/notifications';

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale
)


const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

onMounted(() => {
  emits('updateTitle', '标签逻辑回归')
})

const allDbNames = ref<Array<string>>([])
const selectedPosDb = ref<Array<string>>([])
const selectedNegDb = ref<Array<string>>([])

onMounted(() => {
  wm.ibd_list()
    .then(dls => {
      allDbNames.value = dls
    })
})

const numSamples = ref<number>(0)

const countedTagsTableDef = [
  { name: 'name', label: '名', field: 'name', },
  { name: 'translated', label: '译', field: 'translated', },
  { name: 'count', label: '次', field: 'count' },
]
const addTableVisibleCols = countedTagsTableDef.map(item => item.name)

const countedTags = ref<Array<wm.CountedIllustTag>>([])
const selectedTags = ref<Array<wm.CountedIllustTag>>([])

function countTags() {
  wm.ibdtag_count(selectedNegDb.value.concat(selectedPosDb.value))
    .then(ct => {
      countedTags.value = ct
    })

  const allSelectedDbs = selectedNegDb.value.concat(selectedPosDb.value)
  Promise.all(allSelectedDbs.map(dbn => wm.ibd_ilst_count(dbn)))
    .then(result => numSamples.value = result.reduce((p, c) => p + c))
}

const minCountForRegression = ref<number>(0)

function updateMinCountForRegression(val: number | null) {

  if(val !== null) {
    minCountForRegression.value = val

    selectedTags.value = countedTags.value.filter(
      item => item.count >= minCountForRegression.value
    )
  }
}

const regressionLoading = ref<boolean>(false)
const batchSize = ref<number>(10)
const logLearningRate = ref<number>(-2)
const logEpoch = ref<number>(2)
const testSetRatio = ref<number>(0.05)

const model = ref<wm.TagRegressionModel>()
const lossList = ref<Array<number>>([])
const epochList = ref<Array<number>>([])
const accuracyList = ref<Array<number>>([])
const trainProgress = ref<number>(0)

const chartData = computed(() => ({
    labels: epochList.value,
    datasets: [
    {
      label: '损失',
      data: lossList.value,
      yAxisID: 'loss-axis',
      borderColor: '#FFA500'
    }, {
      label: '测试集准确率',
      data: accuracyList.value,
      yAxisID: 'accuracy-axis',
      borderColor: '#32CD32'
    }
  ]
}))
const chartOptions = {
  responsive: true,
  yAxes: [{
    id: 'loss-axis', type: 'linear', position: 'left'
  },{
    id: 'accuracy-axis', type: 'linear', position: 'right'
  }]
}

async function listenReport(
  trainGen: AsyncGenerator<[[number, number], [Array<number>, Array<number>, wm.TagRegressionModel] | null], undefined, null>
) {

  while(true) {
    const ret = await trainGen.next()

    if(ret.value == undefined) { throw(new TypeError('ret.value is undefined')) }

    const [progress, result] = ret.value

    if(result !== null) {
      const [loss_list, accu_list, m] = result

      lossList.value = loss_list
      accuracyList.value = accu_list
      model.value = m

      break
    }

    const [current, all] = progress
    trainProgress.value = (current + 1) / all
    epochList.value.push(current)

  }


}

function runRegression() {
  regressionLoading.value = true

  lossList.value = []
  epochList.value = []
  accuracyList.value = []

  wm.ibdtag_logistic_regression(
    selectedPosDb.value,
    selectedNegDb.value,
    selectedTags.value,
    Math.pow(10, logLearningRate.value),
    batchSize.value,
    Math.floor(Math.pow(10, logEpoch.value)),
    testSetRatio.value
  )
    .then(train_gen => {
      listenReport(train_gen)
        .then(() => {regressionLoading.value = false})
    })
}

const modelName = ref<string>('')
const saveModelError = ref<boolean>(false)
const showSaveInput = ref<boolean>(false)

function saveModel() {
  wm.ibdtag_write_model(model.value as wm.TagRegressionModel, modelName.value)
    .then(() => {
      showSaveInput.value = false
      wm.get_config('tag_model_dir')
        .then(dir => {
          pushNoti({level: 'success', msg: `已保存为 ${dir}/${modelName.value}.toml`})
        })
    })
    .catch(err => saveModelError.value = true)
}

const showHelp = ref(false)

</script>
