<template>
    <q-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)">
      <q-card style="min-width: 400px; width: 50vw">
        <q-card-section>
          <div class="text-h6">配置 {{ dbName }}</div>
        </q-card-section>
  
        <q-card-section v-if="config !== undefined">
          <q-form @submit="onSubmit">
            <q-input v-model="config.name" label="名称"></q-input>
            <q-input type="textarea" v-model="config.description" label="描述"></q-input>
            <NumberArrayInput v-model="config.subscribed_bookmark_uid" label="订阅用户收藏 UID">
            </NumberArrayInput>
            <NumberArrayInput v-model="config.subscribed_user_uid" label="订阅画师 UID"></NumberArrayInput>
            <q-select v-model="config.subscribe_overwrite" :options="['append', 'intelligent', 'replace']"
              label="覆写模式" hide-hint
              hint="intelligent: 当某一页所有插画均在数据库中，停止更新；append: 追加指定页数的插画；replace: 删除原有插画"></q-select>
            
            <q-input type="number" v-model="config.subscribe_pages" label="更新订阅的页数"
                v-if="config.subscribe_overwrite != 'intelligent'"
                hint="-1 表示不限页数" hide-hint></q-input>
  
            <q-btn flat label="提交" type="submit" color="primary" :loading="submitLoading" class="float-right q-ma-md">
            </q-btn>
            <q-btn flat label="重置" color="primary" class="float-right q-ma-md" @click="reset"></q-btn>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </template>
  
  <script setup lang="ts">import { ref } from '@vue/reactivity';
  import { pushNoti } from 'src/plugins/notifications';
  import { onMounted } from 'vue';
  import * as wm from '../plugins/wahuBridge/methods'
  import NumberArrayInput from './NumberArrayInput.vue';
  
  const props = defineProps<{
    dbName: string
    modelValue: boolean
  }>()
  const emits = defineEmits<{
    (e: 'update:modelValue', val: boolean): void
  }>()
  
  const config = ref<wm.IllustBookmarkingConfig>()
  
  const submitLoading = ref<boolean>(false)
  
  function reset() {
    wm.ibd_get_config(props.dbName)
      .then(cfg => { config.value = cfg })
  }
  
  onMounted(() => {
    reset()
  })
  
  function onSubmit() {
    if (config.value !== undefined) {
      submitLoading.value = true
      wm.ibd_set_config(props.dbName, config.value)
        .then(() => {
          submitLoading.value = false
          emits('update:modelValue', false)
          pushNoti({
            level: 'success',
            msg: '配置更新成功'
          })
        })
    }
  }
  </script>